# manager.py
import asyncio
import logging
from datetime import timedelta
from typing import Dict, Optional

import zeroconf
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from homeassistant.components import zeroconf as ha_zeroconf

from .const import DOMAIN, ZEROCONF_TYPE
from .device import SyncleoDevice
from .protocol import (
    CMD_HANDSHAKE, FRAME_ACK, FRAME_CMD, FRAME_NAK,
    make_x25519_keys, aes_cbc_encrypt, aes_cbc_decrypt,
    build_frame, parse_frame, decrypt_frame_payload, 
    build_encrypted_ack_frame, HandshakeResponseMessage
)
from .client import SyncleoUdpClient

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

class SyncleoManager(zeroconf.ServiceListener):
    """Менеджер устройств, официально реализующий интерфейс ServiceListener."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.discovered_devices: Dict[str, SyncleoDevice] = {}
        self.configured_devices: Dict[str, SyncleoDevice] = {}
        self._unsub_interval = None
        self._browser = None
        self._entry_id_to_mac: Dict[str, str] = {}  # Маппинг entry_id -> mac

    async def async_start(self, initial_info: Optional[ZeroconfServiceInfo] = None) -> None:
        """Запуск менеджера."""
        # 1. Резервный слушатель шины HA
        self.hass.bus.async_listen(
            "zeroconf_service_updated", self._async_zeroconf_service_updated
        )
        
        if initial_info:
            self._process_service_info(initial_info)

        # 2. ЗАПУСКАЕМ BROWSER В ФОНЕ! Это решает проблему зависания на Windows
        self.hass.async_create_task(self._setup_zeroconf_browser())

        # 3. Таймер проверок доступности (не блокирует старт!)
        self._unsub_interval = async_track_time_interval(
            self.hass,
            self._async_availability_check,
            timedelta(seconds=2)
        )

    async def _setup_zeroconf_browser(self) -> None:
        """Фоновая задача: ждет полной готовности Zeroconf и только потом запускается."""
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                # Ждем увеличивающуюся задержку
                delay = 1 + attempt * 0.5
                _LOGGER.debug("Попытка %d запуска Zeroconf через %.1f сек...", attempt + 1, delay)
                await asyncio.sleep(delay)
                
                aiozc = await ha_zeroconf.async_get_async_instance(self.hass)
                self._browser = zeroconf.ServiceBrowser(
                    aiozc.zeroconf,
                    ZEROCONF_TYPE,
                    listener=self
                )
                _LOGGER.info("Zeroconf браузер успешно запущен (попытка %d)", attempt + 1)
                return
                
            except Exception as e:
                _LOGGER.warning("Попытка %d запуска Zeroconf браузера не удалась: %s", attempt + 1, e)
                if attempt == max_attempts - 1:
                    _LOGGER.error("Не удалось запустить Zeroconf браузер после %d попыток", max_attempts)
                    raise

    async def async_stop(self) -> None:
        """Остановка менеджера."""
        if self._browser:
            self._browser.cancel()
            self._browser = None
            
        if self._unsub_interval:
            self._unsub_interval()
            self._unsub_interval = None

    # ==========================================
    # Реализация интерфейса zeroconf.ServiceListener
    # ==========================================

    def add_service(self, zc: zeroconf.Zeroconf, type_: str, name: str) -> None:
        self._update_service_info(zc, type_, name)

    def update_service(self, zc: zeroconf.Zeroconf, type_: str, name: str) -> None:
        self._update_service_info(zc, type_, name)

    def remove_service(self, zc: zeroconf.Zeroconf, type_: str, name: str) -> None:
        pass

    def _update_service_info(self, zc: zeroconf.Zeroconf, type_: str, name: str) -> None:
        try:
            info = zc.get_service_info(type_, name)
            if info:
                self.hass.loop.call_soon_threadsafe(
                    self._process_service_info, info
                )
        except Exception:
            pass

    # ==========================================
    # Обработка данных
    # ==========================================

    @callback
    def _async_zeroconf_service_updated(self, event: dict) -> None:
        service_info = event.get("service_info")
        if not service_info or service_info.type != ZEROCONF_TYPE:
            return
        self._process_service_info(service_info)

    @staticmethod
    def _get_prop(props: dict, key: str) -> str:
        val = props.get(key) or props.get(key.encode()) or b''
        return val.decode('utf-8') if isinstance(val, bytes) else str(val)

    @callback
    def _process_service_info(self, service_info) -> None:
        props = service_info.properties
        mac = self._get_prop(props, 'macaddr')
        if not mac:
            return

        ip = None
        if hasattr(service_info, 'ip_address') and service_info.ip_address:
            ip = str(service_info.ip_address)
        elif hasattr(service_info, 'addresses') and service_info.addresses:
            for addr in service_info.addresses:
                if len(addr) == 4:
                    ip = ".".join(str(b) for b in addr)
                    break
        
        if not ip:
            return

        public_key = self._get_prop(props, 'public')
        
        device_data = {
            "mac": mac,
            "name": service_info.name.replace(f'.{ZEROCONF_TYPE}', ''),
            "ip": ip,
            "port": service_info.port,
            "public_key": public_key,
            "vendor": self._get_prop(props, 'vendor'),
            "basetype": self._get_prop(props, 'basetype'),
            "devtype": self._get_prop(props, 'devtype'),
            "firmware": self._get_prop(props, 'firmware'),
            "protocol": self._get_prop(props, 'protocol'),
        }

        self.discovered_devices[mac] = SyncleoDevice(**device_data)

        if mac in self.configured_devices:
            configured_dev = self.configured_devices[mac]
            if configured_dev.port != device_data["port"] or configured_dev.public_key != public_key:
                _LOGGER.warning("Устройство %s сменило порт/ключ! %s:%s", mac, ip, device_data["port"])
                configured_dev.port = device_data["port"]
                configured_dev.public_key = public_key
                configured_dev.ip = device_data["ip"]
                
                # Будим координатор, чтобы он переподключился по новому адресу
                self._trigger_coordinator_reconnect(mac)

    def _trigger_coordinator_reconnect(self, mac: str) -> None:
        """Находит координатор по MAC и вызывает переподключение."""
        # Ищем coordinator в hass.data
        domain_data = self.hass.data.get(DOMAIN, {})
        for entry_id, coordinator in domain_data.items():
            if entry_id in ["manager", "pending_zeroconf"]:
                continue
            if hasattr(coordinator, 'device') and coordinator.device.mac == mac:
                if hasattr(coordinator, 'trigger_reconnect'):
                    _LOGGER.info("Вызываем trigger_reconnect для координатора %s", mac)
                    self.hass.async_create_task(coordinator.trigger_reconnect())
                return
        
        # Если не нашли через entry_id, ищем в configured_devices
        if mac in self.configured_devices:
            device = self.configured_devices[mac]
            if hasattr(device, 'coordinator') and device.coordinator:
                if hasattr(device.coordinator, 'trigger_reconnect'):
                    _LOGGER.info("Вызываем trigger_reconnect для координатора %s (через device)", mac)
                    self.hass.async_create_task(device.coordinator.trigger_reconnect())

    def add_configured_device(self, mac: str, token: str, vendor: str, devtype: str, firmware: str) -> None:
        
        _LOGGER.debug("discovered_devices: %s, configured_devices: %s", self.discovered_devices, self.configured_devices)
        if mac in self.discovered_devices:
            device = self.discovered_devices.pop(mac)
            _LOGGER.debug("ADD DEVICE %s",device)
            device.token = token
            device.available = True
            device._fail_count = 0
            self.configured_devices[mac] = device
            return
            
        if mac not in self.configured_devices:
            _LOGGER.debug("MAC not in configured_devices %s", mac)
            self.configured_devices[mac] = SyncleoDevice(
                mac=mac, name=mac, ip="0.0.0.0", port=0, public_key="",
                vendor=vendor, basetype="", devtype=devtype, firmware=firmware, protocol="", token=token
            )

    def remove_configured_device(self, mac: str) -> None:
        if mac in self.configured_devices:
            del self.configured_devices[mac]

    # ==========================================
    # Проверка доступности
    # ==========================================

    async def _async_availability_check(self, now) -> None:
        for mac, device in list(self.configured_devices.items()):
            is_online = await self._async_check_device_udp(device)
            
            if is_online:
                if not device.available:
                    _LOGGER.info("Устройство %s снова в сети", mac)
                device.available = True
                device._fail_count = 0
            else:
                device._fail_count += 1
                if device._fail_count >= 3:
                    if device.available:
                        _LOGGER.warning("Устройство %s помечено как недоступное", mac)
                    device.available = False

    async def _async_check_device_udp(self, device: SyncleoDevice) -> bool:
        """Резервная проверка ТОЛЬКО для устройств без координатора."""
        # Если координатор управляет сессией, вообще игнорируем
        if device.is_coordinator_connected:
            return True
            
        # Не пингуем, если нет данных от Zeroconf
        if device.ip == "0.0.0.0" or device.port == 0 or not device.public_key or len(device.token) != 32:
            return False

        try:
            phone_pub, keys = make_x25519_keys(device.public_key)
            token_bytes = bytes.fromhex(device.token)
            encrypted_token = aes_cbc_encrypt(
                keys.tx_key_base, keys.tx_iv_base, token_bytes, pad=False
            )
            
            payload = bytes([CMD_HANDSHAKE]) + phone_pub + encrypted_token
            packet = build_frame(0, FRAME_CMD, payload)
            
            response = await SyncleoUdpClient.async_send_and_receive(
                device.ip, device.port, packet, timeout=1.0
            )
            
            if not response or not (parsed := parse_frame(response)):
                return False
                
            seq, frame_type, resp_payload = parsed
            
            if frame_type == FRAME_NAK: 
                return False
            
            if frame_type == FRAME_ACK and resp_payload and len(resp_payload) == 16:
                try:
                    key, iv = keys.rx_key_iv(seq)
                    aes_cbc_decrypt(key, iv, resp_payload, unpad=True)
                    return True 
                except Exception:
                    return False

            if frame_type == FRAME_CMD:
                plain = decrypt_frame_payload(seq, resp_payload, keys)
                if plain and plain[0] == CMD_HANDSHAKE:
                    ack_packet = build_encrypted_ack_frame(seq, keys)
                    await SyncleoUdpClient.async_send_and_receive(
                        device.ip, device.port, ack_packet, timeout=0.5
                    )
                    return True
                    
            return False
            
        except Exception:
            return False
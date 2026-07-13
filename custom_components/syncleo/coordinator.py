# coordinator.py
import asyncio
import logging
from typing import Any, Dict, Optional

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .device import SyncleoDevice
from .protocol import (
    CMD_HANDSHAKE, FRAME_ACK, FRAME_CMD, FRAME_NAK,
    make_x25519_keys, aes_cbc_encrypt, aes_cbc_decrypt,
    build_frame, parse_frame, decrypt_frame_payload, 
    build_encrypted_ack_frame, build_encrypted_cmd_frame, CMD_NAMES
)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

class _PushProtocol(asyncio.DatagramProtocol):
    """Вспомогательный протокол для асинхронного чтения UDP пакетов."""
    def __init__(self) -> None:
        self.queue = asyncio.Queue()

    def datagram_received(self, data: bytes, addr: tuple) -> None:
        self.queue.put_nowait(data)

    def error_received(self, exc: Exception) -> None:
        _LOGGER.debug("UDP Socket error: %s", exc)

    async def get_packet(self, timeout: float) -> Optional[bytes]:
        try:
            return await asyncio.wait_for(self.queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

class SyncleoCoordinator(DataUpdateCoordinator):
    """Координатор для поддержания постоянной Push-сессии со устройством."""

    def __init__(self, hass: HomeAssistant, device: SyncleoDevice) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"Syncleo {device.mac}",
            update_interval=None,
        )
        self.device = device
        self._transport = None
        self._protocol = None
        self._listen_task: Optional[asyncio.Task] = None
        self._keys = None
        self._seq = 0
        self._ping_fail_count = 0
        self._reconnect_event = asyncio.Event()
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 3
        self._reconnect_delay = 30
        self._is_connecting = False
        # Инициализируем стартовые данные
        self.data = {"available": False, "last_cmd": None, "CMD_PROGRAM_DATA": {}}

    def start(self) -> None:
        """Запуск фонового цикла прослушивания."""
        self._listen_task = self.hass.async_create_background_task(
            self._connection_loop(),
            name=f"syncleo_coordinator_{self.device.mac}",
        )

    async def async_stop(self) -> None:
        """Остановка сессии."""
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
        self._close_transport()
        self.device.is_coordinator_connected = False

    def _close_transport(self) -> None:
        if self._transport:
            self._transport.close()
            self._transport = None
            self._protocol = None

    async def _connection_loop(self) -> None:
        """Основной цикл: подключение -> прослушивание -> реконнект."""
        while True:
            try:
                # Проверяем, не нужно ли выйти из цикла
                if self._is_connecting:
                    _LOGGER.debug("Уже выполняется подключение для %s", self.device.mac)
                    await asyncio.sleep(1)
                    continue
                    
                self._is_connecting = True
                _LOGGER.info("Инициализация Push-сессии для %s", self.device.mac)
                self._close_transport()
                self.device.is_coordinator_connected = False
                self._seq = 0
                self._ping_fail_count = 0

                # 1. Создаем постоянный UDP сокет
                loop = asyncio.get_running_loop()
                self._protocol = _PushProtocol()
                self._transport, _ = await loop.create_datagram_endpoint(
                    lambda: self._protocol,
                    local_addr=('0.0.0.0', 0)
                )

                # 2. Выполняем Handshake через этот сокет
                if not await self._do_handshake():
                    _LOGGER.warning("Handshake не удался для %s", self.device.mac)
                    self._is_connecting = False
                    await self._wait_for_reconnect()
                    continue

                # 3. Успешно! Обновляем статус
                self.device.is_coordinator_connected = True
                self._ping_fail_count = 0
                self._reconnect_attempts = 0
                self._reconnect_event.clear()
                self._is_connecting = False
                self.async_set_updated_data({"available": True, "state": "connected"})
                _LOGGER.info("Push-сессия установлена для %s", self.device.mac)

                # 4. Цикл прослушивания входящих пакетов (Push)
                while True:
                    # Проверяем сигнал переподключения
                    if self._reconnect_event.is_set():
                        _LOGGER.info("Получен сигнал переподключения для %s", self.device.mac)
                        break
                    
                    # Ждем данные от устройства
                    packet = await self._protocol.get_packet(timeout=10.0)
                    
                    if not packet:
                        # Таймаут. Устройство не отвечает
                        self._ping_fail_count += 1
                        _LOGGER.debug("Нет ответа от %s (попытка %d/3)", self.device.mac, self._ping_fail_count)
                        
                        if self._ping_fail_count >= 3:
                            # 3 провала! Помечаем как недоступное
                            _LOGGER.warning("Устройство %s не в сети. Помечаем как недоступное.", self.device.mac)
                            self.device.is_coordinator_connected = False
                            self.async_set_updated_data({"available": False, "state": "unavailable"})
                            
                            # Закрываем старый сокет
                            self._close_transport()
                            
                            # Переходим в режим ожидания
                            await self._wait_for_reconnect()
                            break  # Выходим из внутреннего цикла, чтобы начать новый Handshake
                        else:
                            # Менее 3 провалов - шлем keepalive (Handshake)
                            if not await self._do_handshake():
                                # Если Handshake упал - увеличиваем счетчик и продолжаем
                                self._ping_fail_count += 1
                                if self._ping_fail_count >= 3:
                                    _LOGGER.warning("Устройство %s не отвечает на Handshake. Помечаем как недоступное.", self.device.mac)
                                    self.device.is_coordinator_connected = False
                                    self.async_set_updated_data({"available": False, "state": "unavailable"})
                                    self._close_transport()
                                    await self._wait_for_reconnect()
                                    break
                            continue

                    # Если пакет пришел - сбрасываем счетчик
                    self._ping_fail_count = 0
                    
                    # 5. Обработка пришедшего пакета
                    self._handle_incoming_packet(packet)

            except asyncio.CancelledError:
                break  # Завершение интеграции
            except Exception as e:
                _LOGGER.error("Ошибка сессии %s: %s", self.device.mac, e, exc_info=True)
                # Помечаем как недоступное при любой ошибке
                self.device.is_coordinator_connected = False
                self.async_set_updated_data({"available": False, "state": "unavailable"})
                self._close_transport()
                self._is_connecting = False
                await self._wait_for_reconnect()
            
        self.device.is_coordinator_connected = False
        self._close_transport()
        self._is_connecting = False

    async def _wait_for_reconnect(self) -> None:
        """Ожидание перед переподключением с возможностью прерывания по событию."""
        self._reconnect_attempts += 1
        
        # Сразу проверяем, не установлен ли уже флаг переподключения
        if self._reconnect_event.is_set():
            _LOGGER.debug("Сигнал переподключения уже установлен для %s", self.device.mac)
            self._reconnect_attempts = 0
            return
            
        if self._reconnect_attempts > self._max_reconnect_attempts:
            # Слишком много попыток - ждем сигнала от Zeroconf или таймаут 5 минут
            _LOGGER.warning("Достигнут лимит попыток переподключения для %s. Ожидание сигнала от Zeroconf...", self.device.mac)
            try:
                # Ждем сигнала от Zeroconf
                await self._reconnect_event.wait()
                _LOGGER.info("Получен сигнал пробуждения для %s, переподключаемся...", self.device.mac)
                self._reconnect_attempts = 0
                self._reconnect_event.clear()
                return
            except asyncio.CancelledError:
                raise
            except Exception as e:
                _LOGGER.error("Ошибка ожидания сигнала: %s", e)
                self._reconnect_attempts = 0
                return
        else:
            # Обычная задержка между попытками
            delay = self._reconnect_delay * self._reconnect_attempts
            _LOGGER.debug("Ожидание %d сек перед переподключением %s (попытка %d/%d)", 
                         delay, self.device.mac, self._reconnect_attempts, self._max_reconnect_attempts)
            try:
                # Ждем с возможностью прерывания по событию
                await asyncio.wait_for(self._reconnect_event.wait(), timeout=delay)
                # Если событие установлено - немедленно выходим
                _LOGGER.info("Получен сигнал пробуждения во время ожидания для %s", self.device.mac)
                self._reconnect_attempts = 0
                self._reconnect_event.clear()
                return
            except asyncio.TimeoutError:
                # Таймаут прошел - пробуем переподключиться
                _LOGGER.debug("Таймаут ожидания для %s, пробуем переподключиться", self.device.mac)
                return
            except asyncio.CancelledError:
                raise
            except Exception as e:
                _LOGGER.error("Ошибка в ожидании: %s", e)
                return

    async def trigger_reconnect(self) -> None:
        """Вызывается Менеджером, когда устройство анонсирует себя в сети."""
        _LOGGER.info("=== TRIGGER_RECONNECT вызван для %s ===", self.device.mac)
        self._reconnect_event.set()
        # Если координатор не активен или нет подключения - пробуем переподключиться немедленно
        if not self.device.is_coordinator_connected:
            _LOGGER.info("Устройство %s не в сети, пробуем переподключиться немедленно", self.device.mac)
            self._reconnect_attempts = 0
            # Отменяем текущий listen_task, чтобы он перезапустился
            if self._listen_task and not self._listen_task.done():
                self._listen_task.cancel()
                try:
                    await self._listen_task
                except asyncio.CancelledError:
                    pass
            # Запускаем новое подключение
            self.start()

    async def _do_handshake(self) -> bool:
        """Выполнение handshake по текущему транспорту."""
        if not self.device.public_key or len(self.device.token) != 32:
            return False

        try:
            # Генерируем новые ключи (seq = 0)
            self._seq = 0
            phone_pub, keys = make_x25519_keys(self.device.public_key)
            token_bytes = bytes.fromhex(self.device.token)
            encrypted_token = aes_cbc_encrypt(
                keys.tx_key_base, keys.tx_iv_base, token_bytes, pad=False
            )
            
            payload = bytes([CMD_HANDSHAKE]) + phone_pub + encrypted_token
            packet = build_frame(self._seq, FRAME_CMD, payload)
            
            self._transport.sendto(packet, (self.device.ip, self.device.port))
            
            # Ждем ответ
            response = await self._protocol.get_packet(timeout=3.0)
            if not response or not (parsed := parse_frame(response)):
                return False
                
            seq, frame_type, resp_payload = parsed
            
            if frame_type == FRAME_NAK:
                return False
            
            # Обработка зашифрованного ACK
            if frame_type == FRAME_ACK and resp_payload and len(resp_payload) == 16:
                try:
                    key, iv = keys.rx_key_iv(seq)
                    aes_cbc_decrypt(key, iv, resp_payload, unpad=True)
                    self._keys = keys
                    self._seq = (self._seq + 1) & 0xFF
                    _LOGGER.debug("Push Handshake успешен (ACK)")
                    return True
                except Exception:
                    return False

            # Обработка стандартного CMD ответа
            if frame_type == FRAME_CMD:
                plain = decrypt_frame_payload(seq, resp_payload, keys)
                if plain and plain[0] == CMD_HANDSHAKE:
                    self._keys = keys
                    self._seq = (seq + 1) & 0xFF
                    ack_packet = build_encrypted_ack_frame(seq, keys)
                    self._transport.sendto(ack_packet, (self.device.ip, self.device.port))
                    _LOGGER.debug("Push Handshake успешен (CMD)")
                    return True
                    
            return False
        except Exception as e:
            _LOGGER.debug("Ошибка Handshake в координаторе: %s", e)
            return False

    async def async_send_command(self, cmd: int, payload: bytes = b"") -> bool:
        """Отправка зашифрованной команды устройству по активной сессии."""
        if not self._transport or not self._keys:
            _LOGGER.warning("Попытка отправить команду без активной сессии (нет ключей или сокета)")
            return False

        try:
            packet = build_encrypted_cmd_frame(self._seq, cmd, payload, self._keys)
            self._transport.sendto(packet, (self.device.ip, self.device.port))
            _LOGGER.debug("-> Отправлена команда %s (%s) на %s:%d (seq=%d)", CMD_NAMES.get(cmd, f"CMD_UNKNOWN_0x{cmd:02X}"), payload.hex(), self.device.ip, self.device.port, self._seq)
            self._seq = (self._seq + 1) & 0xFF
            return True
            
        except Exception as e:
            _LOGGER.error("Ошибка отправки команды 0x%02X: %s", cmd, e)
            return False

    def _handle_incoming_packet(self, packet: bytes) -> None:
        """Расшифровка и обработка входящего Push-сообщения."""
        if not self._keys:
            return

        try:
            parsed = parse_frame(packet)
            if not parsed:
                return
                
            seq, frame_type, payload = parsed

            if frame_type == FRAME_CMD and payload:
                try:
                    # Расшифровываем
                    plain = decrypt_frame_payload(seq, payload, self._keys)
                    
                    if not plain:
                        return
                        
                    cmd = plain[0]
                    data = plain[1:]
                    
                    # 1. ВАЖНО: СНАЧАЛА ОТПРАВЛЯЕМ ACK В ЛЮБОМ СЛУЧАЕ!
                    ack_packet = build_encrypted_ack_frame(seq, self._keys)
                    self._transport.sendto(ack_packet, (self.device.ip, self.device.port))

                    # 2. Игнорируем ответный Handshake (0x00) только после отправки ACK
                    if cmd == CMD_HANDSHAKE:
                        _LOGGER.debug("Получен ответный Handshake (0x00), ACK отправлен, данные игнорируем")
                        return

                    # 3. Получаем человекочитаемое имя команды
                    cmd_name = CMD_NAMES.get(cmd, f"CMD_UNKNOWN_0x{cmd:02X}")
                    
                    _LOGGER.info("Message from the device %s: %s | Data: %s", self.device.mac, cmd_name, data.hex())

                    # 4. ФОРМИРУЕМ НОВОЕ СОСТОЯНИЕ
                    new_state = dict(self.data)
                    new_state["available"] = True
                    new_state["last_cmd"] = cmd_name

                    # 5. Обработка CMD_PROGRAM_DATA (0x42)
                    if cmd == 0x42: 
                        if data:
                            index = data[0]
                            payload_hex = data[1:].hex() if len(data) > 1 else ""
#                            programs = {}
                            programs = dict(new_state.get("CMD_PROGRAM_DATA", {}))
                            programs[str(index)] = payload_hex
                            
                            new_state["CMD_PROGRAM_DATA"] = programs
                            _LOGGER.debug("Обновлен Program Data: %s", programs)
                    # 6. Обработка CMD_EXPENDABLES (0x22)
                    elif cmd == 0x22: 
                        if data:
                            filter_data = {}
                            for i in range(6):
                                offset = i * 2
                                if len(data) >= offset + 2:
                                    filter_bytes = int.from_bytes(data[offset:offset + 2], 'little')
                                    filter_data[str(i)] = filter_bytes
                            new_state["CMD_EXPENDABLES"] = filter_data
                    else:
                        # Для всех остальных команд просто сохраняем hex строки
                        new_state[cmd_name] = data.hex()
                    
                    # 7. Пушим новые данные в Home Assistant
                    if cmd != 0xFF:
                        self.async_set_updated_data(new_state)
                        _LOGGER.debug("Координатор: %s", self.data)
                        
                except Exception as e:
                    _LOGGER.warning("Ошибка обработки пуша %s: %s", self.device.mac, e, exc_info=True)

        except Exception as e:
            _LOGGER.warning("Ошибка парсинга фрейма от %s: %s", self.device.mac, e)

    async def _async_update_data(self) -> Dict[str, Any]:
        return self.data if self.data else {"available": False}
import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .const import DOMAIN, POLARIS_DEVICE, HOMMYN_DEVICE

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

class SyncleoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow для добавления устройства Syncleo через Zeroconf."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self) -> None:
        self._discovery_info: Optional[ZeroconfServiceInfo] = None
        self._mac: Optional[str] = None

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> FlowResult:
        """Обрабатывает обнаружение устройства через Zeroconf."""
        self._discovery_info = discovery_info
        _LOGGER.info("Discovered device via zeroconf: %s", self._discovery_info)
        
        # Извлекаем MAC адрес (теперь свойства - это строки, а не байты)
        props = discovery_info.properties
        mac = props.get('macaddr', '')
        public = props.get('public', '')
        vendor = props.get('vendor', '')
        devtype = props.get('devtype', '')
        firmware = props.get('firmware', '')
        
        if not mac:
            return self.async_abort(reason="unknown_device")

        self._mac = mac
        self._public = public
        self._vendor = vendor
        self._devtype = devtype
        self._firmware = firmware

        # Устанавливаем уникальный ID по MAC адресу
        await self.async_set_unique_id(mac)
        
        # Если устройство с таким MAC уже добавлено - прерываем поток
        self._abort_if_unique_id_configured()

        # Показываем пользователю форму ввода токена
        return await self.async_step_confirm()

    async def async_step_confirm(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Шаг подтверждения и ввода токена."""
        errors = {}

        if user_input is not None:
            token = user_input["token"]
            if not token:
                errors["base"] = "token_required"
            else:
                # СОХРАНЯЕМ ДАННЫЕ ZEROCONF ВО ВРЕМЕННОЕ ХРАНИЛИЩЕ
                self.hass.data.setdefault(DOMAIN, {})["pending_zeroconf"] = self._discovery_info
                return self.async_create_entry(
                    title=f"Syncleo {self._mac}",                                                               # Добавтить тип и модель
                    data={
                        "mac": self._mac,
                        "token": token,
                        "vendor": self._vendor,
                        "devtype": self._devtype,
                        "firmware": self._firmware,
                    },
                )

        # Получаем данные для красивого отображения в UI
        vendor = self._discovery_info.properties.get('vendor', 'Unknown')
        devtype = self._discovery_info.properties.get('devtype', '0')
        _LOGGER.debug("Discovered device: %s", self._discovery_info)
        device_info = POLARIS_DEVICE[int(devtype)]
        placeholders = {"name": f"{vendor} {device_info['model']}"}
#        placeholders = {
#            "device": POLARIS_DEVICE[int(self._device_type)]['model'],
#            "class": await self.get_translated_type(POLARIS_DEVICE[int(self._device_type)]['class']),
#            "mac": self._device_mac
#        }
        self.context["title_placeholders"] = placeholders
        

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={"mac": self._mac, "vendor": vendor},
            data_schema=vol.Schema({vol.Required("token"): str}),
            errors=errors,
        )

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Обычный шаг добавления вручную."""
        return self.async_abort(reason="no_devices_found")
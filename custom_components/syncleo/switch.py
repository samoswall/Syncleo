# switch.py - упрощенная версия
import logging
from typing import Any
from slugify import slugify

from homeassistant.components.switch import SwitchEntity

from .const import (
    DOMAIN,
    POLARIS_DEVICE,
    HOMMYN_DEVICE,
)
from . import const as const_module

from .entity import SyncleoEntity
from .entity_description import SWITCH_DESCRIPTIONS

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

def get_command_from_state_key(state_key: str):
    """Получает числовое значение команды из строкового имени."""
    if not state_key:
        return None
    return getattr(const_module, state_key, None)

async def async_setup_entry(hass, entry, async_add_entities):
    """Настройка переключателей."""
    device_mac = entry.data["mac"]
    coordinator = hass.data[DOMAIN].get(entry.entry_id)
    
    if not coordinator:
        _LOGGER.warning("Coordinator not found for entry %s", entry.entry_id)
        return
    
    device = coordinator.device
    entity_config = device.entity_config
    
    entities = []
    
    if "switch" in entity_config:
        for key in entity_config["switch"]:
            if key in SWITCH_DESCRIPTIONS:
                desc = SWITCH_DESCRIPTIONS[key]
                entities.append(SyncleoSwitchEntity(coordinator, device, key, desc))
    
    async_add_entities(entities)


class SyncleoSwitchEntity(SyncleoEntity, SwitchEntity):
    """Переключатель Syncleo."""
    should_poll = False
    
    def __init__(self, coordinator, device, key, desc):
        super().__init__(coordinator, device, "switch", key, desc)
        
        self._state_key = getattr(desc, 'coordinator_state', None)
        self._func = getattr(desc, 'func', None)
        self._command = get_command_from_state_key(self._state_key)
        self._attr_has_entity_name = True
        self._attr_unique_id = slugify(f"{device.mac}_{key}")
        
        # Инициализируем состояние
        self._attr_is_on = False
        
        if device.vendor == 'Polaris':
            self.entity_id = f"switch.{POLARIS_DEVICE[int(device.devtype)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(device.devtype)]['model'].replace('-', '_').lower()}_{key.replace('-', '_').lower()}"
        if device.vendor == 'Hommyn':
            self.entity_id = f"switch.{HOMMYN_DEVICE[int(device.devtype)]['class'].replace('-', '_').lower()}_{HOMMYN_DEVICE[int(device.devtype)]['model'].replace('-', '_').lower()}_{key.replace('-', '_').lower()}"

    @property
    def is_on(self) -> bool:
        """Возвращает состояние переключателя."""
        if not self.available or not self._state_key:
            return False
        
        value = self._get_state_from_coordinator(self._state_key, self._func)
        return bool(value) if value is not None else False

    def _handle_coordinator_update(self) -> None:
        """Обновление при пуше."""
        new_available = self.available
        if new_available != self._attr_available:
            self._attr_available = new_available
            if not new_available:
                self._attr_is_on = False
            self.async_write_ha_state()
            return
        
        if self.available:
            new_state = self.is_on
            if new_state != self._attr_is_on:
                self._attr_is_on = new_state
                self.async_write_ha_state()

    async def _async_set_state(self, state: bool) -> None:
        """Универсальный метод установки состояния."""
        if not self.available:
            _LOGGER.warning("Нельзя изменить состояние на недоступном устройстве %s", self.device.mac)
            return
        
        if self._command is None:
            _LOGGER.error("Неизвестная команда для переключателя %s (state_key=%s)", 
                         self.entity_key, self._state_key)
            return
            
        await self.async_send_command(self._command, b'\x01' if state else b'\x00')

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_set_state(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_set_state(False)
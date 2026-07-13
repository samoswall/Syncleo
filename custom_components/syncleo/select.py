# select.py
import logging
from typing import Optional
from slugify import slugify

from homeassistant.components.select import SelectEntity

from .const import DOMAIN, POLARIS_DEVICE, HOMMYN_DEVICE, CMD_TARGET_TEMPERATURE, CMD_MODE
from .entity import SyncleoEntity
from .entity_description import SELECT_DESCRIPTIONS

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

async def async_setup_entry(hass, entry, async_add_entities):
    """Настройка селектов."""
    device_mac = entry.data["mac"]
    coordinator = hass.data[DOMAIN].get(entry.entry_id)
    
    if not coordinator:
        _LOGGER.warning("Coordinator not found for entry %s", entry.entry_id)
        return
    
    device = coordinator.device
    entity_config = device.entity_config
    
    entities = []
    
    if "select" in entity_config:
        for key in entity_config["select"]:
            if key in SELECT_DESCRIPTIONS:
                desc = SELECT_DESCRIPTIONS[key]
                entities.append(SyncleoSelectEntity(coordinator, device, key, desc))
    
    async_add_entities(entities)


class SyncleoSelectEntity(SyncleoEntity, SelectEntity):
    """Селект Syncleo."""
    should_poll = False
    
    def __init__(self, coordinator, device, key, desc):
        super().__init__(coordinator, device, "select", key, desc)
        
        self._options = getattr(desc, 'options', {})
        self._coordinator_mode = getattr(desc, 'coordinator_mode', None)
        self._coordinator_target = getattr(desc, 'coordinator_target_temperature', None)
        self._attr_options = list(self._options.keys())
        self._attr_has_entity_name = True
        
        # Инициализируем текущий вариант
        self._attr_current_option = self._attr_options[0] if self._attr_options else "not_selected"
        
        self._attr_unique_id = slugify(f"{device.mac}_{key}")
        if device.vendor == 'Polaris':
            self.entity_id = f"select.{POLARIS_DEVICE[int(device.devtype)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(device.devtype)]['model'].replace('-', '_').lower()}_{key.replace('-', '_').lower()}"
        if device.vendor == 'Rusclimate':
            self.entity_id = f"select.{HOMMYN_DEVICE[int(device.devtype)]['class'].replace('-', '_').lower()}_{HOMMYN_DEVICE[int(device.devtype)]['model'].replace('-', '_').lower()}_{key.replace('-', '_').lower()}"

    @property
    def current_option(self) -> Optional[str]:
        """Возвращает текущий выбранный вариант."""
        # Если устройство недоступно, возвращаем None
        if not self.available:
            return None
            
        if self._coordinator_mode:
            value = self._get_state_from_coordinator(self._coordinator_mode, None)
            if value is not None:
                # Преобразуем значение в число для сравнения
                if isinstance(value, bytes):
                    value = int.from_bytes(value, 'little')
                elif isinstance(value, str):
                    try:
                        value = int(value)
                    except ValueError:
                        pass
                
                # Ищем режим по значению
                for name, val in self._options.items():
                    if value == val:
                        return name
        
        return self._attr_options[0] if self._attr_options else "not_selected"

    def _handle_coordinator_update(self) -> None:
        """Вызывается МГНОВЕННО при получении пуша от устройства."""
        # Обновляем доступность
        new_available = self.available
        if new_available != self._attr_available:
            self._attr_available = new_available
            if not new_available:
                # Если устройство недоступно, сбрасываем выбор
                self._attr_current_option = None
            self.async_write_ha_state()
            return
        
        # Обновляем опцию только если устройство доступно
        if self.available:
            new_option = self.current_option
            if new_option != self._attr_current_option:
                self._attr_current_option = new_option
                self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Выбирает вариант."""
        if not self.available:
            _LOGGER.warning("Нельзя выбрать опцию на недоступном устройстве %s", self.device.mac)
            return
            
        if option not in self._options:
            return
        value = self._options[option]
        if POLARIS_DEVICE[int(self.device.devtype)]['class'] == "kettle":
            _LOGGER.debug("Select recipe temperature %s", value)
            payload = bytes([int(value), 0])
            await self.async_send_command(CMD_TARGET_TEMPERATURE, payload)
            payload = bytes([0x03])
            await self.async_send_command(CMD_MODE, payload)
        pass
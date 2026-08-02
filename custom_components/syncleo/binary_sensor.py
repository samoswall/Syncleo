# binary_sensor.py
import logging
from typing import Optional
from slugify import slugify

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)

from .const import DOMAIN, POLARIS_DEVICE, HOMMYN_DEVICE
from .entity import SyncleoEntity
from .entity_description import BINARY_SENSOR_DESCRIPTIONS

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

async def async_setup_entry(hass, entry, async_add_entities):
    """Настройка бинарных сенсоров."""
    coordinator = hass.data[DOMAIN].get(entry.entry_id)

    if not coordinator:
        _LOGGER.warning("Coordinator not found for entry %s", entry.entry_id)
        return

    device = coordinator.device
    entity_config = device.entity_config
    _LOGGER.debug("BINARY_SENSOR_entity_config %s", entity_config)

    entities = []

    if "binary_sensor" in entity_config:
        for key in entity_config["binary_sensor"]:
            if key in BINARY_SENSOR_DESCRIPTIONS:
                desc = BINARY_SENSOR_DESCRIPTIONS[key]
                entities.append(SyncleoBinarySensorEntity(coordinator, device, key, desc))

    async_add_entities(entities)


class SyncleoBinarySensorEntity(SyncleoEntity, BinarySensorEntity):
    """Бинарный сенсор Syncleo."""
    should_poll = False

    def __init__(self, coordinator, device, key, desc):
        super().__init__(coordinator, device, "binary_sensor", key, desc)

        if hasattr(desc, 'device_class') and desc.device_class:
            self._attr_device_class = desc.device_class
        if hasattr(desc, 'translation_key') and desc.translation_key:
            self._attr_translation_key = desc.translation_key
        if hasattr(desc, 'key') and desc.key:
            self._key = desc.key

        self._state_key = getattr(desc, 'coordinator_state', None)
        self._program_index = getattr(desc, 'program_index', "0")
        self._error_code = getattr(desc, "error_code", None)
        self._attr_has_entity_name = True

        # Инициализируем состояние
        self._attr_is_on = False

        _LOGGER.debug("Device Binary Sensor: %s, key: %s, desc: %s", device, key, desc)
        self._attr_unique_id = slugify(f"{device.mac}_{key}")
        if device.vendor == 'Polaris':
            self.entity_id = f"binary_sensor.{POLARIS_DEVICE[int(device.devtype)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(device.devtype)]['model'].replace('-', '_').lower()}_{key.replace('-', '_').lower()}"
        if device.vendor == 'RusClimate':
            self.entity_id = f"binary_sensor.{HOMMYN_DEVICE[int(device.devtype)]['class'].replace('-', '_').lower()}_{HOMMYN_DEVICE[int(device.devtype)]['model'].replace('-', '_').lower()}_{key.replace('-', '_').lower()}"

    @property
    def is_on(self) -> bool:
        """Возвращает состояние бинарного сенсора."""
        # Если устройство недоступно, возвращаем None
        if not self.available:
            return None
        
        if not self._state_key:
            return None
        
        # Сенсоры, работающие через ERROR код
        if self._error_code:
            error = self._get_state_from_coordinator("CMD_ERROR", None)
            if error is not None:
                error_hex = error.hex() if isinstance(error, bytes) else str(error)
                # Проверяем наличие кода ошибки
                return False if self._error_code in error_hex else True
            return True

        # Сенсор "cappuccinator" - проверяем уровень молока в баке
#        if self._key == "cappuccinator":
#            tank = self._get_state_from_coordinator("CMD_TANK", None)
#            if tank is not None:
#                # Если уровень молока низкий - проблема
#                return tank[0] == 0 if isinstance(tank, bytes) else tank == 0
#            return False



        return False

    def _handle_coordinator_update(self) -> None:
        """Вызывается МГНОВЕННО при получении пуша от устройства."""
        new_available = self.available
        if new_available != self._attr_available:
            self._attr_available = new_available
            if not new_available:
                self._attr_is_on = None
            self.async_write_ha_state()
            return

        if self.available:
            new_state = self.is_on
            if new_state != self._attr_is_on:
                self._attr_is_on = new_state
                self.async_write_ha_state()
# sensor.py
import logging
from typing import Any, Dict, Optional
from slugify import slugify

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import EntityCategory

from .const import DOMAIN, POLARIS_DEVICE, HOMMYN_DEVICE
from .entity import SyncleoEntity
from .entity_description import SENSOR_DESCRIPTIONS

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

async def async_setup_entry(hass, entry, async_add_entities):
    """Настройка сенсоров."""
    device_mac = entry.data["mac"]
    coordinator = hass.data[DOMAIN].get(entry.entry_id)
    
    if not coordinator:
        _LOGGER.warning("Coordinator not found for entry %s", entry.entry_id)
        return
    
    device = coordinator.device
    entity_config = device.entity_config
    _LOGGER.debug("SENSOR_entity_config %s",entity_config)
    entities = []
    
    if "sensor" in entity_config:
        for key in entity_config["sensor"]:
            if key in SENSOR_DESCRIPTIONS:
                desc = SENSOR_DESCRIPTIONS[key]
                entities.append(SyncleoSensorEntity(coordinator, device, key, desc))
    
    async_add_entities(entities)


class SyncleoSensorEntity(SyncleoEntity, SensorEntity):
    """Сенсор Syncleo."""
    should_poll = False
    
    def __init__(self, coordinator, device, key, desc):
        super().__init__(coordinator, device, "sensor", key, desc)
        
        if hasattr(desc, 'device_class') and desc.device_class:
            self._attr_device_class = desc.device_class
        if hasattr(desc, 'native_unit_of_measurement') and desc.native_unit_of_measurement:
            self._attr_native_unit_of_measurement = desc.native_unit_of_measurement
        if hasattr(desc, 'state_class') and desc.state_class:
            self._attr_state_class = desc.state_class
        if hasattr(desc, 'translation_key') and desc.translation_key:
            self._attr_translation_key = desc.translation_key
        
        self._state_key = getattr(desc, 'coordinator_state', None)
        self._expendables_index = getattr(desc, 'expendables_index', "0")
        self._program_index = getattr(desc, 'program_index', "0")
        self._func = getattr(desc, 'func', None)
        self._attr_has_entity_name = True
        
        # Инициализируем значение
        self._attr_native_value = None
        
        _LOGGER.debug("Device Sensor: %s, key: %s, desc: %s", device, key, desc)
        self._attr_unique_id = slugify(f"{device.mac}_{key}")
        if device.vendor == 'Polaris':
            self.entity_id = f"sensor.{POLARIS_DEVICE[int(device.devtype)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(device.devtype)]['model'].replace('-', '_').lower()}_{key.replace('-', '_').lower()}"
        if device.vendor == 'Rusclimate':
            self.entity_id = f"sensor.{HOMMYN_DEVICE[int(device.devtype)]['class'].replace('-', '_').lower()}_{HOMMYN_DEVICE[int(device.devtype)]['model'].replace('-', '_').lower()}_{key.replace('-', '_').lower()}"

    @property
    def native_value(self):
        """Возвращает значение сенсора."""
        # Если устройство недоступно, возвращаем None
        if not self.available:
            return None
            
        # Для диагностических сенсоров берем данные из устройства
        if self.entity_key == "firmware":
            return self.device.firmware
        elif self.entity_key == "device_type":
            return self.device.devtype
        
        if not self._state_key:
            return None
        
        if self._state_key == "CMD_EXPENDABLES":
            if not self.coordinator.data:
                return None
            value_data = self.coordinator.data.get("CMD_EXPENDABLES", {})
            value = value_data.get(self._expendables_index)
        elif self._state_key == "CMD_PROGRAM_DATA":
            if not self.coordinator.data:
                return None
            value_data = self.coordinator.data.get("CMD_EXPENDABLES", {})
            value = value_data.get(self._program_index)
            # Возможно нужен парсер и умножение на 10 или 20
        else:
            value = self._get_state_from_coordinator(self._state_key, self._func)
        return value
    
    def _handle_coordinator_update(self) -> None:
        """Вызывается МГНОВЕННО при получении пуша от координатора."""
        # Обновляем доступность
        new_available = self.available
        if new_available != self._attr_available:
            self._attr_available = new_available
            if not new_available:
                # Если устройство недоступно, очищаем значение
                self._attr_native_value = None
            self.async_write_ha_state()
            return
        
        # Обновляем значение только если устройство доступно
        if self.available:
            new_value = self.native_value
            if new_value != self._attr_native_value:
                self._attr_native_value = new_value
                self.async_write_ha_state()
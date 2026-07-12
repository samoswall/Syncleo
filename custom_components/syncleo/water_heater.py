# water_heater.py
import logging
import struct
from typing import Optional
from slugify import slugify

from homeassistant.components.water_heater import WaterHeaterEntity, WaterHeaterEntityFeature
from homeassistant.const import UnitOfTemperature

from .const import (
    DOMAIN,
    POLARIS_DEVICE,
    HOMMYN_DEVICE,
    CMD_MODE,
    CMD_TARGET_TEMPERATURE,
)
from .entity import SyncleoEntity
from .entity_description import WATER_HEATER_DESCRIPTIONS, parse_temp

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

async def async_setup_entry(hass, entry, async_add_entities):
    """Настройка водонагревателей."""
    device_mac = entry.data["mac"]
    coordinator = hass.data[DOMAIN].get(entry.entry_id)
    
    if not coordinator:
        _LOGGER.warning("Coordinator not found for entry %s", entry.entry_id)
        return
    
    device = coordinator.device
    entity_config = device.entity_config
    _LOGGER.debug("WATER_HEATER_entity_config %s",entity_config)
    entities = []
    
    if "water_heater" in entity_config:
        for key in entity_config["water_heater"]:
            if key in WATER_HEATER_DESCRIPTIONS:
                desc = WATER_HEATER_DESCRIPTIONS[key]
                entities.append(SyncleoWaterHeaterEntity(coordinator, device, key, desc))
    
    async_add_entities(entities)


class SyncleoWaterHeaterEntity(SyncleoEntity, WaterHeaterEntity):
    """Водонагреватель Syncleo."""
    should_poll = False
    
    def __init__(self, coordinator, device, key, desc):
        super().__init__(coordinator, device, "water_heater", key, desc)
        
        self._min_temp = getattr(desc, 'min_temp', 30)
        self._max_temp = getattr(desc, 'max_temp', 100)
        self._operation_list = getattr(desc, 'operation_list', {})
        self._coordinator_mode = getattr(desc, 'coordinator_mode', None)
        self._coordinator_target = getattr(desc, 'coordinator_target_temperature', None)
        self._coordinator_current = getattr(desc, 'coordinator_current_temperature', None)
        
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_min_temp = self._min_temp
        self._attr_max_temp = self._max_temp
        self._attr_target_temperature = self._max_temp
        self._attr_operation_list = list(self._operation_list.keys())
        
        # Инициализируем текущую температуру
        self._attr_current_temperature = None
        self._attr_current_operation = None
        
        # Определяем поддерживаемые функции
        features = WaterHeaterEntityFeature.TARGET_TEMPERATURE
        if len(self._operation_list) > 1:
            features |= WaterHeaterEntityFeature.OPERATION_MODE
        self._attr_supported_features = features
        self._attr_has_entity_name = True
        self._attr_unique_id = slugify(f"{device.mac}_{key}")
        if device.vendor == 'Polaris':
            self.entity_id = f"water_heater.{POLARIS_DEVICE[int(device.devtype)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(device.devtype)]['model'].replace('-', '_').lower()}_{key.replace('-', '_').lower()}"
        if device.vendor == 'Hommyn':
            self.entity_id = f"water_heater.{HOMMYN_DEVICE[int(device.devtype)]['class'].replace('-', '_').lower()}_{HOMMYN_DEVICE[int(device.devtype)]['model'].replace('-', '_').lower()}_{key.replace('-', '_').lower()}"

    @property
    def current_temperature(self) -> Optional[float]:
        """Возвращает текущую температуру."""
        if not self.available:
            return None
        if not self._coordinator_current:
            return None
        return self._get_state_from_coordinator(self._coordinator_current, parse_temp)

    @property
    def target_temperature(self) -> Optional[float]:
        """Возвращает целевую температуру."""
        if not self.available:
            return None
        if not self._coordinator_target:
            return None
        return self._get_state_from_coordinator(self._coordinator_target, parse_temp)

    @property
    def current_operation(self) -> Optional[str]:
        """Возвращает текущий режим работы."""
        if not self.available:
            return None
        if not self._coordinator_mode:
            return None
        
        value = self._get_state_from_coordinator(self._coordinator_mode, None)
        if value is None:
            return None
        # Ищем режим по значению
        for mode, val in self._operation_list.items():
            if int.from_bytes(value, 'little') == int(val):
                return mode
        
        return None

    def _handle_coordinator_update(self) -> None:
        """Вызывается МГНОВЕННО при получении пуша от устройства."""
        # Обновляем доступность
        new_available = self.available
        if new_available != self._attr_available:
            self._attr_available = new_available
            if not new_available:
                # Если устройство недоступно, очищаем значения
                self._attr_current_temperature = None
                self._attr_target_temperature = None
                self._attr_current_operation = None
            self.async_write_ha_state()
            return
        
        # Обновляем значения только если устройство доступно
        if self.available:
            # Просто вызываем обновление состояния
            self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs):
        """Устанавливает целевую температуру."""
        if not self.available:
            _LOGGER.warning("Нельзя установить температуру на недоступном устройстве %s", self.device.mac)
            return
            
        temperature = kwargs.get("temperature")
        if temperature is None:
            return
        self._attr_target_temperature = temperature
        payload = bytes([int(temperature), 0])
        await self.async_send_command(CMD_TARGET_TEMPERATURE, payload)
        self.schedule_update_ha_state()
        pass

    async def async_set_operation_mode(self, operation_mode: str):
        """Устанавливает режим работы."""
        if not self.available:
            _LOGGER.warning("Нельзя установить режим на недоступном устройстве %s", self.device.mac)
            return
            
        if operation_mode not in self._operation_list:
            _LOGGER.warning("Неизвестный режим: %s", operation_mode)
            return
        mode_value = self._operation_list[operation_mode]
        _LOGGER.debug("WaterHeater mode %d", int(mode_value))
        if int(mode_value) > 1:
            payload = bytes([int(self._attr_target_temperature), 0])
            await self.async_send_command(CMD_TARGET_TEMPERATURE, payload)
        payload = bytes([int(mode_value)])
        await self.async_send_command(CMD_MODE, payload)
        pass
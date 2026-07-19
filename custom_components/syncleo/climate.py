import logging
from typing import Optional, List
from slugify import slugify

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    ATTR_HVAC_MODE,
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature

from .const import (
    DOMAIN,
    POLARIS_DEVICE,
    HOMMYN_DEVICE,
    CMD_MODE,
    CMD_TARGET_TEMPERATURE,
    CMD_CURRENT_TEMPERATURE,
    CMD_SPEED,
    CMD_PROGRAM_DATA,
)
from .entity import SyncleoEntity
from .entity_description import CLIMATE_DESCRIPTIONS, parse_temp

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


async def async_setup_entry(hass, entry, async_add_entities):
    """Настройка климат-контроля."""
    coordinator = hass.data[DOMAIN].get(entry.entry_id)

    if not coordinator:
        _LOGGER.warning("Coordinator not found for entry %s", entry.entry_id)
        return

    device = coordinator.device
    entity_config = device.entity_config
    _LOGGER.debug("CLIMATE_entity_config %s", entity_config)

    entities = []

    # Если есть climate в конфигурации
    if "climate" in entity_config:
        for key in entity_config["climate"]:
            _LOGGER.debug("Processing climate key: %s", key)
            
            if key in CLIMATE_DESCRIPTIONS:
                desc = CLIMATE_DESCRIPTIONS[key]
                entities.append(SyncleoClimateEntity(coordinator, device, key, desc))
                _LOGGER.debug("Added climate entity with key: %s", key)
            else:
                _LOGGER.warning("Description not found for climate key: %s", key)

    _LOGGER.info("Adding %d climate entities", len(entities))
    async_add_entities(entities)


class SyncleoClimateEntity(SyncleoEntity, ClimateEntity):
    """Климат-контроль Syncleo."""

    should_poll = False

    def __init__(self, coordinator, device, key):
        super().__init__(coordinator, device, "climate", key, None)

        self._min_temp = getattr(desc, 'min_temp', 5)
        self._max_temp = getattr(desc, 'max_temp', 25)
        self._fan_mode = getattr(desc, 'fan_mode', "off")
        self._fan_modes = getattr(desc, 'fan_modes', {})
        self._preset_mode = getattr(desc, 'preset_mode', "auto")
        self._preset_modes = getattr(desc, 'preset_modes', {})
        self._hvac_modes = getattr(desc, 'hvac_modes', {})
        self._supported_features = getattr(desc, 'supported_features', 1)
        self._swing_mode = getattr(desc, 'swing_mode', "off")
        self._swing_modes = getattr(desc, 'swing_modes', {})
        
        self._coordinator_mode = getattr(desc, 'coordinator_mode', None)
        self._coordinator_target = getattr(desc, 'coordinator_target_temperature', None)
        self._coordinator_current = getattr(desc, 'coordinator_current_temperature', None)
        self._coordinator_speed = getattr(desc, 'coordinator_speed', None)
        self._coordinator_swing = getattr(desc, 'coordinator_swing', None)
        self._program_index = getattr(desc, 'program_index', None)
        self._func = getattr(desc, 'func', None)

        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_min_temp = self._min_temp
        self._attr_max_temp = self._max_temp
        self._attr_target_temperature = (self._min_temp + self._max_temp) // 2
        self._attr_target_temperature_step = 1.0
        self._attr_precision = 1.0
        
        self._attr_fan_mode = self._fan_mode
        self._attr_fan_modes = self._fan_modes
        self._attr_preset_mode = self._preset_mode
        self._attr_preset_modes = self._preset_modes
        self._attr_hvac_modes = self._hvac_modes
        self._attr_hvac_mode = self._hvac_mode
        self._attr_supported_features = self._supported_features
        self._attr_swing_mode = self._swing_mode
        self._attr_swing_modes = self._swing_modes
        
        self._attr_has_entity_name = True
        self._attr_unique_id = slugify(f"{device.mac}_{key}")

        if device.vendor == "Polaris":
            self.entity_id = f"climate.{POLARIS_DEVICE[int(device.devtype)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(device.devtype)]['model'].replace('-', '_').lower()}_{key.replace('-', '_').lower()}"
        if device.vendor == "Rusclimate":
            self.entity_id = f"climate.{HOMMYN_DEVICE[int(device.devtype)]['class'].replace('-', '_').lower()}_{HOMMYN_DEVICE[int(device.devtype)]['model'].replace('-', '_').lower()}_{key.replace('-', '_').lower()}"

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
    def hvac_mode(self) -> Optional[HVACMode]:
        """Возвращает текущий режим HVAC."""
        if not self.available:
            return None
        if not self._coordinator_mode:
            return None
        mode_value = self._get_state_from_coordinator(self._coordinator_mode, None)
        if mode_value is None:
            return None
        val = int.from_bytes(mode_value, "little")
        val_mode = self._attr_hvac_modes[val]
        return val_mode


    @property
    def fan_mode(self) -> Optional[str]:
        """Возвращает текущий режим вентилятора."""
        if not self.available:
            return None
        if not self._coordinator_speed:
            return None
        mode_value = self._get_state_from_coordinator(self._coordinator_speed, None)
        if mode_value is None:
            return None
        val = int.from_bytes(mode_value, "little")
        for mode_name, mode_val in self._fan_modes.items():
            if val == int(mode_val):
                val_mode = mode_name
        return val_mode

    @property
    def preset_mode(self) -> Optional[str]:
        """Возвращает текущий пресет."""
        if not self.available:
            return None
        if not self._coordinator_mode:
            return None
        mode_value = self._get_state_from_coordinator(self._coordinator_mode, None)
        if mode_value is None:
            return None
        val = int.from_bytes(mode_value, "little")
        for mode_name, mode_val in self._preset_modes.items():
            if val == int(mode_val):
                val_mode = mode_name
        return val_mode

    @property
    def swing_mode(self) -> Optional[str]:
        """Возвращает текущий режим качания."""
        if not self.available:
            return None
        if not self._coordinator_mode:
            return None
        mode_value = self._get_state_from_coordinator(self._coordinator_swing, None)
        if mode_value is None:
            return None
        val = int.from_bytes(mode_value, "little")
        for mode_name, mode_val in self._preset_modes.items():
            if val == int(mode_val):
                val_mode = mode_name
        return val_mode

    def _handle_coordinator_update(self) -> None:
        """Вызывается МГНОВЕННО при получении пуша от устройства."""
        new_available = self.available
        if new_available != self._attr_available:
            self._attr_available = new_available
            if not new_available:
                self._attr_hvac_mode = None
                self._attr_target_temperature = None
#                self._attr_target_humidity = None
            self.async_write_ha_state()
            return

        if self.available:
            self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs) -> None:
        """Устанавливает целевую температуру."""
        if not self.available:
            _LOGGER.warning("Нельзя установить температуру на недоступном устройстве %s", self.device.mac)
            return

        temperature = kwargs.get("temperature")
        if temperature is not None:
            temperature = max(self._attr_min_temp, min(self._attr_max_temp, temperature))
            self._attr_target_temperature = temperature
            payload = bytes([int(temperature), 0])
            await self.async_send_command(CMD_TARGET_TEMPERATURE, payload)

        self.schedule_update_ha_state()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Устанавливает режим HVAC."""
        if not self.available:
            _LOGGER.warning("Нельзя установить режим на недоступном устройстве %s", self.device.mac)
            return
        if hvac_mode not in self._hvac_modes:
            _LOGGER.warning("Неизвестный режим HVAC: %s", hvac_mode)
            return

        mode_value = self._hvac_modes.index(hvac_mode)
        payload = bytes([mode_value])
        
        # Если режим не OFF, отправляем температуру
        if mode_value > 0 and self._attr_target_temperature:
            temp_payload = bytes([int(self._attr_target_temperature), 0])
            await self.async_send_command(CMD_TARGET_TEMPERATURE, temp_payload)
        await self.async_send_command(CMD_MODE, payload)
        
        # Обновляем состояние
        self._attr_hvac_mode = hvac_mode
        self.async_write_ha_state()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Устанавливает пресет."""
        if not self.available:
            _LOGGER.warning("Нельзя установить пресет на недоступном устройстве %s", self.device.mac)
            return
        if preset_mode not in self._preset_modes:
            _LOGGER.warning("Неизвестный режим preset: %s", preset_mode)
            return

        preset_value = self._preset_modes[preset_mode]
        payload = bytes([int(preset_value)])
        await self.async_send_command(CMD_MODE, payload)
        # Обновляем состояние
        self._attr_preset_mode = preset_mode
        self.async_write_ha_state()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Устанавливает режим вентилятора."""
        if not self.available:
            _LOGGER.warning("Нельзя установить режим вентилятора на недоступном устройстве %s", self.device.mac)
            return
        if fan_mode not in self._fan_modes:
            _LOGGER.warning("Неизвестный режим fan: %s", fan_mode)
            return

        fan_value = self._fan_modes[fan_mode]
        payload = bytes([int(fan_value)])
        await self.async_send_command(CMD_SPEED, payload)
        # Обновляем состояние
        self._attr_fan_mode = fan_mode
        self.async_write_ha_state()
        
    async def async_set_swing_mode(self, swing_mode: str) -> None:
        """Устанавливает режим качания."""
        if not self.available:
            _LOGGER.warning("Нельзя установить режим качания на недоступном устройстве %s", self.device.mac)
            return
        if swing_mode not in ("off","horizontal","vertical","both"):
            _LOGGER.warning("Неизвестный режим swing: %s", swing_mode)
            return

        match swing_mode:
            case "off": 
                swing_value = bytes([0,0])
            case "horizontal": 
                swing_value = bytes([0,1])
            case "vertical": 
                swing_value = bytes([1,0])
            case "both": 
                swing_value = bytes([1,1])
        payload = bytes([self._program_index, swing_value])                 #Это надо доделать, тут скорее всего еще switches и длина неизвестна
        await self.async_send_command(CMD_PROGRAM_DATA, payload)

        # Обновляем состояние
        self._attr_swing_mode = swing_mode
        self.async_write_ha_state()
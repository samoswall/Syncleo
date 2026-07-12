# number.py
import logging
from typing import Optional
from slugify import slugify

from homeassistant.components.number import NumberEntity

from .const import (
    DOMAIN,
    POLARIS_DEVICE,
    HOMMYN_DEVICE,
    CMD_TARGET_TIME,
    CMD_TARGET_TEMPERATURE,
    CMD_SPEED,
    CMD_TARGET_HUMIDITY,
)
from .entity import SyncleoEntity
from .entity_description import NUMBER_DESCRIPTIONS

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


async def async_setup_entry(hass, entry, async_add_entities):
    """Настройка чисел."""
    coordinator = hass.data[DOMAIN].get(entry.entry_id)

    if not coordinator:
        _LOGGER.warning("Coordinator not found for entry %s", entry.entry_id)
        return

    device = coordinator.device
    entity_config = device.entity_config
    _LOGGER.debug("NUMBER_entity_config %s", entity_config)

    entities = []

    if "number" in entity_config:
        for key in entity_config["number"]:
            if key in NUMBER_DESCRIPTIONS:
                desc = NUMBER_DESCRIPTIONS[key]
                entities.append(SyncleoNumberEntity(coordinator, device, key, desc))

    async_add_entities(entities)


class SyncleoNumberEntity(SyncleoEntity, NumberEntity):
    """Number сущность Syncleo."""

    should_poll = False

    def __init__(self, coordinator, device, key, desc):
        super().__init__(coordinator, device, "number", key, desc)

        self._min_value = getattr(desc, "min_value", 0)
        self._max_value = getattr(desc, "max_value", 100)
        self._step = getattr(desc, "step", 1)
        self._native_unit = getattr(desc, "native_unit_of_measurement", None)
        self._coordinator_state = getattr(desc, "coordinator_state", None)

        self._attr_native_min_value = self._min_value
        self._attr_native_max_value = self._max_value
        self._attr_native_step = self._step
        self._attr_native_unit_of_measurement = self._native_unit
        self._attr_has_entity_name = True
        self._attr_unique_id = slugify(f"{device.mac}_{key}")

        # Инициализируем значение
        self._attr_native_value = self._min_value

        if device.vendor == "Polaris":
            self.entity_id = (
                f"number.{POLARIS_DEVICE[int(device.devtype)]['class'].replace('-', '_').lower()}"
                f"_{POLARIS_DEVICE[int(device.devtype)]['model'].replace('-', '_').lower()}_{key.replace('-', '_').lower()}"
            )
        if device.vendor == "Hommyn":
            self.entity_id = (
                f"number.{HOMMYN_DEVICE[int(device.devtype)]['class'].replace('-', '_').lower()}"
                f"_{HOMMYN_DEVICE[int(device.devtype)]['model'].replace('-', '_').lower()}_{key.replace('-', '_').lower()}"
            )

    @property
    def native_value(self) -> Optional[float]:
        """Возвращает текущее значение."""
        if not self.available:
            return None

        if not self._coordinator_state:
            return self._attr_native_value

        value = self._get_state_from_coordinator(self._coordinator_state, None)
        if value is None:
            return self._attr_native_value

        # Преобразуем байты в число
        if isinstance(value, bytes):
            return int.from_bytes(value, "little")

        return value

    def _handle_coordinator_update(self) -> None:
        """Вызывается МГНОВЕННО при получении пуша от устройства."""
        new_available = self.available
        if new_available != self._attr_available:
            self._attr_available = new_available
            if not new_available:
                self._attr_native_value = None
            self.async_write_ha_state()
            return

        if self.available:
            new_value = self.native_value
            if new_value != self._attr_native_value:
                self._attr_native_value = new_value
                self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Устанавливает значение."""
        if not self.available:
            _LOGGER.warning("Нельзя установить значение на недоступном устройстве %s", self.device.mac)
            return

        value = max(self._min_value, min(self._max_value, value))

        # Определяем команду по ключу
        cmd_map = {
            "cooking_time": CMD_TARGET_TIME,
            "humidifier_intensity": CMD_SPEED,
            "humidity": CMD_TARGET_HUMIDITY,
        }

        cmd = cmd_map.get(self.entity_key, CMD_TARGET_TEMPERATURE)

        # Для температуры используем 2 байта
        if self.entity_key == "cooking_time":
            payload = int(value).to_bytes(2, "little")
        else:
            payload = bytes([int(value)])

        await self.async_send_command(cmd, payload)
        self._attr_native_value = value
        self.async_write_ha_state()
# humidifier.py
import logging
from typing import Optional
from slugify import slugify

from homeassistant.components.humidifier import (
    HumidifierEntity,
    HumidifierEntityFeature,
    HumidifierDeviceClass,
)
from homeassistant.const import PERCENTAGE

from .const import (
    DOMAIN,
    POLARIS_DEVICE,
    HOMMYN_DEVICE,
    CMD_MODE,
    CMD_TARGET_HUMIDITY,
)
from .entity import SyncleoEntity
from .entity_description import (
    HUMIDIFIER_DESCRIPTIONS,
    parse_humidity,
)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


async def async_setup_entry(hass, entry, async_add_entities):
    """Настройка увлажнителей."""
    coordinator = hass.data[DOMAIN].get(entry.entry_id)

    if not coordinator:
        _LOGGER.warning("Coordinator not found for entry %s", entry.entry_id)
        return

    device = coordinator.device
    entity_config = device.entity_config
    _LOGGER.debug("HUMIDIFIER_entity_config %s", entity_config)

    entities = []

    if "humidifier" in entity_config:
        for key in entity_config["humidifier"]:
            _LOGGER.debug("Processing humidifier key: %s", key)
            
            if key in HUMIDIFIER_DESCRIPTIONS:
                desc = HUMIDIFIER_DESCRIPTIONS[key]
                entities.append(SyncleoHumidifierEntity(coordinator, device, key, desc))
                _LOGGER.debug("Added humidifier entity with key: %s", key)
            else:
                _LOGGER.warning("Description not found for humidifier key: %s", key)

    _LOGGER.info("Adding %d humidifier entities", len(entities))
    async_add_entities(entities)


class SyncleoHumidifierEntity(SyncleoEntity, HumidifierEntity):
    """Увлажнитель Syncleo."""

    should_poll = False

    def __init__(self, coordinator, device, key, desc):
        super().__init__(coordinator, device, "humidifier", key, desc)

        self._min_humidity = getattr(desc, "min_humidity", 30)
        self._max_humidity = getattr(desc, "max_humidity", 80)
        self._operation_list = getattr(desc, "operation_list", {})
        self._coordinator_mode = getattr(desc, "coordinator_mode", None)
        self._coordinator_target = getattr(desc, "coordinator_target_humidity", None)
        self._coordinator_current = getattr(desc, "coordinator_current_humidity", None)

        self._attr_min_humidity = self._min_humidity
        self._attr_max_humidity = self._max_humidity
        self._attr_target_humidity = self._min_humidity
        
        # Список доступных режимов (исключаем "off" если он есть, для режимов увлажнения)
        all_modes = list(self._operation_list.keys())
        # Если есть режим "off", убираем его из списка режимов работы
        self._attr_available_modes = [m for m in all_modes if m != "off"]

        # Инициализируем текущую влажность
        self._attr_current_humidity = None
        self._attr_target_humidity = None
        self._attr_mode = None
        self._attr_is_on = False

        # Определяем поддерживаемые функции
        features = HumidifierEntityFeature(0)
        if len(self._operation_list) > 2:
            features |= HumidifierEntityFeature.MODES
        self._attr_supported_features = features

        self._attr_has_entity_name = True
        self._attr_unique_id = slugify(f"{device.mac}_{key}")

        if device.vendor == "Polaris":
            self.entity_id = (
                f"humidifier.{POLARIS_DEVICE[int(device.devtype)]['class'].replace('-', '_').lower()}"
                f"_{POLARIS_DEVICE[int(device.devtype)]['model'].replace('-', '_').lower()}_{key.replace('-', '_').lower()}"
            )
        if device.vendor == "Rusclimate":
            self.entity_id = (
                f"humidifier.{HOMMYN_DEVICE[int(device.devtype)]['class'].replace('-', '_').lower()}"
                f"_{HOMMYN_DEVICE[int(device.devtype)]['model'].replace('-', '_').lower()}_{key.replace('-', '_').lower()}"
            )

        _LOGGER.debug("Created humidifier entity: %s", self.entity_id)
        _LOGGER.debug("Available modes: %s", self._attr_available_modes)

    @property
    def is_on(self) -> bool:
        """Возвращает True если увлажнитель включен."""
        if not self.available:
            return False
        
        if self.mode and self.mode != "off":
            return True
        return False

    @property
    def current_humidity(self) -> Optional[int]:
        """Возвращает текущую влажность."""
        if not self.available:
            return None
        if not self._coordinator_current:
            return None
        return self._get_state_from_coordinator(self._coordinator_current, parse_humidity)

    @property
    def target_humidity(self) -> Optional[int]:
        """Возвращает целевую влажность."""
        if not self.available:
            return None
        if not self._coordinator_target:
            return None
        return self._get_state_from_coordinator(self._coordinator_target, parse_humidity)

    @property
    def mode(self) -> Optional[str]:
        """Возвращает текущий режим."""
        if not self.available:
            return None
        if not self._coordinator_mode:
            return None

        value = self._get_state_from_coordinator(self._coordinator_mode, None)
        if value is None:
            return None

        # Преобразуем значение в int
        if isinstance(value, bytes):
            value = int.from_bytes(value, "little")
        elif isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                return None

        _LOGGER.debug("Current mode value: %d, operation_list: %s", value, self._operation_list)

        # Ищем режим по значению
        for mode_name, mode_val in self._operation_list.items():
            if value == int(mode_val):
                return mode_name

        # Если значение не найдено, но это 0 - значит выключено
        if value == 0:
            return "off"

        return None

    def _handle_coordinator_update(self) -> None:
        """Вызывается МГНОВЕННО при получении пуша от устройства."""
        new_available = self.available
        if new_available != self._attr_available:
            self._attr_available = new_available
            if not new_available:
                self._attr_current_humidity = None
                self._attr_target_humidity = None
                self._attr_mode = None
                self._attr_is_on = False
            self.async_write_ha_state()
            return

        if self.available:
                # Просто вызываем обновление состояния
                self.async_write_ha_state()

    async def async_set_humidity(self, humidity: int) -> None:
        """Устанавливает целевую влажность."""
        if not self.available:
            _LOGGER.warning("Нельзя установить влажность на недоступном устройстве %s", self.device.mac)
            return

        humidity = max(self._min_humidity, min(self._max_humidity, humidity))
        self._attr_target_humidity = humidity
        if self.coordinator.data:
            new_data = dict(self.coordinator.data)
            humid_bytes = humidity.to_bytes(2, 'little')
            new_data["CMD_TARGET_HUMIDITY"] = humid_bytes.hex()
            # Обновляем данные координатора
            self.coordinator.data = new_data
            # Уведомляем подписчиков (включая эту сущность)
            self.coordinator.async_set_updated_data(new_data)
        payload = bytes([int(humidity), 0])
        await self.async_send_command(CMD_TARGET_HUMIDITY, payload)
        self.schedule_update_ha_state()

    async def async_set_mode(self, mode: str) -> None:
        """Устанавливает режим работы."""
        if not self.available:
            _LOGGER.warning("Нельзя установить режим на недоступном устройстве %s", self.device.mac)
            return

        if mode not in self._operation_list:
            _LOGGER.warning("Неизвестный режим: %s", mode)
            return

        mode_value = int(self._operation_list[mode])
        _LOGGER.debug("Setting mode: %s (value: %d)", mode, mode_value)
        payload = bytes([mode_value])
        await self.async_send_command(CMD_MODE, payload)

    async def async_turn_on(self, **kwargs) -> None:
        """Включает увлажнитель."""
        if not self.available:
            _LOGGER.warning("Нельзя включить увлажнитель на недоступном устройстве %s", self.device.mac)
            return

        # Если есть режимы увлажнения (не "off") - устанавливаем первый
        available_modes = [m for m in self._operation_list.keys() if m != "off"]
        if available_modes:
            first_mode = available_modes[0]
            _LOGGER.debug("Turning on with mode: %s", first_mode)
            await self.async_set_mode(first_mode)
        else:
            # Иначе отправляем команду включения (режим 1)
            _LOGGER.debug("Turning on with default mode 1")
            await self.async_send_command(CMD_MODE, b"\x01")

    async def async_turn_off(self, **kwargs) -> None:
        """Выключает увлажнитель."""
        if not self.available:
            _LOGGER.warning("Нельзя выключить увлажнитель на недоступном устройстве %s", self.device.mac)
            return

        # Отправляем команду выключения (режим 0)
        _LOGGER.debug("Turning off")
        await self.async_send_command(CMD_MODE, b"\x00")
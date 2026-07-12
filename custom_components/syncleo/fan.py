import logging
from typing import Optional

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.util.percentage import int_states_in_range, percentage_to_ranged_value, ranged_value_to_percentage

from .const import DOMAIN
from .entity import SyncleoEntity
from .entity_description import FAN_DESCRIPTIONS

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

async def async_setup_entry(hass, entry, async_add_entities):
    """Настройка вентиляторов."""
    device_mac = entry.data["mac"]
    coordinator = hass.data[DOMAIN].get(device_mac)
    
    if not coordinator:
        _LOGGER.warning("Coordinator not found for device %s", device_mac)
        return
    
    device = coordinator.device
    entity_config = device.entity_config
    
    entities = []
    
    if "fan" in entity_config:
        for key in entity_config["fan"]:
            if key in FAN_DESCRIPTIONS:
                desc = FAN_DESCRIPTIONS[key]
                entities.append(SyncleoFanEntity(hass, device, key, desc))
    
    async_add_entities(entities)


class SyncleoFanEntity(SyncleoEntity, FanEntity):
    """Вентилятор Syncleo."""

    def __init__(self, hass, device, key, desc):
        super().__init__(hass, device, "fan", key, desc)
        
        self._speed_list = getattr(desc, 'speed_list', {})
        self._coordinator_mode = getattr(desc, 'coordinator_mode', None)
        self._coordinator_speed = getattr(desc, 'coordinator_speed', None)
        
        # Определяем поддерживаемые функции
        features = FanEntityFeature.SET_SPEED
        if len(self._speed_list) > 1:
            features |= FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
        self._attr_supported_features = features
        
        # Устанавливаем количество скоростей
        self._attr_speed_count = len(self._speed_list) if self._speed_list else 3
        
        _LOGGER.debug("Fan entity created with speed_count: %d", self._attr_speed_count)

    @property
    def is_on(self) -> bool:
        """Возвращает состояние включения."""
        if not self._coordinator_mode:
            return False
        
        value = self._get_state_from_coordinator(self._coordinator_mode, None)
        if value is None:
            return False
        
        # Проверяем, не выключен ли режим
        off_value = self._speed_list.get("off", 0)
        return int.from_bytes(value, 'little') if isinstance(value, bytes) else int(value) != off_value

    @property
    def percentage(self) -> Optional[int]:
        """Возвращает текущую скорость в процентах."""
        if not self._coordinator_speed:
            return None
        
        value = self._get_state_from_coordinator(self._coordinator_speed, None)
        if value is None:
            return None
        
        # Преобразуем значение скорости в процент
        speed = int.from_bytes(value, 'little') if isinstance(value, bytes) else int(value)
        
        # Находим соответствующий процент
        speeds = list(self._speed_list.values())
        if not speeds:
            return 0
        
        # Если есть прямая привязка к процентам
        if speed in speeds:
            index = speeds.index(speed)
            return int((index / (len(speeds) - 1)) * 100) if len(speeds) > 1 else 0
        
        return 0

    async def async_set_percentage(self, percentage: int):
        """Устанавливает скорость в процентах."""
        if percentage == 0:
            await self.async_turn_off()
            return
        
        # Преобразуем процент в значение скорости
        speeds = list(self._speed_list.values())
        if not speeds:
            return
        
        # Находим ближайшую скорость
        index = int((percentage / 100) * (len(speeds) - 1))
        if index >= len(speeds):
            index = len(speeds) - 1
        
        speed_value = speeds[index]
        
        # TODO: Отправить команду установки скорости
        # Команда CMD_SPEED
        pass

    async def async_turn_on(self, percentage: Optional[int] = None, **kwargs):
        """Включает вентилятор."""
        if percentage is not None:
            await self.async_set_percentage(percentage)
        else:
            # Устанавливаем среднюю скорость
            speeds = list(self._speed_list.values())
            if speeds:
                mid_index = len(speeds) // 2
                if mid_index >= len(speeds):
                    mid_index = len(speeds) - 1
                await self.async_set_percentage(int((mid_index / (len(speeds) - 1)) * 100))

    async def async_turn_off(self, **kwargs):
        """Выключает вентилятор."""
        off_value = self._speed_list.get("off", 0)
        # TODO: Отправить команду установки скорости 0
        pass
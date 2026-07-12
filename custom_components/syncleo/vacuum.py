import logging
from typing import Optional

from homeassistant.components.vacuum import (
    ATTR_CLEANED_AREA,
    StateVacuumEntity,
    VacuumActivity,
    VacuumEntityFeature,
)

from .const import DOMAIN
from .entity import SyncleoEntity
from .entity_description import VACUUM_DESCRIPTIONS

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

async def async_setup_entry(hass, entry, async_add_entities):
    """Настройка пылесосов."""
    device_mac = entry.data["mac"]
    coordinator = hass.data[DOMAIN].get(device_mac)
    
    if not coordinator:
        _LOGGER.warning("Coordinator not found for device %s", device_mac)
        return
    
    device = coordinator.device
    entity_config = device.entity_config
    
    entities = []
    
    if "vacuum" in entity_config:
        for key in entity_config["vacuum"]:
            if key in VACUUM_DESCRIPTIONS:
                desc = VACUUM_DESCRIPTIONS[key]
                entities.append(SyncleoVacuumEntity(hass, device, key, desc))
    
    async_add_entities(entities)


class SyncleoVacuumEntity(SyncleoEntity, StateVacuumEntity):
    """Пылесос Syncleo."""

    def __init__(self, hass, device, key, desc):
        super().__init__(hass, device, "vacuum", key, desc)
        
        self._coordinator_mode = getattr(desc, 'coordinator_mode', None)
        self._coordinator_battery = getattr(desc, 'coordinator_battery', None)
        
        # Определяем поддерживаемые функции
        features = (
            VacuumEntityFeature.RETURN_HOME
#            | VacuumEntityFeature.BATTERY
            | VacuumEntityFeature.CLEAN_SPOT
            | VacuumEntityFeature.STOP
#            | VacuumEntityFeature.PAUSE
            | VacuumEntityFeature.START
            | VacuumEntityFeature.LOCATE
            | VacuumEntityFeature.STATE
            | VacuumEntityFeature.SEND_COMMAND
            | VacuumEntityFeature.FAN_SPEED
#            | VacuumEntityFeature.STATUS
            | VacuumEntityFeature.MAP
        )
        self._attr_supported_features = features

    @property
    def state(self) -> Optional[str]:
        """Возвращает текущее состояние."""
        if not self._coordinator_mode:
            return None
        
        value = self._get_state_from_coordinator(self._coordinator_mode, None)
        if value is None:
            return None
        
        # TODO: Преобразовать значение режима в состояние
        return "idle"

    @property
    def battery_level(self) -> Optional[int]:
        """Возвращает уровень заряда батареи."""
        if not self._coordinator_battery:
            return None
        
        from .entity_description import parse_hex_to_int
        return self._get_state_from_coordinator(self._coordinator_battery, parse_hex_to_int)

    async def async_start(self):
        """Запускает уборку."""
        # TODO: Отправить команду запуска
        pass

    async def async_stop(self, **kwargs):
        """Останавливает уборку."""
        # TODO: Отправить команду остановки
        pass

    async def async_pause(self):
        """Приостанавливает уборку."""
        # TODO: Отправить команду паузы
        pass

    async def async_return_to_base(self, **kwargs):
        """Возвращает на базу."""
        # TODO: Отправить команду возврата на базу
        pass
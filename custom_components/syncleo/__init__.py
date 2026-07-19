# __init__.py
import logging

from homeassistant.core import HomeAssistant
#from .debug_helper import async_setup_debug_services
from .const import DOMAIN
from .manager import SyncleoManager
from .coordinator import SyncleoCoordinator

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)
DEBUG_ENABLED = True

PLATFORMS = [
    "sensor",
    "switch",
    "water_heater",
    "humidifier",
    "fan",
    "select",
    "light",
    "number",
    "climate",
    "vacuum"
]

async def async_setup_entry(hass: HomeAssistant, entry) -> bool:
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
        
    if "manager" not in hass.data[DOMAIN]:
        manager = SyncleoManager(hass)
        hass.data[DOMAIN]["manager"] = manager
    else:
        manager = hass.data[DOMAIN]["manager"]

    initial_info = hass.data.get(DOMAIN, {}).pop("pending_zeroconf", None)
    _LOGGER.debug("initial_info zeroconf %s entry.data %s %s %s", initial_info, entry.data["mac"], entry.data["vendor"], entry.data["devtype"])
    manager.add_configured_device(entry.data["mac"], entry.data["token"], entry.data["vendor"], entry.data["devtype"], entry.data["firmware"])
    await manager.async_start(initial_info=initial_info)
 
    device = manager.configured_devices[entry.data["mac"]]
    
    # Создаем координатор и ЗАПУСКАЕМ ПОСТОЯННОЕ ПОДКЛЮЧЕНИЕ
    coordinator = SyncleoCoordinator(hass, device)
    coordinator.start()
    
    # Сохраняем координатор в hass.data по entry_id
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Сохраняем связь entry_id -> mac для быстрого поиска координатора
    if "entry_to_mac" not in hass.data[DOMAIN]:
        hass.data[DOMAIN]["entry_to_mac"] = {}
    hass.data[DOMAIN]["entry_to_mac"][entry.entry_id] = entry.data["mac"]
    
    # Регистрируем платформы
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    
    # Для отладки - регистрируем сервисы
#    if DEBUG_ENABLED:
#        await async_setup_debug_services(hass)
        
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry) -> bool:
    manager = hass.data[DOMAIN].get("manager")
    coordinator = hass.data[DOMAIN].get(entry.entry_id)
    
    # ОСТАНАВЛИВАЕМ СЕССИЮ
    if coordinator:
        await coordinator.async_stop()
        hass.data[DOMAIN].pop(entry.entry_id, None)
        
    # Удаляем связь entry_id -> mac
    if "entry_to_mac" in hass.data[DOMAIN]:
        hass.data[DOMAIN]["entry_to_mac"].pop(entry.entry_id, None)

    if manager:
        manager.remove_configured_device(entry.data["mac"])
        
        if not manager.configured_devices:
            await manager.async_stop()
            hass.data.pop(DOMAIN)
    
    # Выгружаем платформы
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    return True

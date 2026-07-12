# entity.py
import logging
from typing import Any, Dict, Optional

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from slugify import slugify

from .const import DOMAIN
from .device import SyncleoDevice

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

class SyncleoEntity(CoordinatorEntity):
    """Базовый класс для всех сущностей Syncleo."""

    def __init__(
        self,
        coordinator,
        device: SyncleoDevice,
        platform: str,
        entity_key: str,
        description
    ):
        super().__init__(coordinator)
        self.device = device
        self.platform = platform
        self.entity_key = entity_key
        self.description = description
        
        # Генерация уникального ID
        slug = slugify(f"{device.mac}_{platform}_{entity_key}")
        self._attr_unique_id = slug
        
        # Генерация entity_id
        device_slug = slugify(device.mac)
        entity_slug = slugify(entity_key)
        self.entity_id = f"{DOMAIN}.{device_slug}_{entity_slug}"
        
        # Устанавливаем has_entity_name
        self._attr_has_entity_name = True
        
        # Копируем атрибуты из описания
        if hasattr(description, 'translation_key'):
            self._attr_translation_key = description.translation_key
        
        if hasattr(description, 'entity_category') and description.entity_category:
            self._attr_entity_category = description.entity_category
        
        if hasattr(description, 'icon') and description.icon:
            self._attr_icon = description.icon
        
        # Инициализируем доступность
        self._attr_available = False
        
        _LOGGER.debug(
            "Created entity: %s (%s)", 
            self._attr_unique_id, 
            self.entity_id
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Возвращает информацию об устройстве."""
        return self.device.device_info

    @property
    def available(self) -> bool:
        """Доступность на основе данных координатора (мгновенно)."""
        if not self.coordinator or not self.coordinator.data:
            return False
        return self.coordinator.data.get("available", False)

    def _handle_coordinator_update(self) -> None:
        """Обработка обновления от координатора - переопределяется в наследниках."""
        # Обновляем доступность
        new_available = self.available
        if new_available != self._attr_available:
            self._attr_available = new_available
            self.async_write_ha_state()
        else:
            # Если доступность не изменилась, но могут измениться другие данные
            self.async_write_ha_state()

    def _get_state_from_coordinator(self, state_key: str, func=None) -> Any:
        """Берет состояние напрямую из кэша координатора (без задержек)."""
        if not self.coordinator.data:
            return None
        
        # Проверяем доступность
        if not self.coordinator.data.get("available", False):
            return None
        
        value = self.coordinator.data.get(state_key)
        if value is None:
            return None
        
        # Координатор хранит hex-строки. Вашим функциям парсинга нужны байты.
        if isinstance(value, str):
            try:
                value = bytes.fromhex(value)
            except ValueError:
                return None
        
        if func:
            return func(value)
        return value

    async def async_send_command(self, cmd: int, payload: bytes = b'') -> bool:
        """Отправляет команду устройству через координатор."""
        if not self.available:
            _LOGGER.warning("Попытка отправить команду на недоступное устройство %s", self.device.mac)
            return False
            
        if hasattr(self.coordinator, 'async_send_command'):
            return await self.coordinator.async_send_command(cmd, payload)
        _LOGGER.error("Координатор не поддерживает отправку команд")
        return False
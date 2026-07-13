from dataclasses import dataclass, field
from typing import Optional, Dict, List
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN, POLARIS_DEVICE, HOMMYN_DEVICE
from .device_configs import POLARIS_DEVICE_CONFIGS, HOMMYN_DEVICE_CONFIGS, DEFAULT_CONFIGS

@dataclass
class SyncleoDevice:
    """Представляет устройство Syncleo."""
    mac: str
    name: str
    ip: str
    port: int
    public_key: str
    vendor: str
    basetype: str
    devtype: str
    firmware: str
    protocol: str
    
    # Поля для настроенного устройства
    token: Optional[str] = None
    available: bool = True
    
    # Скрытое поле для счетчика ошибок доступности
    _fail_count: int = field(default=0, init=False, repr=False)
    
    # Флаг того, что координатор удерживает постоянную сессию
    is_coordinator_connected: bool = False
    
    # Кэш для конфигурации сущностей
    _entity_config: Optional[Dict[str, List[str]]] = field(default=None, init=False, repr=False)

    @property
    def id(self) -> str:
        """Уникальный идентификатор устройства (MAC адрес)."""
        return self.mac

    @property
    def device_type_class(self) -> str:
        """Возвращает класс устройства."""
        if self.vendor == "Polaris" and self.devtype and self.devtype.isdigit():
            dev_id = int(self.devtype)
            if dev_id in POLARIS_DEVICE:
                return POLARIS_DEVICE[dev_id]["class"]
        elif self.vendor == "Rusclimate" and self.devtype and self.devtype.isdigit():
            dev_id = int(self.devtype)
            if dev_id in HOMMYN_DEVICE:
                return HOMMYN_DEVICE[dev_id]["class"]
        return "unknown"
    
    @property
    def device_model(self) -> str:
        """Возвращает модель устройства."""
        if self.vendor == "Polaris" and self.devtype and self.devtype.isdigit():
            dev_id = int(self.devtype)
            if dev_id in POLARIS_DEVICE:
                return POLARIS_DEVICE[dev_id]["model"]
        elif self.vendor == "Rusclimate" and self.devtype and self.devtype.isdigit():
            dev_id = int(self.devtype)
            if dev_id in HOMMYN_DEVICE:
                return HOMMYN_DEVICE[dev_id]["model"]
        return "Unknown"

    @property
    def device_info(self) -> DeviceInfo:
        """Возвращает информацию об устройстве для Home Assistant."""
        return DeviceInfo(
            name=f"{self.vendor} {self.device_model}" if self.device_model != "Unknown" else self.name,
            identifiers={(DOMAIN, self.mac)},
            manufacturer=self.vendor,
            model=self.device_model,
            sw_version=self.firmware,
        )

    @property
    def entity_config(self) -> Dict[str, List[str]]:
        """Возвращает конфигурацию сущностей для устройства."""
        if self._entity_config is not None:
            return self._entity_config
        
        config = {}
        
        # Проверяем конкретную конфигурацию устройства
        if self.vendor == "Polaris" and self.devtype and self.devtype.isdigit():
            dev_id = int(self.devtype)
            if dev_id in POLARIS_DEVICE_CONFIGS:
                config = POLARIS_DEVICE_CONFIGS[dev_id]
        
        elif self.vendor == "Rusclimate" and self.devtype and self.devtype.isdigit():
            dev_id = int(self.devtype)
            if dev_id in HOMMYN_DEVICE_CONFIGS:
                config = HOMMYN_DEVICE_CONFIGS[dev_id]
        
        # Если нет конкретной конфигурации, используем по типу
        if not config:
            device_type = self.device_type_class
            if device_type in DEFAULT_CONFIGS:
                config = DEFAULT_CONFIGS[device_type]
            else:
                config = DEFAULT_CONFIGS["default"]
        
        self._entity_config = config
        return config
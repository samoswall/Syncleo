# light.py
import logging
from typing import Optional
from slugify import slugify

from homeassistant.components.light import LightEntity, ColorMode, LightEntityFeature, ATTR_BRIGHTNESS, ATTR_RGB_COLOR

from .const import DOMAIN, POLARIS_DEVICE, HOMMYN_DEVICE, CMD_NIGHT, CMD_PROGRAM_DATA
from .entity import SyncleoEntity
from .entity_description import LIGHT_DESCRIPTIONS

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

async def async_setup_entry(hass, entry, async_add_entities):
    """Настройка света."""
    device_mac = entry.data["mac"]
    coordinator = hass.data[DOMAIN].get(entry.entry_id)
    
    if not coordinator:
        _LOGGER.warning("Coordinator not found for entry %s", entry.entry_id)
        return
    
    device = coordinator.device
    entity_config = device.entity_config
    
    entities = []
    
    if "light" in entity_config:
        for key in entity_config["light"]:
            if key in LIGHT_DESCRIPTIONS:
                desc = LIGHT_DESCRIPTIONS[key]
                entities.append(SyncleoLightEntity(coordinator, device, key, desc))
    
    async_add_entities(entities)


class SyncleoLightEntity(SyncleoEntity, LightEntity):
    """Свет Syncleo."""
    should_poll = False
    
    def __init__(self, coordinator, device, key, desc):
        super().__init__(coordinator, device, "light", key, desc)
        
        self._coordinator_state = getattr(desc, 'coordinator_state', None)
        self._coordinator_color = getattr(desc, 'coordinator_color', None)
        self._program_index = getattr(desc, 'program_index', "0")
        self._func = getattr(desc, 'func', None)
        
        # Кэш для текущего цвета, чтобы не парсить дважды (для RGB и Brightness)
        self._current_rgb: Optional[tuple] = None
        
        self._attr_color_mode = ColorMode.RGB
        self._attr_supported_color_modes = {ColorMode.RGB}
        self._attr_is_on = False
        self._attr_brightness = 255
            
        if device.vendor == 'Polaris':
            self.entity_id = f"light.{POLARIS_DEVICE[int(device.devtype)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(device.devtype)]['model'].replace('-', '_').lower()}_{key.replace('-', '_').lower()}"
        elif device.vendor == 'Rusclimate':
            self.entity_id = f"light.{HOMMYN_DEVICE[int(device.devtype)]['class'].replace('-', '_').lower()}_{HOMMYN_DEVICE[int(device.devtype)]['model'].replace('-', '_').lower()}_{key.replace('-', '_').lower()}"

    @property
    def is_on(self) -> bool:
        """Возвращает состояние включения."""
        # Если устройство недоступно, возвращаем False
        if not self.available:
            return False
            
        if not self._coordinator_state:
            return False
        
        value = self._get_state_from_coordinator(self._coordinator_state, None)
        if value is None:
            return False
        if isinstance(value, bytes):
            return value[0] == 1
        return bool(value)

    @property
    def rgb_color(self) -> Optional[tuple]:
        """Возвращает ИСТИННЫЙ RGB цвет (нормализованный к 100% яркости для HA)."""
        # Если устройство недоступно, возвращаем None
        if not self.available:
            return None
            
        if not self._coordinator_color:
            return None
        
        parsed = None

        if self._coordinator_color == "CMD_PROGRAM_DATA":
            if not self.coordinator.data:
                return None
                
            program_data = self.coordinator.data.get("CMD_PROGRAM_DATA", {})
            color_hex = program_data.get(self._program_index)
            
            if not color_hex:
                return None
                
            try:
                color_bytes = bytes.fromhex(color_hex)
            except ValueError:
                return None
                
            if self._func:
                parsed = self._func(color_bytes)
        else:
            parsed = self._get_state_from_coordinator(self._coordinator_color, self._func)

        if parsed and isinstance(parsed, dict):
            raw_r = parsed.get('r', 0)
            raw_g = parsed.get('g', 0)
            raw_b = parsed.get('b', 0)
            
            # Вычисляем яркость по максимальному каналу
            max_channel = max(raw_r, raw_g, raw_b)
            
            if max_channel == 0:
                # Цвет черный - яркость 0, истинный цвет (0,0,0)
                self._attr_brightness = 0
                self._current_rgb = (0, 0, 0)
            else:
                # Яркость для ползунка HA (0-255)
                self._attr_brightness = max_channel
                
                # МАГИЯ: Вычисляем "истинный" цвет.
                # Если пришел 128,0,0 (тусклый красный), а яркость 128...
                # То истинный цвет 255,0,0. Делим на коэффициент.
                factor = 255.0 / max_channel
                self._current_rgb = (
                    min(255, int(raw_r * factor)),
                    min(255, int(raw_g * factor)),
                    min(255, int(raw_b * factor))
                )
            
            return self._current_rgb
            
        self._current_rgb = None
        return None

    @property
    def brightness(self) -> Optional[int]:
        """Возвращает яркость, вычисленную в rgb_color."""
        return self._attr_brightness

    def _handle_coordinator_update(self) -> None:
        """Мгновенное обновление при пуше."""
        # Обновляем доступность
        new_available = self.available
        if new_available != self._attr_available:
            self._attr_available = new_available
            if not new_available:
                # Если устройство недоступно, выключаем свет
                self._attr_is_on = False
                self._attr_brightness = 0
                self._current_rgb = None
            self.async_write_ha_state()
            return
        
        # Обновляем значения только если устройство доступно
        if self.available:
            # Сохраняем старые значения для проверки
            old_is_on = self._attr_is_on
            old_rgb = self._current_rgb
            old_brightness = self._attr_brightness

            # Считываем новые (это обновит self._current_rgb внутри свойств)
            new_is_on = self.is_on
            new_rgb = self.rgb_color
            new_brightness = self.brightness

            # Если что-то изменилось - пушим в UI
            if old_is_on != new_is_on or old_rgb != new_rgb or old_brightness != new_brightness:
                self._attr_is_on = new_is_on
                self._attr_brightness = new_brightness
                self.async_write_ha_state()

    async def async_turn_on(self, **kwargs) -> None:
        """Включает свет, устанавливает цвет и/или яркость."""
        if not self.available:
            _LOGGER.warning("Нельзя включить свет на недоступном устройстве %s", self.device.mac)
            return
            
        # 1. Определяем целевой цвет
        # Если передали конкретный цвет - берем его. Иначе берем текущий. Иначе белый.
        rgb = kwargs.get("rgb_color")
        target_rgb = rgb if rgb else self._current_rgb or (255, 255, 255)
        
        # 2. ИСПРАВЛЕНО: Правильно определяем яркость!
        # Если HA передала яркость - используем её.
        # Если HA передал ТОЛЬКО цвет - берем ТЕКУЩУЮ яркость из состояния сущности,
        # чтобы ползунок не прыгал на 100% при смене цвета!
        brightness = kwargs.get("brightness")
        if brightness is None:
            brightness = self._attr_brightness
            
        # Если яркость всё ещё не определена (например, первый запуск), считаем что 100%
        if brightness is None:
            brightness = 255
            
        # 3. Применяем яркость (HA передает ее от 0 до 255)
        factor = brightness / 255.0
        target_rgb = tuple(int(c * factor) for c in target_rgb)
            
        # 4. Отправляем команду включения (если есть привязанная команда состояния)
        if self._coordinator_state:
            await self.async_send_command(CMD_NIGHT, b'\x01')

        # 5. Отправляем RGB цвет
        if self._coordinator_color:
            # Формируем пакет: [индекс, R, G, B]
            index = int(self._program_index)
            payload = bytes([index, target_rgb[0], target_rgb[1], target_rgb[2]])
            await self.async_send_command(CMD_PROGRAM_DATA, payload)

    async def async_turn_off(self, **kwargs) -> None:
        """Выключает свет."""
        if not self.available:
            _LOGGER.warning("Нельзя выключить свет на недоступном устройстве %s", self.device.mac)
            return
            
        # 1. Отправляем команду выключения состояния
        if self._coordinator_state:
            await self.async_send_command(CMD_NIGHT, b'\x00')

    async def async_set_rgb_color(self, rgb: tuple) -> None:
        """Устанавливает RGB цвет (вызывается HA в некоторых старых версиях UI)."""
        # Просто делегируем в async_turn_on, передавая цвет
        await self.async_turn_on(rgb_color=rgb)
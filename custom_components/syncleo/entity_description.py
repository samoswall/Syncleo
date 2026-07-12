from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, List
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.humidifier import HumidifierEntity, HumidifierEntityDescription, HumidifierDeviceClass
from homeassistant.const import (
    EntityCategory,
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfMass,
    SIGNAL_STRENGTH_DECIBELS,
    CONCENTRATION_PARTS_PER_MILLION,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    UnitOfTime,
    UnitOfVolume,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfArea,
)
from homeassistant.helpers.entity import EntityDescription

# ============= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =============

def parse_temp(data: bytes) -> float:
    """Парсинг температуры из байтов."""
    if len(data) >= 2:
        return int.from_bytes(data[:2], 'little') 
    return 0.0

def parse_hex_to_int(data: bytes) -> int:
    """Парсинг hex в десятичное число."""
    if data:
        return int.from_bytes(data, 'little')
    return 0

def parse_hex_to_bool(data: bytes) -> bool:
    """Парсинг hex в булево значение."""
    if data:
        return data[0] > 0
    return False

def parse_color(data: bytes) -> Dict[str, int]:
    """Парсинг цвета из байтов."""
    if len(data) >= 3:
        return {"r": data[0], "g": data[1], "b": data[2]}
    return {"r": 0, "g": 0, "b": 0}

def parse_humidity(data: bytes) -> int:
    """Парсинг влажности."""
    if data:
        return int.from_bytes(data, 'little')
    return 0

def parse_speed(data: bytes) -> int:
    """Парсинг скорости."""
    if data:
        return data[0]
    return 0

def parse_power(data: bytes) -> int:
    """Парсинг мощности."""
    if len(data) >= 2:
        return int.from_bytes(data[:2], 'little')
    return 0

def parse_weight(data: bytes) -> float:
    """Парсинг веса."""
    if len(data) >= 2:
        return int.from_bytes(data[:2], 'little') / 100.0
    return 0.0

def parse_time(data: bytes) -> int:
    """Парсинг времени в минутах."""
    if data:
        return int.from_bytes(data, 'little')
    return 0

# ============= Entity Description =============

@dataclass(frozen=True)
class SyncleoEntityDescription(EntityDescription):
    """Базовое описание сущности Syncleo."""
    coordinator_state: Optional[str] = None
    func: Optional[Callable] = None
    entity_category: Optional[EntityCategory] = None

    
# ---------- WATER HEATER ----------
@dataclass(frozen=True)
class SyncleoWaterHeaterDescription(SyncleoEntityDescription):
    """Описание для водонагревателя/чайника."""
    min_temp: int = 30
    max_temp: int = 100
    operation_list: Dict[str, str] = field(default_factory=dict)
    coordinator_mode: Optional[str] = None
    coordinator_target_temperature: Optional[str] = None
    coordinator_current_temperature: Optional[str] = None


WATER_HEATER_DESCRIPTIONS = {
    "kettle": SyncleoWaterHeaterDescription(
        key="kettle",
        translation_key="kettle",
        name="Kettle",
        min_temp=30,
        max_temp=100,
        operation_list={"off":"0","performance":"1","electric":"3","heat_pump":"4","eco":"5"},
        coordinator_mode="CMD_MODE",
        coordinator_target_temperature="CMD_TARGET_TEMPERATURE",
        coordinator_current_temperature="CMD_CURRENT_TEMPERATURE",
        icon="mdi:kettle"
    ),
    "kettle_with_tea_time": SyncleoWaterHeaterDescription(
        key="kettle_with_tea_time",
        translation_key="kettle",
        name="Kettle",
        min_temp=30,
        max_temp=100,
        operation_list={"off":"0","performance":"1","electric":"3","heat_pump":"4","eco": "5","gas": "6"},
        coordinator_mode="CMD_MODE",
        coordinator_target_temperature="CMD_TARGET_TEMPERATURE",
        coordinator_current_temperature="CMD_CURRENT_TEMPERATURE",
        icon="mdi:kettle"
    ),
    "kettle_with_tea_time_keep_with_warm": SyncleoWaterHeaterDescription(
        key="kettle_with_tea_time_keep_with_warm",
        translation_key="kettle",
        name="Kettle",
        min_temp=30,
        max_temp=100,
        operation_list={"off":"0","performance":"1","high_demand":"2","electric":"3","heat_pump":"4","eco":"5","gas":"6"},
        coordinator_mode="CMD_MODE",
        coordinator_target_temperature="CMD_TARGET_TEMPERATURE",
        coordinator_current_temperature="CMD_CURRENT_TEMPERATURE",
        icon="mdi:kettle"
    ),

}


# ---------- HUMIDIFIER ----------
@dataclass(frozen=True)
class SyncleoHumidifierDescription(SyncleoEntityDescription):
    """Описание для увлажнителя."""
    device_class: Optional[HumidifierDeviceClass] = None
    min_humidity: int = 30
    max_humidity: int = 80
    operation_list: Dict[str, str] = field(default_factory=dict)
    coordinator_mode: Optional[str] = None
    coordinator_target_humidity: Optional[str] = None
    coordinator_current_humidity: Optional[str] = None


HUMIDIFIER_DESCRIPTIONS = {
    "humidifier_1_mode": SyncleoHumidifierDescription(
        key="humidifier_1_mode",
        translation_key="humidifier",
        name="Humidifier",
        min_humidity=30,
        max_humidity=80,
        operation_list={"boost": "5"},
        coordinator_mode="CMD_MODE",
        coordinator_target_humidity="CMD_TARGET_HUMIDITY",
        coordinator_current_humidity="CMD_CURRENT_HUMIDITY",
        device_class=HumidifierDeviceClass.HUMIDIFIER,
        icon="mdi:air-humidifier",
    ),
    "humidifier_2_mode": SyncleoHumidifierDescription(
        key="humidifier_2_mode",
        translation_key="humidifier",
        name="Humidifier",
        min_humidity=30,
        max_humidity=80,
        operation_list={"home": "1", "auto": "2"},
        coordinator_mode="CMD_MODE",
        coordinator_target_humidity="CMD_TARGET_HUMIDITY",
        coordinator_current_humidity="CMD_CURRENT_HUMIDITY",
        device_class=HumidifierDeviceClass.HUMIDIFIER,
        icon="mdi:air-humidifier",
    ),
    "humidifier_3A_mode": SyncleoHumidifierDescription(
        key="humidifier_3A_mode",
        translation_key="humidifier",
        name="Humidifier",
        min_humidity=30,
        max_humidity=80,
        operation_list={"boost": "5", "home": "6", "eco": "7"},
        coordinator_mode="CMD_MODE",
        coordinator_target_humidity="CMD_TARGET_HUMIDITY",
        coordinator_current_humidity="CMD_CURRENT_HUMIDITY",
        device_class=HumidifierDeviceClass.HUMIDIFIER,
        icon="mdi:air-humidifier",
    ),
    "humidifier_3B_mode": SyncleoHumidifierDescription(
        key="humidifier_3B_mode",
        translation_key="humidifier",
        name="Humidifier",
        min_humidity=30,
        max_humidity=80,
        operation_list={"auto": "1", "boost": "5", "eco": "7"},
        coordinator_mode="CMD_MODE",
        coordinator_target_humidity="CMD_TARGET_HUMIDITY",
        coordinator_current_humidity="CMD_CURRENT_HUMIDITY",
        device_class=HumidifierDeviceClass.HUMIDIFIER,
        icon="mdi:air-humidifier",
    ),
    "humidifier_4_mode": SyncleoHumidifierDescription(
        key="humidifier_4_mode",
        translation_key="humidifier",
        name="Humidifier",
        min_humidity=30,
        max_humidity=80,
        operation_list={"auto": "1", "boost": "5", "home": "6", "eco": "7"},
        coordinator_mode="CMD_MODE",
        coordinator_target_humidity="CMD_TARGET_HUMIDITY",
        coordinator_current_humidity="CMD_CURRENT_HUMIDITY",
        device_class=HumidifierDeviceClass.HUMIDIFIER,
        icon="mdi:air-humidifier",
    ),
    "humidifier_5A_mode": SyncleoHumidifierDescription(
        key="humidifier_5A_mode",
        translation_key="humidifier",
        name="Humidifier",
        min_humidity=30,
        max_humidity=80,
        operation_list={"auto": "1", "comfort": "2", "baby": "3", "sleep": "4", "boost": "5"},
        coordinator_mode="CMD_MODE",
        coordinator_target_humidity="CMD_TARGET_HUMIDITY",
        coordinator_current_humidity="CMD_CURRENT_HUMIDITY",
        device_class=HumidifierDeviceClass.HUMIDIFIER,
        icon="mdi:air-humidifier",
    ),
    "humidifier_5B_mode": SyncleoHumidifierDescription(
        key="humidifier_5B_mode",
        translation_key="humidifier",
        name="Humidifier",
        min_humidity=30,
        max_humidity=80,
        operation_list={"auto": "1", "sleep": "4", "boost": "5", "home": "6", "eco": "7"},
        coordinator_mode="CMD_MODE",
        coordinator_target_humidity="CMD_TARGET_HUMIDITY",
        coordinator_current_humidity="CMD_CURRENT_HUMIDITY",
        device_class=HumidifierDeviceClass.HUMIDIFIER,
        icon="mdi:air-humidifier",
    ),
    "humidifier_7_mode": SyncleoHumidifierDescription(
        key="humidifier_7_mode",
        translation_key="humidifier",
        name="Humidifier",
        min_humidity=30,
        max_humidity=80,
        operation_list={"off": "0", "auto": "1", "comfort": "2", "baby": "3", "sleep": "4", "boost": "5", "home": "6", "eco": "7"},
        coordinator_mode="CMD_MODE",
        coordinator_target_humidity="CMD_TARGET_HUMIDITY",
        coordinator_current_humidity="CMD_CURRENT_HUMIDITY",
        device_class=HumidifierDeviceClass.HUMIDIFIER,
        icon="mdi:air-humidifier",
    ),
    "humidifier_11_mode": SyncleoHumidifierDescription(
        key="humidifier_11_mode",
        translation_key="humidifier",
        name="Humidifier",
        min_humidity=30,
        max_humidity=80,
        operation_list={"home": "1", "auto": "2", "sleep": "3", "baby": "4", "comfort": "5", "fitnes": "6", "yoga": "7", "meditation": "8", "prana_hand": "9", "prana_auto": "10", "aroma": "11"},
        coordinator_mode="CMD_MODE",
        coordinator_target_humidity="CMD_TARGET_HUMIDITY",
        coordinator_current_humidity="CMD_CURRENT_HUMIDITY",
        device_class=HumidifierDeviceClass.HUMIDIFIER,
        icon="mdi:air-humidifier",
    ),
    
}


# ---------- FAN ----------
@dataclass(frozen=True)
class SyncleoFanDescription(SyncleoEntityDescription):
    """Описание для вентилятора."""
    speed_list: Dict[str, int] = field(default_factory=dict)
    coordinator_mode: Optional[str] = None
    coordinator_speed: Optional[str] = None


FAN_DESCRIPTIONS = {
    "air_cleaner": SyncleoFanDescription(
        translation_key="air_cleaner",
        key="air_cleaner",
        name="Air Cleaner",
        speed_list={
            "off": 0,
            "silent": 1,
            "low": 2,
            "medium": 3,
            "high": 4,
            "turbo": 5
        },
        coordinator_mode="CMD_MODE",
        coordinator_speed="CMD_SPEED",
        icon="mdi:air-purifier"
    ),
    "fan": SyncleoFanDescription(
        translation_key="fan",
        key="fan",
        name="Fan",
        speed_list={
            "off": 0,
            "low": 1,
            "medium": 2,
            "high": 3,
            "turbo": 4
        },
        coordinator_mode="CMD_MODE",
        coordinator_speed="CMD_SPEED",
        icon="mdi:fan"
    ),
}


# ---------- SWITCH ----------
@dataclass(frozen=True)
class SyncleoSwitchDescription(SyncleoEntityDescription):
    """Описание для переключателя."""
    entity_category: Optional[EntityCategory] = EntityCategory.CONFIG


SWITCH_DESCRIPTIONS = {
    "power": SyncleoSwitchDescription(
        translation_key="power_switch",
        key="power",
        coordinator_state="CMD_MODE",
        func=parse_hex_to_bool,
        icon="mdi:power",
        entity_category=None
    ),
    "sound": SyncleoSwitchDescription(
        translation_key="sound_switch",
        key="sound",
        coordinator_state="CMD_VOLUME",
        func=parse_hex_to_bool,
        icon="mdi:volume-high",
        entity_category=EntityCategory.CONFIG
    ),
    "child_lock": SyncleoSwitchDescription(
        translation_key="child_lock_switch",
        key="child_lock",
        coordinator_state="CMD_CHILD_LOCK",
        func=parse_hex_to_bool,
        icon="mdi:lock",
        entity_category=EntityCategory.CONFIG
    ),
    "backlight": SyncleoSwitchDescription(
        translation_key="backlight_switch",
        key="backlight",
        coordinator_state="CMD_BACKLIGHT",
        func=parse_hex_to_bool,
        icon="mdi:lightbulb",
        entity_category=EntityCategory.CONFIG
    ),
    "ionization": SyncleoSwitchDescription(
        translation_key="ionization_switch",
        key="ionization",
        coordinator_state="CMD_IONIZATION",
        func=parse_hex_to_bool,
        icon="mdi:atom-variant",
        entity_category=EntityCategory.CONFIG
    ),
    "turbo": SyncleoSwitchDescription(
        translation_key="turbo_switch",
        key="turbo",
        coordinator_state="CMD_TURBO",
        func=parse_hex_to_bool,
        icon="mdi:fan-speed-2",
        entity_category=EntityCategory.CONFIG
    ),
    "warmstream": SyncleoSwitchDescription(
        translation_key="warmstream_switch",
        key="warmstream",
        coordinator_state="CMD_WARMSTREAM",
        func=parse_hex_to_bool,
        icon="mdi:heat-wave",
        entity_category=EntityCategory.CONFIG
    ),
    "night": SyncleoSwitchDescription(
        translation_key="night_mode_switch",
        key="night_mode",
        coordinator_state="CMD_NIGHT",
        func=parse_hex_to_bool,
        icon="mdi:weather-night",
        entity_category=EntityCategory.CONFIG
    ),
    "smart_mode": SyncleoSwitchDescription(
        translation_key="smart_mode_switch",
        key="smart_mode",
        coordinator_state="CMD_SMART_MODE",
        func=parse_hex_to_bool,
        icon="mdi:brain",
        entity_category=EntityCategory.CONFIG
    ),
}


# ---------- SENSOR ----------
@dataclass(frozen=True)
class SyncleoSensorDescription(SyncleoEntityDescription):
    """Описание для сенсора."""
    device_class: Optional[SensorDeviceClass] = None
    native_unit_of_measurement: Optional[str] = None
    state_class: Optional[SensorStateClass] = None


SENSOR_DESCRIPTIONS = {
    "temperature": SyncleoSensorDescription(
        key="temperature",
        translation_key="temperature_sensor",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        coordinator_state="CMD_CURRENT_TEMPERATURE",
        func=parse_temp,
        icon="mdi:thermometer"
    ),
    "humidity": SyncleoSensorDescription(
        translation_key="humidity_sensor",
        key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        coordinator_state="CMD_CURRENT_HUMIDITY",
        func=parse_humidity,
        icon="mdi:water-percent"
    ),
    "current_power": SyncleoSensorDescription(
        translation_key="current_power",
        key="current_power",
        device_class=None,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        coordinator_state="CMD_CURRENT_POWER",
        func=parse_power,
        icon="mdi:flash"
    ),
    "speed": SyncleoSensorDescription(
        translation_key="speed_sensor",
        key="speed_sensor",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        coordinator_state="CMD_SPEED",
        func=parse_speed,
        icon="mdi:speedometer"
    ),
    "weight": SyncleoSensorDescription(
        translation_key="weight_sensor",
        key="weight",
        device_class=SensorDeviceClass.WEIGHT,
        native_unit_of_measurement=UnitOfMass.GRAMS,
        state_class=SensorStateClass.MEASUREMENT,
        coordinator_state="CMD_WEIGHT",
        func=parse_weight,
        icon="mdi:weight-gram"
    ),
    "error": SyncleoSensorDescription(
        translation_key="error",
        key="error",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=None,
        coordinator_state="CMD_ERROR",
        func=parse_hex_to_int,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:alert"
    ),
    "filter_retain": SyncleoSensorDescription(
        translation_key="filter_retain_sensor",
        key="filter_retain",
        device_class=None,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.MEASUREMENT,
        coordinator_state="CMD_EXPENDABLES",
        func=parse_hex_to_int,
        icon="mdi:filter"
    ),
    "clean_retain": SyncleoSensorDescription(
        translation_key="clean_retain_sensor",
        key="clean_retain",
        device_class=None,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.MEASUREMENT,
        coordinator_state="CMD_EXPENDABLES",
        func=parse_hex_to_int,
        icon="mdi:cup-water"
    ),
    "firmware": SyncleoSensorDescription(
        translation_key="firmware_version_sensor",
        key="firmware_version",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:information-outline"
    ),
    "device_type": SyncleoSensorDescription(
        translation_key="device_type_sensor",
        key="device_type",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:devices"
    ),
}


# ---------- SELECT ----------
@dataclass(frozen=True)
class SyncleoSelectDescription(SyncleoEntityDescription):
    """Описание для селекта."""
    options: Dict[str, int] = field(default_factory=dict)
    coordinator_mode: Optional[str] = None
    coordinator_target_temperature: Optional[str] = None


SELECT_DESCRIPTIONS = {
    "select_tea_kettle": SyncleoSelectDescription(
        translation_key="select_tea_kettle",
        key="select_tea_kettle",
        options={
            "not_selected": 0,
            "black_tea": 100,
            "baby_bottle": 40,
            "instant_coffee": 95,
            "green_tea": 80,
            "flower_tea": 80,
            "tea_bag": 100,
            "red_tea": 90,
            "puerh_tea": 95,
            "oolong_tea": 90,
            "white_tea": 65,
            "herbal_tea": 90
        },
        coordinator_mode="CMD_MODE",
        coordinator_target_temperature="CMD_TARGET_TEMPERATURE",
        entity_category=EntityCategory.CONFIG,
        icon="mdi:tea"
    ),
    "mode": SyncleoSelectDescription(
        translation_key="mode",
        key="mode",
        options={
            "auto": 1,
            "manual": 2,
            "sleep": 3,
            "turbo": 4
        },
        coordinator_mode="CMD_MODE",
        entity_category=EntityCategory.CONFIG,
        icon="mdi:format-list-bulleted"
    ),
    "speed": SyncleoSelectDescription(
        translation_key="speed",
        key="speed",
        options={
            "low": 1,
            "medium": 2,
            "high": 3,
            "turbo": 4
        },
        coordinator_mode="CMD_SPEED",
        entity_category=EntityCategory.CONFIG,
        icon="mdi:speedometer"
    ),
}


# ---------- LIGHT ----------
@dataclass(frozen=True)
class SyncleoLightDescription(SyncleoEntityDescription):
    """Описание для света."""
    coordinator_color: Optional[str] = None
    program_index: str = "0"

LIGHT_DESCRIPTIONS = {
    "night_light": SyncleoLightDescription(
        translation_key="night_light",
        key="night_light",
        coordinator_state="CMD_NIGHT",
        coordinator_color="CMD_PROGRAM_DATA",
        program_index="0",
        func=parse_color,
        entity_category=EntityCategory.CONFIG,
        icon="mdi:weather-night"
    ),
    "backlight": SyncleoLightDescription(
        translation_key="backlight",
        key="backlight",
        coordinator_state="CMD_BACKLIGHT",
        entity_category=EntityCategory.CONFIG,
        icon="mdi:lightbulb"
    ),
    "rgb": SyncleoLightDescription(
        translation_key="rgb_light",
        key="rgb_light",
        coordinator_state="CMD_MODE",
        coordinator_color="CMD_PROGRAM_DATA",
        func=parse_color,
        icon="mdi:palette"
    ),
}


# ---------- NUMBER ----------
@dataclass(frozen=True)
class SyncleoNumberDescription(SyncleoEntityDescription):
    """Описание для числа."""
    min_value: float = 0
    max_value: float = 100
    step: float = 1
    native_unit_of_measurement: Optional[str] = None


NUMBER_DESCRIPTIONS = {
    "humidifier_intensity": SyncleoNumberDescription(
        translation_key="intensity",
        key="intensity",
        coordinator_state="CMD_SPEED",
        min_value=0,
        max_value=7,
        step=1,
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        native_unit_of_measurement=None
    ),
}


# ---------- VACUUM ----------
@dataclass(frozen=True)
class SyncleoVacuumDescription(SyncleoEntityDescription):
    """Описание для пылесоса."""
    coordinator_mode: Optional[str] = None
    coordinator_battery: Optional[str] = None


VACUUM_DESCRIPTIONS = {
    "vacuum": SyncleoVacuumDescription(
        translation_key="vacuum",
        key="vacuum",
        name="Vacuum Cleaner",
        coordinator_mode="CMD_MODE",
        coordinator_battery=None,
        icon="mdi:robot-vacuum"
    ),
}

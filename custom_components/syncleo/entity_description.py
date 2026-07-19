from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, List
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.humidifier import HumidifierEntity, HumidifierEntityDescription, HumidifierDeviceClass
from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACAction, HVACMode
from homeassistant.components.number import NumberDeviceClass, NumberEntityDescription
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
        return int.from_bytes(data[:2], 'little')
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
#        icon="mdi:kettle"
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
#        icon="mdi:kettle"
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
#        icon="mdi:kettle"
    ),
    "water_boiler": SyncleoWaterHeaterDescription(
        key="water_boiler",
        translation_key="water_boiler",
        name="boiler",
        min_temp=30,
        max_temp=75,
        operation_list={"off": "0", "performance": "1", "electric": "2", "heat_pump": "3"},
        coordinator_mode="CMD_MODE",
        coordinator_target_temperature="CMD_TARGET_TEMPERATURE",
        coordinator_current_temperature="CMD_CURRENT_TEMPERATURE",
#        icon="mdi:kettle"
    ),
    "water_boiler_antifrost": SyncleoWaterHeaterDescription(
        key="water_boiler_antifrost",
        translation_key="water_boiler",
        name="boiler",
        min_temp=30,
        max_temp=75,
        operation_list={"off": "0", "performance": "1", "electric": "2", "heat_pump": "3", "gas": "5"},
        coordinator_mode="CMD_MODE",
        coordinator_target_temperature="CMD_TARGET_TEMPERATURE",
        coordinator_current_temperature="CMD_CURRENT_TEMPERATURE",
#        icon="mdi:kettle"
    ),
    "water_boiler_eco": SyncleoWaterHeaterDescription(
        key="water_boiler_eco",
        translation_key="water_boiler",
        name="boiler",
        min_temp=30,
        max_temp=75,
        operation_list={"off": "0", "performance": "1", "electric": "2", "heat_pump": "3", "eco": "6"},
        coordinator_mode="CMD_MODE",
        coordinator_target_temperature="CMD_TARGET_TEMPERATURE",
        coordinator_current_temperature="CMD_CURRENT_TEMPERATURE",
#        icon="mdi:kettle"
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
    program_index: str = "0"
    byte_index: str = None

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
    "backlight_bright": SyncleoSwitchDescription(
        translation_key="backlight_bright_switch",
        key="backlight_bright",
        coordinator_state="CMD_BACKLIGHT",
        func=parse_hex_to_bool,
        icon="mdi:lightbulb",
        entity_category=EntityCategory.CONFIG
    ),
    "backlight_bright_pd": SyncleoSwitchDescription(
        translation_key="backlight_bright_switch",
        key="backlight_bright_pd",
        coordinator_state="CMD_PROGRAM_DATA",
        program_index="0",
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
        translation_key="warm_stream_switch",
        key="warmstream",
        coordinator_state="CMD_WARMSTREAM",
        func=parse_hex_to_bool,
        icon="mdi:heat-wave",
        entity_category=EntityCategory.CONFIG
    ),
    "ultraviolet": SyncleoSwitchDescription(
        translation_key="ultraviolet_switch",
        key="ultraviolet",
        coordinator_state="CMD_ULTRAVIOLET",
        func=parse_hex_to_bool,
        icon="mdi:white-balance-sunny",
        entity_category=EntityCategory.CONFIG
    ),
    "night": SyncleoSwitchDescription(
        translation_key="backlight_switch",
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
        icon="mdi:water-boiler-auto",
        entity_category=EntityCategory.CONFIG
    ),
    "bss_mode": SyncleoSwitchDescription(
        translation_key="bss_mode_switch",
        key="bss_mode",
        coordinator_state="CMD_BSS",
        func=parse_hex_to_bool,
        icon="mdi:bacteria",
        entity_category=EntityCategory.CONFIG
    ),
    "no_frost": SyncleoSwitchDescription(
        translation_key="no_frost_switch",
        key="no_frost",
        coordinator_state="CMD_KEEP_WARM",
        func=parse_hex_to_bool,
        icon="mdi:snowflake-off",
        entity_category=EntityCategory.CONFIG
    ),
    "damper": SyncleoSwitchDescription(
        translation_key="damper_switch",
        key="damper",
        coordinator_state="CMD_DAMPER",
        func=parse_hex_to_bool,
        icon="mdi:swap-horizontal-circle-outline",
        entity_category=EntityCategory.CONFIG
    ),
    "display_off_heater": SyncleoSwitchDescription(
        translation_key="display_off_heater_switch",
        key="display_off_heater",
        coordinator_state="CMD_PROGRAM_DATA",
        program_index = "0",
        byte_index = "1",
        func=parse_hex_to_bool,
        entity_category=EntityCategory.CONFIG
    ),
    "half_power_heater": SyncleoSwitchDescription(
        translation_key="half_power_heater_switch",
        key="half_power_heater",
        coordinator_state="CMD_PROGRAM_DATA",
        program_index = "0",
        byte_index = "0",
        func=parse_hex_to_bool,
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
    expendables_index: str = "0"
    program_index: str = "0"

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
        entity_category=EntityCategory.DIAGNOSTIC,
        coordinator_state="CMD_EXPENDABLES",
        expendables_index = "0",
        icon="mdi:filter"
    ),
    "clean_retain": SyncleoSensorDescription(
        translation_key="clean_retain_sensor",
        key="clean_retain",
        device_class=None,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        coordinator_state="CMD_EXPENDABLES",
        expendables_index = "1",
        icon="mdi:cup-water"
    ),
    "anode_retain": SyncleoSensorDescription(
        key="anode_retain",
        name="anode_retain",
        translation_key="anode_retain_sensor",
        device_class=None,
        native_unit_of_measurement=UnitOfTime.DAYS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        coordinator_state="CMD_EXPENDABLES",
        expendables_index = "0",
        icon="mdi:sign-pole",
    ),
    "pm_2_5": SyncleoSensorDescription(
        key="pm_2_5",
        name="pm_2_5",
        translation_key="pm2_5_sensor",
        device_class=None,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        coordinator_state="CMD_CURRENT_PM2",
        func=parse_weight,
        icon="mdi:molecule",
    ),
    "co2": SyncleoSensorDescription(
        key="co2",
        name="co2",
        translation_key="co2_sensor",
        device_class=SensorDeviceClass.CO2,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=SensorStateClass.MEASUREMENT,
        coordinator_state="CMD_CURRENT_CO2",
        func=parse_weight,
        icon="mdi:molecule-co2",
    ),
    "filter_retain_percent": SyncleoSensorDescription(
        translation_key="filter_retain_sensor",
        key="filter_retain",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        coordinator_state="CMD_EXPENDABLES",
        expendables_index = "0",
        icon="mdi:filter",
    ),
    "pre_filter_retain_percent": SyncleoSensorDescription(
        translation_key="pre_filter_retain_sensor",
        key="pre_filter_retain_percent",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        coordinator_state="CMD_EXPENDABLES",
        expendables_index = "1",
        icon="mdi:filter",
    ),
    "time_to_end": SyncleoSensorDescription(
        translation_key="time_to_end_turbo_sensor",
        key="time_to_end",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        coordinator_state="CMD_TOTAL_TIME",
        func=parse_time,
        icon="mdi:timer",
    ),
    "current_power": SyncleoSensorDescription(
        translation_key="current_power_sensor",
        key="current_power",
        device_class=None,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        coordinator_state="CMD_PROGRAM_DATA",
        program_index = "0",
        func=parse_temp,
        icon="mdi:equalizer",
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
        name="Preset",
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
    "select_melody": SyncleoSelectDescription(
        key="select_melody",
        name="Melody",
        translation_key="select_melody",
        options={
          "mute": 0,
          "rainstorm": 1,
          "surf": 2,
          "forest": 3,
          "birdsong": 4,
          "bonfire": 5,
        },
        coordinator_mode="CMD_AMOUNT",
        entity_category=EntityCategory.CONFIG,
        icon="mdi:music-note",
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
    program_index: str = "0"

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
    "humidifier_intensity_low": SyncleoNumberDescription(
        translation_key="intensity",
        key="intensity_low",
        coordinator_state="CMD_SPEED",
        min_value=0,
        max_value=3,
        step=1,
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        native_unit_of_measurement=None
    ),
    "humidifier_evaporation": SyncleoNumberDescription(
        translation_key="evaporation_rate",
        key="evaporation_rate",
        coordinator_state="CMD_SPEED",
        min_value=1,
        max_value=3,
        step=1,
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        native_unit_of_measurement=None
    ),
    "temperature_difference_eco": SyncleoNumberDescription(
        translation_key="temperature_difference_eco",
        key="temperature_difference_eco",
        coordinator_state="CMD_PROGRAM_DATA",
        program_index = "2",
        min_value=3,
        max_value=7,
        step=1,
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    "temperature_difference_antifrost": SyncleoNumberDescription(
        translation_key="temperature_difference_antifrost",
        key="temperature_difference_antifrost",
        coordinator_state="CMD_PROGRAM_DATA",
        program_index = "3",
        min_value=3,
        max_value=7,
        step=1,
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
}

# ---------- CLIMATE ----------
@dataclass(frozen=True)
class SyncleoClimateDescription(SyncleoEntityDescription):
    """Описание для Climate."""
    
    fan_mode: Optional[str] = None
    fan_modes: Dict[str, str] = field(default_factory=dict)
    preset_mode: Optional[str] = None
    preset_modes: Dict[str, str] = field(default_factory=dict)
    hvac_modes: list | None = None
    supported_features: int | None = None
    min_temp: int = 10
    max_temp: int = 40
    temp_step: int = 1
    swing_mode: Optional[str] = None
    swing_modes: Dict[str, str] = field(default_factory=dict)
    coordinator_current_temperature: Optional[str] = None
    coordinator_target_temperature: Optional[str] = None
    coordinator_speed: Optional[str] = None
    coordinator_mode: Optional[str] = None


CLIMATE_DESCRIPTIONS = {
    "climate_fan_only": SyncleoClimateDescription(
        name = "Climate",
        key = "climate_fan_only",
        translation_key = "climate",
        fan_mode = "off",
        fan_modes = {"off": "0", "1_speed": "1", "2_speed": "2", "3_speed": "3", "4_speed": "4", "5_speed": "5", "6_speed": "6", "7_speed": "7"},
        preset_mode = "passive",
        preset_modes = {"hands": "1", "auto": "2", "night": "3", "turbo": "4", "passive": "5"},
        hvac_modes = [HVACMode.OFF, HVACMode.FAN_ONLY],
        supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.PRESET_MODE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
        ),
        coordinator_current_temperature="CMD_CURRENT_TEMPERATURE",
        coordinator_target_temperature="CMD_TARGET_TEMPERATURE",
        coordinator_speed="CMD_SPEED",
        coordinator_mode="CMD_MODE",
        min_temp = 5,
        max_temp = 25,
        device_class = None,
    ),
    "climate_asp_100": SyncleoClimateDescription(
        name = "Climate",
        key = "climate_asp_100",
        translation_key = "climate",
        fan_mode = "off",
        fan_modes = {"off": "0", "1_speed": "1", "2_speed": "2", "3_speed": "3", "4_speed": "4", "5_speed": "5", "6_speed": "6", "7_speed": "7"},
        preset_mode = "passive",
        preset_modes = {"hands": "1", "auto": "2", "night": "3", "turbo": "4", "passive": "5"},
        hvac_modes = [HVACMode.OFF, HVACMode.FAN_ONLY],
        supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.PRESET_MODE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
        ),
        coordinator_current_temperature="CMD_CURRENT_TEMPERATURE",
        coordinator_target_temperature="CMD_TARGET_TEMPERATURE",
        coordinator_speed="CMD_SPEED",
        coordinator_mode="CMD_MODE",
        min_temp = 5,
        max_temp = 25,
        temp_step = 1,
        device_class = None,
    ),
    "climate_asp_200": SyncleoClimateDescription(
        name = "Climate",
        key = "climate_asp_200",
        translation_key = "climate",
        fan_mode = "off",
        fan_modes = {"off": "0", "1_speed": "1", "2_speed": "2", "3_speed": "3", "4_speed": "4", "5_speed": "5", "6_speed": "6", "7_speed": "7", "8_speed": "8", "9_speed": "9"},
        preset_mode = "auto",
        preset_modes = {"hands": "1", "auto": "2", "night": "3", "turbo": "4"},
        hvac_modes = [HVACMode.OFF, HVACMode.FAN_ONLY],
        supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.PRESET_MODE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
        ),
        coordinator_current_temperature="CMD_CURRENT_TEMPERATURE",
        coordinator_target_temperature="CMD_TARGET_TEMPERATURE",
        coordinator_speed="CMD_SPEED",
        coordinator_mode="CMD_MODE",
        min_temp = 5,
        max_temp = 25,
        temp_step = 1,
    ),
    "climate_heater": SyncleoClimateDescription(
        name = "Heater",
        key = "heater",
        translation_key = "heater",
        fan_mode = "auto",
        fan_modes = {"auto": "0", "20_5_percent": "1", "40_5_percent": "2", "60_5_percent": "3", "80_5_percent": "4", "100_5_percent": "5"},
        preset_mode = "comfort",
        preset_modes = {"comfort": "1", "eco": "2", "away": "3"},
        hvac_modes = [HVACMode.OFF, HVACMode.HEAT],
        supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.PRESET_MODE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
        ),
        coordinator_current_temperature="CMD_CURRENT_TEMPERATURE",
        coordinator_target_temperature="CMD_TARGET_TEMPERATURE",
        coordinator_speed="CMD_SPEED",
        coordinator_mode="CMD_MODE",
        min_temp = 5,
        max_temp = 35,
        temp_step = 1,
    ),
    "climate_heater_4mode": SyncleoClimateDescription(
        name = "Heater",
        key = "heater",
        translation_key = "heater",
        fan_mode = "auto",
        fan_modes = {"auto": "0", "10_percent": "1", "20_percent": "2", "30_percent": "3", "40_percent": "4", "50_percent": "5", "60_percent": "6", "70_percent": "7", "80_percent": "8", "90_percent": "9", "100_percent": "10"},
        preset_mode = "comfort",
        preset_modes = {"comfort": "1", "eco": "2", "away": "3", "hands": "4"},
        hvac_modes = [HVACMode.OFF, HVACMode.HEAT],
        supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.PRESET_MODE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
        ),
        coordinator_current_temperature="CMD_CURRENT_TEMPERATURE",
        coordinator_target_temperature="CMD_TARGET_TEMPERATURE",
        coordinator_speed="CMD_SPEED",
        coordinator_mode="CMD_MODE",
        min_temp = 5,
        max_temp = 35,
        temp_step = 1,
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

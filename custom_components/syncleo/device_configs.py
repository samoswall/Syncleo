from typing import Dict, List

# Конфигурации устройств Polaris

POLARIS_DEVICE_CONFIGS: Dict[int, Dict[str, List[str]]] = {
##############################
#          Чайники           #
##############################
    2: {
        "water_heater": ["kettle_with_tea_time"],
        "switch": ["power", "sound", "child_lock"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    6: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    8: {
        "water_heater": ["kettle_with_tea_time"],
        "switch": ["power", "sound", "child_lock"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    29: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    36: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
    37: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
    38: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    51: {
        "water_heater": ["kettle_with_tea_time"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    52: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    53: {
        "water_heater": ["kettle_with_tea_time"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    54: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    56: {
        "water_heater": ["kettle_with_tea_time"],
        "switch": ["power", "sound", "child_lock"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    57: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    58: {
        "water_heater": ["kettle_with_tea_time"],
        "switch": ["power", "sound", "child_lock"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    59: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    60: {
        "water_heater": ["kettle_with_tea_time"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    61: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    62: {
        "water_heater": ["kettle_with_tea_time"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    63: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    67: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    82: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    83: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    84: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    85: {
        "water_heater": ["kettle_with_tea_time"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    86: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
    97: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
    98: {
        "water_heater": ["kettle_with_tea_time"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error", "weight"],
        "select": ["select_tea_kettle"]
    },
    105: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    106: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
    117: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
    121: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    139: {
        "water_heater": ["kettle_with_tea_time"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    164: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error", "weight"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
    165: {
        "water_heater": ["kettle_with_tea_time"],
        "switch": ["power", "sound", "child_lock"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["select_tea_kettle"]
    },
    175: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
    176: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
    177: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
    185: {
        "water_heater": ["kettle_with_tea_time"],
        "switch": ["power", "sound", "child_lock"],
        "sensor": ["temperature", "firmware", "device_type", "error", "weight"],
        "select": ["select_tea_kettle"]
    },
    188: {
        "water_heater": ["kettle_with_tea_time"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error", "weight"],
        "select": ["select_tea_kettle"]
    },
    189: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
    194: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
    196: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
    205: {
        "water_heater": ["kettle_with_tea_time_keep_with_warm"],
        "switch": ["power", "sound", "child_lock"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
    208: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error", "weight"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
    209: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
    223: {
        "water_heater": ["kettle_with_tea_time"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error", "weight"],
        "select": ["select_tea_kettle"]
    },
    244: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error", "weight"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
    245: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error", "weight"],
        "select": ["select_tea_kettle"]
    },
    253: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
    254: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
    255: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
    260: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
    262: {
        "water_heater": ["kettle_with_tea_time_keep_with_warm"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error", "weight"],
        "select": ["select_tea_kettle"]
    },
    263: {
        "water_heater": ["kettle_with_tea_time"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error", "weight"],
        "select": ["select_tea_kettle"]
    },
    271: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
    275: {
        "water_heater": ["kettle_with_tea_time"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error", "weight"],
        "select": ["select_tea_kettle"]
    },
    294: {
        "water_heater": ["kettle_with_tea_time_keep_with_warm"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error", "weight"],
        "select": ["select_tea_kettle"]
    },
    308: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
##############################
#        Увлажнители         #
##############################
    4: {
        "humidifier": ["humidifier_5A_mode"],
        "number": ["humidifier_intensity"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain", "clean_retain"],
        "switch": ["sound", "child_lock", "backlight", "ionization", "warm_stream"]
    },
    15: {
        "humidifier": ["humidifier_4_mode"],
        "number": ["humidifier_intensity"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain", "clean_retain"],
        "switch": ["sound", "child_lock", "backlight", "ionization", "warm_stream"]
    },
    17: {
        "humidifier": ["humidifier_7_mode"],
        "number": ["humidifier_intensity"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain", "clean_retain"],
        "switch": ["sound", "child_lock", "backlight", "ionization", "warm_stream"]
    },
    18: {
        "humidifier": ["humidifier_7_mode"],
        "number": ["humidifier_intensity"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain", "clean_retain"],
        "switch": ["sound", "child_lock", "backlight", "ionization", "warm_stream"]
    },
    25: {
        "humidifier": ["humidifier_3A_mode"],
        "number": ["humidifier_intensity_low"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain", "clean_retain"],
        "switch": ["sound", "child_lock", "backlight"]
    },
    44: {
        "humidifier": ["humidifier_7_mode"],
        "number": ["humidifier_intensity"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain", "clean_retain"],
        "switch": ["sound", "child_lock", "backlight", "ionization", "warm_stream"]
    },
    70: {
        "humidifier": ["humidifier_7_mode"],
        "switch": ["sound", "child_lock", "ionization", "warm_stream", "backlight"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain", "clean_retain"],
        "number": ["humidifier_intensity"]
    },
    71: {
        "humidifier": ["humidifier_4_mode"],
        "number": ["humidifier_intensity_low"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain", "clean_retain"],
        "switch": ["sound", "child_lock", "backlight"]
    },
    72: {
        "humidifier": ["humidifier_5B_mode"],
        "number": ["humidifier_intensity_low"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain", "clean_retain"],
        "switch": ["sound", "child_lock", "backlight", "ionization", "warm_stream"]
    },
    73: {
        "humidifier": ["humidifier_4_mode"],
        "number": ["humidifier_intensity_low"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain", "clean_retain"],
        "switch": ["sound", "child_lock", "backlight", "ionization"]
    },
    74: {
        "humidifier": ["humidifier_5B_mode"],
        "number": ["humidifier_intensity_low"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain", "clean_retain"],
        "switch": ["sound", "child_lock", "backlight", "ionization", "warm_stream"]
    },
    75: {
        "humidifier": ["humidifier_4_mode"],
        "number": ["humidifier_intensity_low"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain", "clean_retain"],
        "switch": ["sound", "child_lock", "backlight"]
    },
    87: {
        "humidifier": ["humidifier_5B_mode"],
        "number": ["humidifier_intensity_low"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain", "clean_retain"],
        "switch": ["sound", "child_lock", "backlight"]
    },
    99: {
        "humidifier": ["humidifier_4_mode"],
        "number": ["humidifier_intensity_low"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain", "clean_retain"],
        "switch": ["sound", "child_lock", "backlight"]
    },
    137: {
        "humidifier": ["humidifier_1_mode"],
        "number": ["humidifier_intensity_low"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain", "clean_retain"],
        "switch": ["sound", "child_lock", "backlight", "ionization"]
    },
    147: {
        "humidifier": ["humidifier_5B_mode"],
        "number": ["humidifier_intensity"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain", "clean_retain"],
        "switch": ["sound", "child_lock", "backlight", "ionization", "warm_stream"]
    },
    153: {
        "humidifier": ["humidifier_3B_mode"],
        "number": ["humidifier_intensity_low"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain", "clean_retain"],
        "switch": ["sound", "child_lock", "backlight", "ionization"]
    },
    155: {
        "humidifier": ["humidifier_5B_mode"],
        "number": ["humidifier_intensity_low"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain", "clean_retain"],
        "switch": ["sound", "child_lock", "backlight", "ionization"]
    },
    157: {
        "humidifier": ["humidifier_3B_mode"],
        "number": ["humidifier_intensity_low"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain", "clean_retain"],
        "switch": ["sound", "child_lock", "backlight", "ionization", "warm_stream", "ultraviolet"]
    },
    158: {
        "humidifier": ["humidifier_3B_mode"],
        "number": ["humidifier_intensity_low"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain", "clean_retain"],
        "switch": ["sound", "child_lock", "night", "ionization", "warm_stream"]
    },
}

# Конфигурации для устройств Hommyn
HOMMYN_DEVICE_CONFIGS: Dict[int, Dict[str, List[str]]] = {
##############################
#          Бойлеры           #
##############################
    2: {
        "water_heater": ["water_boiler"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "switch": ["power", "bss_mode", "smart_mode","no_frost"]
    },
    7: {
        "water_heater": ["water_boiler_antifrost"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "switch": ["power", "bss_mode"]
    },
    33: {
        "water_heater": ["water_boiler_eco"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "switch": ["power", "bss_mode"]
    },
    44: {
        "water_heater": ["water_boiler"],
        "sensor": ["temperature", "firmware", "device_type", "error", "anode_retain"],
        "switch": ["power", "bss_mode", "smart_mode", "backlight_bright", "backlight_bright_pd"]
    },
    76: {
        "water_heater": ["water_boiler_eco"],
        "sensor": ["temperature", "firmware", "device_type", "error", "anode_retain"],
        "switch": ["power", "bss_mode", "smart_mode"]
    },
    77: {
        "water_heater": ["water_boiler"],
        "sensor": ["temperature", "firmware", "device_type", "error", "anode_retain"],
        "switch": ["power", "child_lock", "bss_mode", "smart_mode"]
    },
##############################
#        Увлажнители         #
##############################
    35: {
        "humidifier": ["humidifier_11_mode"],
        "number": ["humidifier_evaporation"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain"],
        "switch": ["sound", "ionization", "warm_stream", "ultraviolet"]
    },
    81: {
        "humidifier": ["humidifier_2_mode"],
        "number": ["humidifier_evaporation"],
        "sensor": ["humidity", "firmware", "device_type", "error"],
        "switch": ["night", "backlight", "warm_stream"]
    },
##############################
#          Бризеры           #
##############################
    30: {
        "climate": ["climate_asp_200"],
        "select": ["select_melody"],
        "sensor": ["temperature", "firmware", "device_type", "error", "co2", "pm_2_5", "filter_retain_percent", "pre_filter_retain_percent", "time_to_end"],
        "switch": ["power", "sound", "backlight", "damper", "ionization", "ultraviolet"]
    },
    32: {
        "climate": ["climate_asp_100"],
        "select": ["select_melody"],
        "sensor": ["temperature", "firmware", "device_type", "error", "co2", "filter_retain_percent"],
        "switch": ["power", "sound", "backlight"]
    },
    59: {
        "climate": ["climate_asp_200"],
        "select": ["select_melody"],
        "sensor": ["temperature", "firmware", "device_type", "error", "co2", "pm_2_5", "filter_retain_percent", "pre_filter_retain_percent", "time_to_end"],
        "switch": ["power", "sound", "backlight", "damper", "ionization", "ultraviolet"]
    },
    69: {
        "climate": ["climate_asp_100"],
        "select": ["select_melody"],
        "sensor": ["temperature", "firmware", "device_type", "error", "co2", "filter_retain_percent"],
        "switch": ["power", "sound", "backlight"]
    },
##############################
#        Конвекторы          #
##############################
    6: {
        "climate": ["climate_heater"],
        "sensor": ["temperature", "firmware", "device_type", "error", "current_power"],
        "switch": ["power", "sound", "backlight", "child_lock", "damper", "display_off_heater"],
        "number": ["temperature_difference_eco", "temperature_difference_antifrost"]
        
    },
    14: {
        "climate": ["climate_heater"],
        "sensor": ["temperature", "firmware", "device_type", "error", "current_power"],
        "switch": ["child_lock", "backlight"]

    },
    46: {
        "climate": ["climate_heater_4mode"],
        "sensor": ["temperature", "firmware", "device_type", "error", "current_power"],
        "switch": ["power", "sound", "backlight", "child_lock", "damper", "display_off_heater", "half_power_heater"],
        "number": ["temperature_difference_eco", "temperature_difference_antifrost"]
    },
    47: {
        "climate": ["climate_heater"],
        "sensor": ["temperature", "firmware", "device_type", "error", "current_power"],
        "switch": ["power", "sound", "backlight", "child_lock", "damper", "display_off_heater"],
        "number": ["temperature_difference_eco", "temperature_difference_antifrost"]
    },
    49: {
        "climate": ["climate_heater"],
        "sensor": ["temperature", "firmware", "device_type", "error", "current_power"],
        "switch": ["child_lock", "backlight"]
    },

}

# Маппинг типа устройства к конфигурации, если нет конкретной           временная заглушка, потом будет убрана!
DEFAULT_CONFIGS: Dict[str, Dict[str, List[str]]] = {
    "kettle": {
        "water_heater": ["kettle"],
        "switch": ["power", "child_lock"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["program"]
    },
    "humidifier": {
        "humidifier": ["humidifier"],
        "switch": ["power", "ionization"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "tank"],
        "select": ["mode"]
    },
    "air_cleaner": {
        "fan": ["air_cleaner"],
        "switch": ["power", "child_lock"],
        "sensor": ["temperature", "firmware", "device_type"],
        "select": ["speed", "mode"]
    },
    "cooker": {
        "switch": ["power", "child_lock"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["mode"]
    },
    "air_fryer": {
        "switch": ["power", "child_lock"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "number": ["temperature"]
    },
    "coffeemaker": {
        "switch": ["power", "child_lock"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "select": ["mode"]
    },
    "boiler": {
        "water_heater": ["water_boiler"],
        "switch": ["power", "child_lock"],
        "sensor": ["temperature", "firmware", "device_type", "error"]
    },
    "heater": {
        "fan": ["fan"],
        "switch": ["power", "child_lock"],
        "sensor": ["temperature", "firmware", "device_type"],
        "select": ["mode"]
    },
    "cleaner": {
        "vacuum": ["vacuum"],
        "switch": ["power"],
        "sensor": ["firmware", "device_type"],
        "select": ["mode"]
    },
    "fan": {
        "fan": ["fan"],
        "switch": ["power", "child_lock"],
        "sensor": ["firmware", "device_type"],
        "select": ["speed", "mode"]
    },
    "default": {
        "switch": ["power"],
        "sensor": ["firmware", "device_type"]
    }
}
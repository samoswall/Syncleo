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
#    4: {

#    },
#    15: {

#    },
#    17: {

#    },
#    18: {

#    },
#    25: {

#    },
#    44: {

#    },
    70: {
        "humidifier": ["humidifier_7_mode"],
        "switch": ["sound", "child_lock", "ionization", "warm_stream", "backlight"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain", "clean_retain"],
        "number": ["humidifier_intensity"]
    },
#    71: {

#    },
#    72: {

#    },
#    73: {

#    },
#    74: {

#    },
#    75: {

#    },
#    87: {

#    },
#    99: {

#    },
#    137: {

#    },
#    147: {

#    },
#    153: {

#    },
#    155: {

#    },
#    157: {

#    },
#    158: {

#    },
}

# Конфигурации для устройств Hommyn
HOMMYN_DEVICE_CONFIGS: Dict[int, Dict[str, List[str]]] = {
##############################
#        Увлажнители         #
##############################
#    35: {

#    },
#    81: {

#    },
##############################
#                            #
##############################
    

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
        "water_heater": ["water_heater"],
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
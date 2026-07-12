# Syncleo
Integration of Polaris and Hommyn devices into Home Assistant using UDP protocol

Интеграция для Home Assistant поддерживающая полное управление устройствами экосистем<br>
Polaris IQ Home и Hommyn c использованием протокола UDP

Также поддерживаются все бренды использующие SDK Syncleo и имеющие mdns `_syncleo._udp.local.`

Локальное управление (внутри сети) работает одновременно с облаком, приложением и(или) MQTT, не мешая им.

> [!WARNING]
> Интеграция находится на стадии тестирования!
> Это первая версия со стабильным ядром!
> Реализовано:
> - отслеживание отключения устройства (все сущности становятся недоступны)
> - отслеживание появление в сети (все сущности становятся доступны)
> - при перезагрузки Home Assistant корректное восстановление соединения (устройство может быть выключено, или перезагружалось, а значит сменились ключи шифрования и порт подключения)
> - автоматическое обнаружение новых устройств

Пока добавлены только все чайники из интеграции POLARIS MQTT - как устройства с частыми отключениями от сети

Для добавления устройства в интеграцию, необходим токен устройсва!

:information_source: Как получить токен устройства:

Вариант 1<br>
В приложении на телефоне в настройках устройства -> Контроль прав -> Нажать на значок поделиться устройством
Полученным QR-кодом опять поделиться и появится возможность скопировать или отправить текстовую ссылку вида:<br>
`https://l.polaris-iot.com/device-share/polaris/86/112233445566?token=aaaabbbbccccddddeeeeffffeeeedddd&name=Chainik`<br>
где `aaaabbbbccccddddeeeeffffeeeedddd` токен вашего устройства.

Вариант 2 (у кого устройство уже подключено к MQTT брокеру через разворот трафика)<br>
Токен в пути топика устройства:
```
polaris/86/aaaabbbbccccddddeeeeffffeeeedddd/state/
```
или
```
rusclimate/67/aaaabbbbccccddddeeeeffffeeeedddd/state
```
Посмотреть можно любыми средствами, например mqtt explorer

Устройство автоматически обнаруживается и предлагает себя добавить в интерфейсе Home Assistant.
Если устройства нет нужно его разбудить!
Вариант 1: Выключить и включить устройство сноваю. После подключения к сети устройство обнаружится.
Вариант 2: Запустить приложение на телефоне, оно заставит устройство откликнуться.
Вариант 3: Перезагрузить Home Assistant, он запустит обнаружение всех устройств.

> [!NOTE]
> Информация для желающих добавить свое устройство, не дожидаясь обновлений интеграции<br>
> Не забывайте делиться успешными настройками, это поможет многим пользователям!

Добавлять новые устройства просто! На это был сделан упор для облегчения поддержки и сопровождения!

1. В интеграции имеется файл `const.py` в котором перечислены все поддерживаемые приложением устройства Polaris и Hommyn
```
86:  {"model": "PWK-1725CGLD", "class": "kettle"},
```
Тут все просто - тип, модель и класс устройства.


2. В файле `device_configs.py` перечисляется в 2 разделах (POLARIS_DEVICE_CONFIGS и HOMMYN_DEVICE_CONFIGS) какие сущности содержит устройство

```
# Чайник
    86: {
        "water_heater": ["kettle"],
        "switch": ["power", "sound", "child_lock", "backlight"],
        "sensor": ["temperature", "firmware", "device_type", "error"],
        "light": ["night_light"],
        "select": ["select_tea_kettle"]
    },
# Увлажнитель
    70: {
        "humidifier": ["humidifier_7_mode"],
        "switch": ["sound", "child_lock", "ionization", "warm_stream", "backlight"],
        "sensor": ["humidity", "temperature", "firmware", "device_type", "error", "filter_retain", "clean_retain"],
        "number": ["humidifier_intensity"]
    },
```
Тут тоже все просто. Чайник содержит:
- сущность "water_heater" в чайнике она одна с именем "kettle" (для бойлера имя будет другое)
- сущности выключателей "switch" в этом чайнике: "power", "sound", "child_lock", "backlight"
- сущности сенсоров "sensor" в чайнике "temperature", "firmware", "device_type", "error" (последние 3 есть у всех)
- сущность света - в этой модели есть функция Ночник с выбором цвета, поэтому "light" с именем "night_light"
- сущность выбора напитков "select": "select_tea_kettle"
Просто нужно перечислить все, что есть в устройстве, исходя из имеющихся имен в файле `entity_description.py`


3. В файле `entity_description.py` описаны все варианты существующих сущностей всех устройств Polaris и Hommyn с функциями парсинга.
```
# Пример чайника без режимов "high_demand":"2" и "gas":"6" Кипячение с удержанием и Чайная церемония
    "kettle": SyncleoWaterHeaterDescription(  # kettle - имя сущности, имена все разные, если есть отличия       
        key="kettle",                         # уникальный ключ описания - нужен НА
        translation_key="kettle",             # уникальный ключ для перевода на любой язык, переводы в translations\ru.json 
        name="Kettle",                        # Имя сущности - если не заменится переводом
        min_temp=30,                          # Минимальная температура 
        max_temp=100,                         # Максимальная температура
        operation_list={"off":"0","performance":"1","electric":"3","heat_pump":"4","eco":"5"},  # Список режимов (у разных моделей разный)
        coordinator_mode="CMD_MODE",                                  # Команда протокола для режимов
        coordinator_target_temperature="CMD_TARGET_TEMPERATURE",      # Команда протокола для целевой температуры
        coordinator_current_temperature="CMD_CURRENT_TEMPERATURE",    # Команда протокола для текущей температуры
        icon="mdi:kettle"                                             # иконка, можно не ставить, а описать в icons.json
    ),
```
для сенсоров все как и в требованиях НА, только добавлены:
```
    "temperature": SyncleoSensorDescription(
        key="temperature",
        translation_key="temperature_sensor",
        device_class=SensorDeviceClass.TEMPERATURE,              # класс сенсора
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,    # еденицы измерения
        state_class=SensorStateClass.MEASUREMENT,                # группа состояний
        coordinator_state="CMD_CURRENT_TEMPERATURE",             # Команда протокола для текущей температуры
        func=parse_temp,                                         # Функция для парсинга
        icon="mdi:thermometer"
    ),
```

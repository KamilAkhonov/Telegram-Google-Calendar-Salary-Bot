# Telegram-Google-Calendar-Salary-Bot

## `Telegram` бот для подсчета заработной платы через `Google Calendar API`.

> Задача: подсчитать заработную плату за предыдущие полмесяца(с 30 прошлого по 15 текущего) и текущие полмесяца(с 15 по 30 текущего месяца), заработная плата выдается по определенным дням и фиксируется в виде мероприятий в `Google Calendar`.

Для автоматизации решения задачи было предложено использование `Telegram` бота. В качестве библиотеки для работы с `Telegram API` использовалась `telebot` (pyTelegramBotAPI). Описывать поэтапно создание бота и работу с `telebot` не буду. Остановлюсь на ключевых моментах.

***Ограничение доступа к боту***

Я не стал заморачиваться с авторизацией в боте, поэтому просто отрезаю доступ по 'Telegram ID':
```python
allowed_user_id = ' '
def restricted(func):
    def wrapped(message):
        user_id = message.from_user.id
        if user_id == allowed_user_id:
            return func(message)
        else:
            bot.reply_to(message, "У вас нет доступа к этому боту. Извините.")

    return wrapped

@bot.message_handler(content_types=['text'])
@restricted
# обработчик
```
Конечно, можно было добавить авторизацию, я подумаю над этим :)

***Получение зарплаты***

У меня вся работа разделена на два направления: работа с `Telegram` ботом, работа с `Google Calendar API`. Для упрощения работы было решено использовать два файла отвечающие за указанные направления. Чтобы подружить данные направления был использован модуль `subprocess`, который позволил получить результаты запроса к календарю и выдать пользователю.

```python
result = subprocess.run(['python', 'Schedule.py', str(0)], capture_output=True, text=True)
# Process the output and retrieve the value of the variable
try:
    variable_value = result.stdout.strip()
    bot.send_message(message.from_user.id, f"Зарплата за предыдущие две недели была в размере {variable_value}₽")
except ValueError:
    print("Ошибка: невозможно преобразовать значение в число.")
```

***Дополнительный параметр***

В качестве параметра в файл `Schedule.py` передается либо 0, либо 1, отвечающие за период выплаты зарплаты:

```python
if flag == 0:
    # 30th of the previous month
    start_date = datetime.datetime(datetime.datetime.utcnow().year, datetime.datetime.utcnow().month - 1, 30)
    # 14th of the current month (not including)
    end_date = datetime.datetime(datetime.datetime.utcnow().year, datetime.datetime.utcnow().month, 15)
elif flag == 1:
    # 15th of the current month
    start_date = datetime.datetime(datetime.datetime.utcnow().year, datetime.datetime.utcnow().month, 15)
    # 30th of the current month (not including)
    end_date = datetime.datetime(datetime.datetime.utcnow().year, datetime.datetime.utcnow().month, 30)
```
Для дополнительной защиты от ошибок были использованы небольшие проверки для параметра, а именно на количество аргументов и тип

```python
if len(sys.argv) != 2:
    print("Ошибка: необходимо передать один аргумент.")
    sys.exit(1)

# Get the value of the argument (variable) from the command line
try:
    flag = int(sys.argv[1])
except ValueError:
    print("Ошибка: аргумент должен быть числом.")
    sys.exit(1)
```

***Запрос к Google Calendar API***

Сам шаблон для подключения и работы с `API` представлен в официальной документации `Google` на [туть](https://developers.google.com/calendar/api/quickstart/python?hl=ru)
А необходимый для задачи запрос представлен ниже:

```Python
# Convert start and end dates to UTC format and add 'Z' at the end to indicate UTC time
start_date_utc = start_date.isoformat() + 'Z'
end_date_utc = end_date.isoformat() + 'Z'

# Request events in the specified date range
events_result = service.events().list(calendarId='[your_calendar_id]',
                                      timeMin=start_date_utc,
                                      timeMax=end_date_utc,
                                      singleEvents=True,
                                      orderBy='startTime').execute()
events = events_result.get('items', [])

# Check if there are any events in the specified range
if not events:
    print('No events found in the specified range.')
else:
    # Loop through each event in the list of events
    for event in events:
        try:
            # Try to convert the event name to an integer using the extract_numbers function
            event_name_as_int = int(extract_numbers(event['summary']))
            # If successful, add the integer value to the salary list
            salary.append(event_name_as_int)
        except ValueError:
            # If it cannot be converted to a number, skip the event
            pass

# Calculate and print the sum of the salary values
print('Total salary:', sum(salary))
```


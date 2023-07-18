import telebot
import subprocess

allowed_user_id = ' '


def restricted(func):
    def wrapped(message):
        user_id = message.from_user.id
        if user_id == allowed_user_id:
            return func(message)
        else:
            bot.reply_to(message, "У вас нет доступа к этому боту. Извините.")

    return wrapped


bot = telebot.TeleBot(' ')


@bot.message_handler(content_types=['text'])
@restricted
def get_text_messages(message):
    if message.text == '/start':
        bot.send_message(message.from_user.id,
                         "/previous_salary - Показывает информацию о заработной плате за предыдущие две недели. \n/salary - Выводит информацию о заработной плате за текущий период. ")
    elif message.text == '/previous_salary':
        # Run main2.py as a subprocess and get the output (stdout)
        result = subprocess.run(['python', 'Schedule.py', str(0)], capture_output=True, text=True)
        # Process the output and retrieve the value of the variable
        try:
            variable_value = result.stdout.strip()
            bot.send_message(message.from_user.id, f"Зарплата за предыдущие две недели была в размере {variable_value}₽")
        except ValueError:
            print("Ошибка: невозможно преобразовать значение в число.")
    elif message.text == '/salary':
        # Run main2.py as a subprocess and get the output (stdout)
        result = subprocess.run(['python', 'Schedule.py', str(1)], capture_output=True, text=True)
        # Process the output and retrieve the value of the variable
        try:
            variable_value = result.stdout.strip()
            bot.send_message(message.from_user.id, f"Зарплата за текущий период будет в размере {variable_value}₽")
        except ValueError:
            print("Ошибка: невозможно преобразовать значение в число.")
    elif message.text == '/help':
        bot.send_message(message.from_user.id, f" Если у вас возникнут вопросы или нужна дополнительная помощь, не стесняйтесь обратиться к администратору: ")
    else:
        bot.send_message(message.from_user.id, f"{message.from_user.id}")


bot.polling(none_stop=True, interval=0)

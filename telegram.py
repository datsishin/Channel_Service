import os
import telebot
from datetime import datetime as dt
from dotenv import load_dotenv

load_dotenv()

nl = '\n'

bot = telebot.TeleBot(os.getenv('TELEGRAM_API_TOKEN'))
chat_id = int(os.getenv('USER_ID'))


def send_notification(list_of_expired_orders: list):
    # current_time = dt.today()
    #
    # if current_time.hour == 10 and current_time.minute == 0:
    extra_text = ''
    for i in range(0, len(list_of_expired_orders)):
        extra_text += f'Номер заказа {list_of_expired_orders[i][0]},' \
                      f' срок поставки {list_of_expired_orders[i][3]}{nl}'

    text = f'По следующим заказами прошел срок поставки:{nl}{nl}' \
           f'{extra_text}'
    bot.send_message(chat_id, text=text)
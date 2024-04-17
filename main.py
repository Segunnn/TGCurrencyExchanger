import os
import telebot
from sys import stderr
from loguru import logger
from dotenv import load_dotenv

from extensions import ExchangeCurrencyAPI
from constants import GREETING_MESSAGE, CURRENCYS_LIST


load_dotenv()
app = telebot.TeleBot(os.getenv("TOKEN"))
logger.remove(0)
logger.add(stderr, format="<k><b>{time:YYYY-MM-DD HH:mm:ss}</b></k> <c><lvl>{level}</lvl></c>      <m>{name}</m> <w><i>{message}</i></w>")



@app.message_handler(commands = ['start', 'help'])
def start(message: telebot.types.Message):
    app.send_message(message.chat.id, GREETING_MESSAGE.format(message.from_user.first_name))

@app.message_handler(commands = ['values', 'currencies'])
def currencies(message: telebot.types.Message):
    text = "Aviable currencies: "

    for key in CURRENCYS_LIST.keys():
        currency = f"{key} : {CURRENCYS_LIST[key]}"
        text = '\n'.join((text, currency))
    
    app.reply_to(message, text)

@app.callback_query_handler(func=lambda call: True)
def callback_query(call: telebot.types.CallbackQuery):

    if call.data[:3] in CURRENCYS_LIST.values():
        # Answer as a notification
        app.answer_callback_query(call.id, f"{call.data} clicked")

        # Answer as message
        base, amount = call.data.split(" ")
        result = ExchangeCurrencyAPI.convert(base, amount)

        answer_text = f"*{amount} {base} is equals to..* "
        for x in result:
            key, value = x.items()
            answer_text = '\n'.join((answer_text, f" *{round(value[1], 2)}* {key[1]},"))

        app.send_message(call.message.chat.id, answer_text, parse_mode="markdown")
        

@app.message_handler(commands = ['convert', 'exchange'])
def convert(message: telebot.types.Message):
    try:
        arg = int(message.text.split()[1])
    except ValueError:
        app.send_message(message.chat.id, text="*Non numeric argument was detected in command.*", parse_mode="markdown")
        return 0
    except IndexError:
        app.send_message(message.chat.id, text="*Something went wrong, maybe you forgot about argument for this command.*", parse_mode="markdown")
        return 0

    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)

    for key, value in CURRENCYS_LIST.items():
        button = telebot.types.InlineKeyboardButton(text=f'{key} | {value}', callback_data=f'{value} {arg}')
        keyboard.add(button)
    
    app.send_message(message.chat.id, text="Choose currency that you want to exchange into other", reply_markup=keyboard)


if __name__ == "__main__":
    logger.info('Starting app..')
    app.infinity_polling()
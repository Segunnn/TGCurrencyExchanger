import os
import os.path
from sys import stderr
from loguru import logger
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, executor

from extensions import CurrencyAPI, ApiError, BaseCurrencyError, QuoteCurrencyError
from constants import GREETING_MESSAGE


load_dotenv()

app = Bot(os.getenv("TOKEN"))
dp = Dispatcher(app)
# Improve our logger style
logger.remove(0)
logger.add(stderr, format="<k><b>{time:YYYY-MM-DD HH:mm:ss}</b></k> <c><lvl>{level}</lvl></c>      <m>{name}</m> <w><i>{message}</i></w>")

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply(GREETING_MESSAGE.format(message.from_user.first_name))

@dp.message_handler(commands = ['convert', 'exchange'])
async def convert(message: types.Message):
    _, base, amount, *quote = message.text.split()

    try:
        amount = int(amount)
    except ValueError:
        await message.reply(text="*Non numeric argument was detected in command.*", parse_mode="markdown")
        return 0
    except IndexError:
        await message.reply(text="*Something went wrong, maybe you forgot about argument for this command.*", parse_mode="markdown")
        return 0

    try:
        result = CurrencyAPI.convert(base, amount, quote)
    
    except ApiError as err:
        await message.reply(text=f"**Something went wrong**\nError message:\n `{err.args[0]}`", parse_mode="markdown")
        return 0
    except BaseCurrencyError as err:
        await message.reply(text=f"**Something went wrong**\nError message:\n `{err.args[0]}`", parse_mode="markdown")
        return 0
    except QuoteCurrencyError as err:
        await message.reply(text=f"**Something went wrong**\nError message:\n `{err.args[0]}`", parse_mode="markdown")
        return 0
    
    await message.reply(text=f"Result:\n{result}")


if __name__ == "__main__":
    logger.info('Checking if currencies file exists..')
    if not os.path.isfile("currs.txt"):
        logger.info('File not found, creating..')
        CurrencyAPI.get_aviable_currencys_in_file()

    logger.info('Checking id .env file exists..')    
    if not os.path.isfile('.env'):
        logger.info("File not found, creating...")
        with open('.env', 'w') as f:
            f.write("TOKEN=\"\" \nAPI_KEY=\"\"")
        logger.critical("Please, fill the .env file befor starting")
        exit(1)

    logger.info('Starting app..')
    executor.start_polling(dp, skip_updates=True)
import requests
import currencyapicom
from os import getenv
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class ApiError(Exception):
    @property
    def message(self):
        return "API Error"

class BaseCurrencyError(Exception):
    @property
    def message(self):
        return "Base Currency Error"

class QuoteCurrencyError(Exception):
    @property
    def message(self):
        return "Quote Currency Error"

class CurrencyAPI():
    """
    ##### Convert values with `convert()` method
    """
    _client = currencyapicom.Client(getenv("API_KEY"))

    @classmethod
    def get_aviable_currencys_in_file(cls) -> None:
        """
        ### Returns 
        ```
        dict[ dict[str : str] ]
        ```
        """

        currs: dict = cls._client.currencies()

        with open("currs.txt", "w+") as f:
            f.write(str(currs))
    
    @classmethod
    def convert(cls, 
                base: str, 
                amount: int | str | float, 
                quotes: str | list[str] | tuple[str]) -> list[dict]:
        """
        ### Returns 
        ```
        list[dict[
                'code': 'value'
            ]]
        ```
        ### Paremeters
        `base: str` - currency code (USD, EUR) etc.,
        `amount: int` - amount,
        `quote: tuple` - target currencies
        """

        # В этой функции генерируется список валют чтобы вставить его в ссылку
        url = "https://api.currencyapi.com/v3/latest?apikey=cur_live_sXKMGzbDxoSevZQMZwd4Q8mh792kb7P7W8Pfgogx&currencies={}&base_currency={}"
        
        # Разделяем все валюты "%2C"
        with open("currs.txt", "r") as f:
            currencies = eval(f.read())

        if not currencies:
            raise BaseCurrencyError("One of the currencies are invalid")

        currencies = currencies['data'].keys()

        base = base.upper()

        if base not in currencies:
            logger.error("Base not in aviable currencies")
            raise BaseCurrencyError(f"{base} in not aviable currency")
        
        for i, cur in enumerate(quotes):
            quotes[i] = cur = cur.upper()
            if cur not in currencies:
                logger.error("Quote not in aviable currencies")
                raise QuoteCurrencyError(f"{cur} in not aviable currency")
            
        quote: str = "%2C".join(quotes)
        url = url.format(quote, base)

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)
            raise ApiError("Something went wrong with your requests, try again")

        response = response.json()
        result = list()

        for key, value in response['data'].items():
            result.append({
                value['code']: value['value'] * amount
            })

        return result
        
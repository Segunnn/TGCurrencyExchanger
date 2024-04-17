import json
import requests
from constants import CURRENCYS_LIST


class ApiError(Exception):
    @property
    def message(self):
        return "API Error"

class ExchangeCurrencyAPI():
    """
    ##### Convert values with `convert()` method
    """
    @staticmethod
    def currencies_list_generator(currencies: list) -> str:
        result = ""
        for currency in currencies:
            # %2C - разделитель
            result = '%2C'.join((result,currency))
        return result[3:]
    
    @staticmethod
    def convert(base: str, amount: int) -> list[dict]:
        """
        ### Returns 
        ```
        list[dict[
                'code': str, 
                'value': int
            ]]
        ```
        ### Paremeters
        `base: str` - currency code (USD, EUR) etc.,
        `amount: int` - amount 
        """

        # В этой функции генерируется список валют чтобы вставить его в ссылку
        currencies = ExchangeCurrencyAPI.currencies_list_generator(CURRENCYS_LIST.values())

        # Base - валюта, стоимость которой будут смотреть относительно currencies
        conn_string = "https://api.currencyapi.com/v3/latest?apikey=cur_live_sXKMGzbDxoSevZQMZwd4Q8mh792kb7P7W8Pfgogx&currencies={}&base_currency={}"
        
        if (base in CURRENCYS_LIST.values()):
            req: requests.Response = requests.get(conn_string.format(currencies, base))
            content: dict = eval(req.content.decode())['data']
            
            result = list()
            for x in content.values():
                # Т.к в какой-то момент amount становится str, int(amount) - необходимо
                x['value'] = x['value']*int(amount) 
                result.append(x)

            return result
        else:
            raise ApiError(f"Invalid currency detected")
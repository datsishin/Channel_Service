import time
from datetime import datetime as dt
import httplib2
import requests as r
import xmltodict
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from db_connect import insert_data
from telegram import send_notification

start_time = time.time()


def auth():
    # Файл, полученный в Google Developer Console
    CREDENTIALS_FILE = 'creds.json'
    # ID Google Sheets документа (можно взять из его URL)
    spreadsheet_id = '1pB9YZm2WAsioaIocoi9oH6yRKX6yPyD0NV5S22D4YWU'

    # Авторизуемся и получаем service — экземпляр доступа к API
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    with build('sheets', 'v4', http=httpAuth) as service:
        values = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='A2:D',
        ).execute()

        data_processor(values)


def data_processor(values):
    initial_data = values['values']
    dict_of_quotes = get_date_range(initial_data)

    list_of_orders = []

    for i in range(0, len(initial_data)):

        order_number = int(initial_data[i][1])
        cost_usd = int(initial_data[i][2])
        delivery_date = str(initial_data[i][3])

        if delivery_date in dict_of_quotes:
            cost_rub = round(cost_usd * float(dict_of_quotes[delivery_date]), 2)
            tuple_data = (order_number, cost_usd, cost_rub, delivery_date)
            list_of_orders.append(tuple_data)

        else:
            url = 'https://cbr.ru/scripts/XML_daily.asp'
            params = {'date_req': delivery_date}
            response = r.get(url, params=params)
            items_of_currency = xmltodict.parse(response.content)['ValCurs']['Valute']
            for _ in range(0, len(items_of_currency)):

                if items_of_currency[_]['@ID'] == 'R01235':
                    value = float(items_of_currency[_]['Value'].replace(',', '.'))
                    dict_of_quotes[delivery_date] = value
                    cost_rub = round(cost_usd * value, 2)
                    tuple_data = (order_number, cost_usd, cost_rub, delivery_date)
                    list_of_orders.append(tuple_data)

    insert_data(list_of_orders)
    check_deadlines(list_of_orders)


def check_deadlines(list_of_orders: list):
    list_of_expired_orders = []
    today = dt.today().date()

    for i in list_of_orders:
        delivery_date = dt.strptime(i[3], '%d.%m.%Y').date()

        if delivery_date < today:
            list_of_expired_orders.append(i)

    if list_of_expired_orders:
        # print(f'Просроченных заказов – {len(list_of_expired_orders)}')
        send_notification(list_of_expired_orders)


def get_date_range(items: list) -> dict:
    list_of_date = []
    for _ in range(0, len(items)):
        item = dt.strptime(items[_][3], '%d.%m.%Y').date()
        list_of_date.append(item)

    start_range = dt.strftime(min(list_of_date), "%d/%m/%Y")
    end_range = dt.strftime(max(list_of_date), "%d/%m/%Y")

    return get_currency(start_range, end_range)


def get_currency(start_range: str, end_range: str) -> dict:
    url = 'http://www.cbr.ru/scripts/XML_dynamic.asp'
    params = {'date_req1': start_range,
              'date_req2': end_range,
              'VAL_NM_RQ': 'R01235'}

    response = r.get(url, params=params)
    data = xmltodict.parse(response.content)
    items = data['ValCurs']['Record']
    exchange_rate_by_date = {}

    for i in range(0, len(items)):
        date = items[i]['@Date']
        value = float(items[i]['Value'].replace(',', '.'))
        exchange_rate_by_date[date] = value

    return exchange_rate_by_date


while True:
    auth()
    time.sleep(60)

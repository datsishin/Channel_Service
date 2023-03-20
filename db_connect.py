import psycopg2
from psycopg2 import Error


def connect():
    try:
        connection = psycopg2.connect(
            user="postgres",
            password="1234",
            host="127.0.0.1",
            port="5432",
            database="postgres")
        connection.autocommit = True

        cursor = connection.cursor()
        return cursor

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)


def insert_data(list_of_orders: list):
    cursor = connect()
    cursor.execute("DELETE FROM orders")
    db_insert_data = "INSERT INTO orders(order_number, cost_usd, cost_rub, delivery_date) " \
                     "VALUES(%s, %s, %s, %s);"

    for item in list_of_orders:
        cursor.execute(db_insert_data, item)
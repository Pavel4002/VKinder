"""
new users - таблица новых пользователей
seen users - просмотренные пользователи
data new users - добавить новых пользователей в таблицу
data viewed users - данные в таблицу просмотренных пользователей
select - перебор пользователей
drop new users(viewed users) - удаление таблиц
"""

import psycopg2
from config import *

connection = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=db_name,
    port=port
)

connection.autocommit = True

def create_new_users():
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS new_users(
                id serial,
                first_name varchar(70) NOT NULL,
                last_name varchar(70) NOT NULL,
                vk_id varchar(20) NOT NULL PRIMARY KEY,
                vk_link varchar(100));"""
        )
    print("Таблица NEW_USERS создана.")


def create_viewed_users():
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS viewed_users(
            id serial,
            vk_id varchar(50) PRIMARY KEY);"""
        )
    print("[INFO] Table VIEWED_USERS was created.")


def insert_new_users(first_name, last_name, vk_id, vk_link):
    with connection.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO new_users (first_name, last_name, vk_id, vk_link) 
            VALUES ('{first_name}', '{last_name}', '{vk_id}', '{vk_link}');"""
        )


def insert_viewed_users(vk_id, offset):
    with connection.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO viewed_users (vk_id) 
            VALUES ('{vk_id}')
            OFFSET '{offset}';"""
        )


def select(offset):
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT u.first_name,
                        u.last_name,
                        u.vk_id,
                        u.vk_link,
                        su.vk_id
                        FROM users AS u
                        LEFT JOIN seen_users AS su 
                        ON u.vk_id = su.vk_id
                        WHERE su.vk_id IS NULL
                        OFFSET '{offset}';"""
        )
        return cursor.fetchone()


def drop_new_users():
    with connection.cursor() as cursor:
        cursor.execute(
            """DROP TABLE IF EXISTS new_users CASCADE;"""
        )
        print('[INFO] Table NEW_USERS was deleted.')


def drop_viewed_users():
    with connection.cursor() as cursor:
        cursor.execute(
            """DROP TABLE  IF EXISTS viewed_users CASCADE;"""
        )
        print('[INFO] Table VIEWED_USERS was deleted.')


def drop_black_users():
    with connection.cursor() as cursor:
        cursor.execute(
            """DROP TABLE  IF EXISTS black_list_users CASCADE;"""
        )
        print('[INFO] Table BLACK_LIST_USERS was deleted.')


def creating_database():
    drop_new_users()
    drop_viewed_users()
    create_new_users()
    create_viewed_users()

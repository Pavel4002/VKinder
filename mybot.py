"""
write_msg - метод отправки сообщений,
user_name - имя пользователя написавшего боту
get_sex - получить пол пользователя и заменить противоположным
get_age - получить возраст пользователя
cities - получить ID города пользователя
find_city - информация о городе пользователя
find_user - поиск по данным
get_photo_id - получить ID фотографии
get_photo - получить фотографии
send_photo - отправить фотографии
find_users - найти пользователя
found_user_info - информация о найденном пользователе
user_id - ID найденного пользователя
"""

from config import TOKEN_APP, TOKEN_API, offset, line
import vk_api
import requests
import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange
from dbase import *


class VKBot:
    def __init__(self):
        self.vk = vk_api.VkApi(token=TOKEN_API)
        self.longpoll = VkLongPoll(self.vk)
        self.url: str = f'https://api.vk.com/method/'
        self.params = {"access_token": TOKEN_APP,
                       'v': '5.131'
                       }

    def write_msg(self, user_id, message):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'message': message,
                                         'random_id': randrange(10 ** 7)})

    def user_name(self, user_id):
        repl = requests.get(self.url + 'users.get', params={**self.params,
                                                            'user_ids': user_id
                                                            })
        response = repl.json()

        try:
            information_dict = response['response']
            for i in information_dict:
                for key, value in i.items():
                    first_name = i.get('first_name')
                    return first_name
        except Exception:
            self.write_msg(user_id, 'Ошибка ввода данных')

    def get_sex(self, user_id):
        repl = requests.get(self.url + 'users.get', params={**self.params,
                                                           'user_ids': user_id,
                                                           'fields': 'sex'
                                                           })
        response = repl.json()
        try:
            information_list = response['response']
            for i in information_list:
                if i.get('sex') == 2:
                    find_sex = 1
                    return find_sex
                elif i.get('sex') == 1:
                    find_sex = 2
                    return find_sex
        except Exception:
            self.write_msg(user_id, 'Ошибка данных')

    def get_age(self, user_id):
        repl = requests.get(self.url + 'users.get', params={**self.params,
                                                            'user_ids': user_id,
                                                            'fields': 'bdate'
                                                            })
        response = repl.json()
        try:
            information_list = response['response']
            for i in information_list:
                date = i.get('bdate')
            date_list = date.split('.')
            if len(date_list) == 3:
                year = int(date_list[2])
                year_now = int(datetime.date.today().year)
                return year_now - year
            elif len(date_list) == 2 or date not in information_list:
                self.write_msg(user_id, 'Введите возраст ')
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        age = event.text
                        if age.isdigit():
                            age = int(age)
                            if 18 <= age <= 70:
                                return age
                            else:
                                self.write_msg(user_id, 'Возраст от 18 до 70 ')
        except Exception:
            self.write_msg(user_id, 'Ошибка ввода данных')

    def cities(self, user_id, city_name):
        repl = requests.get(self.url + 'database.getCities', params={**self.params,
                                                                     'country_id': 1,
                                                                     'q': f'{city_name}',
                                                                     'need_all': 0,
                                                                     'count': 1000
                                                                     })
        response = repl.json()
        try:
            information_list = response['response']
            list_cities = information_list['items']
            for i in list_cities:
                found_city_name = i.get('title')
                if found_city_name == city_name:
                    found_city_id = i.get('id')
                    return int(found_city_id)
        except Exception:
            self.write_msg(user_id, 'Ошибка поиска данных')

    def find_city(self, user_id):
        repl = requests.get(self.url + 'users.get', params={**self.params,
                                                            'fields': 'city',
                                                            'user_ids': user_id
                                                            })
        response = repl.json()
        try:
            information_dict = response['response']
            for i in information_dict:
                if 'city' in i:
                    city = i.get('city')
                    id = str(city.get('id'))
                    return id
                elif 'city' not in i:
                    self.write_msg(user_id, 'Введите город: ')
                    for event in self.longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            city_name = event.text
                            id_city = self.cities(user_id, city_name)
                            if id_city != '' or id_city != None:
                                return str(id_city)
                            else:
                                break
        except Exception:
            self.write_msg(user_id, 'Ошибка ввода данных')

    def find_user(self, user_id):
        resp = requests.get(self.url + 'users.search', params={**self.params,
                                                               'sex': self.get_sex(user_id),
                                                               'age_from': self.get_age(user_id),
                                                               'age_to': self.get_age(user_id),
                                                               'city': self.find_city(user_id),
                                                               'fields': 'is_closed, id, first_name, last_name',
                                                               'status': '1' or '6',
                                                               'count': 500
                                                               })
        resp_json = resp.json()
        try:
            dict_1 = resp_json['response']
            list_1 = dict_1['items']
            for person_dict in list_1:
                if person_dict.get('is_closed') == False:
                    first_name = person_dict.get('first_name')
                    last_name = person_dict.get('last_name')
                    vk_id = str(person_dict.get('id'))
                    vk_link = 'vk.com/id' + str(person_dict.get('id'))
                    insert_new_users(first_name, last_name, vk_id, vk_link)
                else:
                    continue
            return f'Поиск завершён'
        except Exception:
            self.write_msg(user_id, 'Ошибка поиска по данным')

    def get_id_photo(self, user_id):
        url = self.url + 'photos.get'
        resp = requests.get(url, params={**self.params,
                                         'album_id': 'profile',
                                         'owner_id': user_id,
                                         'extended': 'likes',
                                         'feed_type': 'photo_tag',
                                         'count': 25
                                         })
        dict_photos = dict()
        resp_json = resp.json()
        try:
            dict_1 = resp_json['response']
            list_1 = dict_1['items']
            for i in list_1:
                photo_id = str(i.get('id'))
                i_likes = i.get('likes')
                if i_likes.get('count'):
                    likes = i_likes.get('count')
                    dict_photos[likes] = photo_id
            list_of_ids = sorted(dict_photos.items(), reverse=True)
            return list_of_ids
        except Exception:
            self.write_msg(user_id, 'Ошибка получения ID фото')

    def get_1photo(self, user_id):
        list = self.get_id_photo(user_id)
        count = 0
        for i in list:
            count += 1
            if count == 1:
                return i[1]

    def get_2photo(self, user_id):
        list = self.get_id_photo(user_id)
        count = 0
        for i in list:
            count += 1
            if count == 2:
                return i[1]

    def get_3photo(self, user_id):
        list = self.get_id_photo(user_id)
        count = 0
        for i in list:
            count += 1
            if count == 3:
                return i[1]

    def send_1photo(self, user_id, message, offset):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'access_token': TOKEN_APP,
                                         'message': message,
                                         'attachment': f'photo{self.user_id(offset)}_{self.get_1photo(self.user_id(offset))}',
                                         'random_id': 0})

    def send_2photo(self, user_id, message, offset):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'access_token': TOKEN_APP,
                                         'message': message,
                                         'attachment': f'photo{self.user_id(offset)}_{self.get_2photo(self.user_id(offset))}',
                                         'random_id': 0})

    def send_3photo(self, user_id, message, offset):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'access_token': TOKEN_APP,
                                         'message': message,
                                         'attachment': f'photo{self.user_id(offset)}_{self.get_3photo(self.user_id(offset))}',
                                         'random_id': 0})

    def find_users(self, user_id, offset):
        self.write_msg(user_id, self.found_user_info(offset))
        self.user_id(offset)
        insert_viewed_users(self.user_id(offset), offset)
        self.get_id_photo(self.user_id(offset))
        self.send_1photo(user_id, '1 Фото', offset)
        if self.get_2photo(self.user_id(offset)) != None:
            self.send_2photo(user_id, '2 Фото', offset)
            self.send_3photo(user_id, '3 Фото', offset)
        else:
            self.write_msg(user_id, f'Это всё!')

    def found_user_info(self, offset):
        tuple_person = select(offset)
        list_person = []
        for i in tuple_person:
            list_person.append(i)
        return f'{list_person[0]} {list_person[1]}, ссылка - {list_person[3]}'

    def user_id(self, offset):
        tuple_person = select(offset)
        list_person = []
        for i in tuple_person:
            list_person.append(i)
        return str(list_person[2])


bot = VKBot()

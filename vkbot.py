from keyboard import sender
from mybot import *


for event in bot.longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        user_id = str(event.user_id)
        msg = event.text.lower()
        sender(user_id, msg.lower())
        if request == 'поиск':
            creating_database()
            bot.write_msg(user_id, f'Привет, {bot.user_name(user_id)}')
            bot.find_user(user_id)
            bot.write_msg(event.user_id, f'Собеседник найден')
            bot.find_users(user_id, offset)

        elif request == 'новая анкета':
            for i in line:
                offset += 1
                bot.find_users(user_id, offset)
                break

        else:
            bot.write_msg(event.user_id, 'Выражайтесь яснее')

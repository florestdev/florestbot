# -*- coding: utf-8 -*-

admins = [] # список админов. (их ID в Telegram)
token = '' # токен Вашего бота, который можно узнать в BotFather.
telegram_channel_id = '' # ID вашего Telegram канала, или чата, где у бота есть права администратора.
proxies = {} # прокси, которые используются ботом. Оставьте пустой словарь, если прокси отсутствует. Пример использования прокси: {"socks5":"http://IP прокси:порт", 'socks5':"http://IP прокси:порт"}
headers_for_html_requests = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36', 'Accept-Language': 'ru-RU'} # Юзер агент, а также язык, на котором будут возвращаться данные при парсинге любого сайта.

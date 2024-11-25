# -*- coding: utf-8 -*-

admins = [] # список админов. (их ID в Telegram)
token = '' # токен Вашего бота, который можно узнать в BotFather.
telegram_channel_id = '' # ID вашего Telegram канала, или чата, где у бота есть права администратора.
proxies = {} # прокси, которые используются ботом. Оставьте пустой словарь, если прокси отсутствует. Пример использования прокси: {"socks5":"http://IP прокси:порт", 'socks5':"http://IP прокси:порт"}
headers_for_html_requests = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36', 'Accept-Language': 'ru-RU'} # Юзер агент, а также язык, на котором будут возвращаться данные при парсинге любого сайта.
google_api_key = None # Сюда введите токен от Google APIs для того, чтобы можно было узнать данные о канале, или узнать данные о видео при скачивании. Токен можно получить тут: https://developers.google.com/identity/oauth2/web/guides/get-google-api-clientid (заходить с VPN)
gigachat_token = '' # токен от GigaChat API (ПАО "СберБанк")

# -*- coding: utf-8 -*-
import g4f.Provider
import telebot, asyncio, aiohttp
from telebot import TeleBot, types
import time, pathlib, sys, logging
import random, os
from config import *
from qrcode import make as create_qr
import string, requests, threading
import io
from gtts import gTTS
from telebot.util import quick_markup
from PIL import Image, ImageDraw, ImageFont, ImageOps
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from pytubefix import Channel, YouTube, Search, Playlist
import xml.etree.ElementTree as ET
import faker as faker_
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import hashlib
from virus_total_apis import PublicApi as VirusTotalPublicApi
import speech_recognition as sr
import subprocess
from vkpymusic import Service, TokenReceiver, Song
import vk_api
import zipfile, shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as Service1
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from tqdm.asyncio import tqdm
import numpy
import cv2
from yoloface import face_analysis
from mcstatus import JavaServer
import base64
from g4f.client import Client
import g4f
from g4f.Provider import OIVSCodeSer2, Blackbox, Chatai, LegacyLMArena, PollinationsAI, RetryProvider, ARTA, PollinationsImage, DeepInfraChat
from g4f.Provider.Together import Together
import pyttsx3
from tqdm import tqdm as sync_tqdm
import tqdm
import yt_dlp
from moviepy import VideoFileClip
from telethon.sync import TelegramClient
import socks
import pandas as pd
from telethon.errors import FloodWaitError
from telethon.types import UserStatusRecently, UserStatusEmpty, UserStatusLastMonth, UserStatusLastWeek, UserStatusOnline, UserStatusOffline
from datetime import datetime
from openai import OpenAI
import json
from typing import Any, Dict
import feedparser
from newspaper import Article

def _format_value(value: Any, indent: int = 0) -> str:
    """Рекурсивно форматирует любое значение для отчёта."""
    pad = "    " * indent  # 4 пробела на уровень
    if isinstance(value, dict):
        if not value:
            return f"{pad}- (пусто)"
        lines = []
        for k, v in value.items():
            lines.append(f"{pad}{k}:")
            lines.append(_format_value(v, indent + 1))
        return "\n".join(lines)
    elif isinstance(value, list):
        if not value:
            return f"{pad}- (пусто)"
        lines = []
        for i, item in enumerate(value, 1):
            lines.append(f"{pad}- [{i}]")
            lines.append(_format_value(item, indent + 1))
        return "\n".join(lines)
    else:
        return f"{pad}{value if value not in [None, ''] else '(нет данных)'}"

def parse_vk_user_data(data: Dict[str, Any]) -> str:
    """Создает подробный текстовый отчет из профиля ВКонтакте."""
    if not isinstance(data, dict):
        raise TypeError("Аргумент должен быть словарём.")

    id_ = data.get("id")
    first_name = data.get("first_name", "(нет имени)")
    last_name = data.get("last_name", "(нет фамилии)")
    domain = data.get("domain", f"id{id_}")
    profile_link = f"https://vk.com/{domain}"

    report = [
        f"👤 Профиль VK: {first_name} {last_name}",
        f"🔗 Ссылка: {profile_link}",
        f"🆔 ID: {id_}",
        ""
    ]

    # Пробегаемся по всем полям (чтобы ничего не пропустить)
    for key, value in sorted(data.items()):
        # Пропускаем уже выведенные поля
        if key in {"id", "first_name", "last_name", "domain"}:
            continue
        report.append(f"▶ {key}: {_format_value(value, 1)}")
        report.append("")

    return "\n".join(report)

bot = TeleBot(token=token)
path = pathlib.Path(sys.argv[0]).parent.resolve()
users = []
admins = [7455363246]
buttons = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Генерация информации, паролей и т.д.', callback_data='gen_info-btns'), types.InlineKeyboardButton('Деанончик', callback_data='deanon_btns'), types.InlineKeyboardButton('Утилиты', callback_data='utilits_btns'), types.InlineKeyboardButton('ИИ, текст в речь, картинки', callback_data='ai_btns'), types.InlineKeyboardButton('Парсеры', callback_data='youtube_funcs_btns'), types.InlineKeyboardButton('Игры', callback_data='games'))
gen_info_btns = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Сгенерировать QR код', callback_data='generate_qr'), types.InlineKeyboardButton('Сгенирировать пароль', callback_data='generate_password'), types.InlineKeyboardButton('Топ песни с чартов', callback_data='download-audio-from-youtube'),  types.InlineKeyboardButton('Цена крипты', callback_data='crypto-price'), types.InlineKeyboardButton('Проверить пароль на утечки', callback_data='password_check'), types.InlineKeyboardButton('Фейковая личность', callback_data='fake_human'), types.InlineKeyboardButton('Назад', callback_data='back_to_menu'))
deanon_btns = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Информация по IP', callback_data='information_about_ip'), types.InlineKeyboardButton('Деанон по фото', callback_data='deanon_by_photo'), types.InlineKeyboardButton('Назад', callback_data='back_to_menu'))
utilits_btns = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Погода', callback_data='weather-info'), types.InlineKeyboardButton('Затемнить фотографию', callback_data='black-photo-make'), types.InlineKeyboardButton('Создать демотиватор', callback_data='demotivator-create'), types.InlineKeyboardButton('Предложить новость', callback_data='predloshka'), types.InlineKeyboardButton('Узнать ИМТ', callback_data='imt_check'), types.InlineKeyboardButton('Отправить письмо через бота', callback_data='send-mail-by-bot'), types.InlineKeyboardButton('Рассылка по E-Mail', callback_data='make-email-rassylka'), types.InlineKeyboardButton('Проверка на вирусы', callback_data='virus-check'), types.InlineKeyboardButton('Добавить водяной знак (текст)', callback_data='add_watermark_on_photo'), types.InlineKeyboardButton('Сократить ссылку (clck.ru)', callback_data='cut-link-clck-yandex'), types.InlineKeyboardButton('Разархивировать APK | JAR', callback_data='unzip_apk_or_jar'), types.InlineKeyboardButton('Из .zip в .apk', callback_data='from-zip-to-apk'), types.InlineKeyboardButton('Конвертация изображений', callback_data='img-format-convertation'), types.InlineKeyboardButton('Назад', callback_data='back_to_menu'))
ai_btns = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Разговор с GPT-4o', callback_data='ai-text'), types.InlineKeyboardButton('Разговор с DeepSeek-v3', callback_data='deepseek-ai-usage'), types.InlineKeyboardButton('Нарисовать изображение', callback_data='ai-image'), types.InlineKeyboardButton('Из текста в речь', callback_data='text-to-speech'), types.InlineKeyboardButton('Из речи в текст', callback_data='speech-to-text'), types.InlineKeyboardButton('Нейро-апскейл (x4)', callback_data='ai-upscale-x4'), types.InlineKeyboardButton('Нейросетевые субтитры', callback_data='ai-subtitles-video'), types.InlineKeyboardButton('Назад', callback_data='back_to_menu'))
parsers = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Подробная информация о YouTube канале', callback_data='full_info_yt'), types.InlineKeyboardButton('Скачать видео с YouTube', callback_data='download-video-from-yt'), types.InlineKeyboardButton('Найти видео по названию', callback_data='search_youtube_video'), types.InlineKeyboardButton('Скачать элементы плейлиста', callback_data='download-playlist-elements'), types.InlineKeyboardButton('Парсинг сайта', callback_data='parsing-site'), types.InlineKeyboardButton('Парсинг Google фото', callback_data='google-photo-parsing'), types.InlineKeyboardButton('Скачать музыку с VK', callback_data='vk_music_download'), types.InlineKeyboardButton('Последний пост в VK', callback_data='last_post_vk'), types.InlineKeyboardButton('Парсер Yandex (BETA)', callback_data='yandex_beta_parse'), types.InlineKeyboardButton('Получить API-токен', callback_data='get-api-token'), types.InlineKeyboardButton('Информация о Minecraft-сервере', callback_data='info-about-minecraft-server'), types.InlineKeyboardButton('Парсер Kwork', callback_data='parser-kwork'), types.InlineKeyboardButton('Скачать видео с TikTok', callback_data='tiktok-video-downloader'), types.InlineKeyboardButton('Скачать клип с Twitch', callback_data='twitch-clips-downloader'), types.InlineKeyboardButton('Парсер VK | RUTUBE | DZEN', callback_data='russian-trio-parsing'), types.InlineKeyboardButton('VK PROFILE PARSE', callback_data='vk-profile-info'), types.InlineKeyboardButton('Парсинг профилей Steam', callback_data='steam-profile-parsing'), types.InlineKeyboardButton('Последние новости', callback_data='last_news_meduza'), types.InlineKeyboardButton('Парсинг статьи', callback_data='parse_statii'), types.InlineKeyboardButton('Назад', callback_data='back_to_menu'))
games = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Сыграть в кликер', web_app=types.WebAppInfo('https://florestdev.github.io/clicker-html/')), types.InlineKeyboardButton("Змейка [NEW]", web_app=types.WebAppInfo("https://florestdev.github.io/snake-html/")), types.InlineKeyboardButton("Назад", callback_data="back_to_menu"))
client_for_gpt = Client()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
sambanova_api = OpenAI(api_key=sambanova_api_key, base_url="https://api.sambanova.ai/v1")
PIL_FORMATS_MAP = {
    '.jpg': 'JPEG', '.jpeg': 'JPEG',
    '.png': 'PNG',
    '.bmp': 'BMP',
    '.gif': 'GIF',
    '.webp': 'WEBP'
}

os.chdir(path)

def parse_statii(message: types.Message):
    def article_parsing(url: str):
        """Парсинг статьи через прокси. Возвращает ArticleInfo."""
        try:
            # создаём объект newspaper
            article = Article(url)

            # КАСТОМНАЯ ЗАГРУЗКА через прокси
            r = requests.get(
                article.url,
                proxies=proxies,
                headers=headers_for_html_requests,
                timeout=12
            )
            if r.status_code != 200 or not r.text.strip():
                return None

            # вручную подсовываем html newspaper'у
            article.html = r.text
            article.download_state = 2  # SUCCESS

            # парсим
            article.parse()

            return {
                "title": article.title,
                "text": article.text[:3000],
                "top_image": article.top_image
            }

        except Exception as e:
            print("proxy parsing error:", e)
            return None
    article = article_parsing(message.text)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Назад', callback_data='back'))
    if not article:
        bot.reply_to(message, f'Не получилось получить доступ к статье.', reply_markup=markup)
    else:
        if article.get("top_image"):
            try:
                bot.send_photo(
                    chat_id=message.chat.id,
                    photo=requests.get(article.get('top_image'), proxies=proxies, headers=headers_for_html_requests).content,
                    caption=f'**{article.get("title")}**\n\n{article.get("text")}',
                    reply_to_message_id=message.id,
                    parse_mode='Markdown'
                )
            except:
                bot.send_photo(message.chat.id, requests.get(article.get('top_image'), proxies=proxies, headers=headers_for_html_requests).content)
                bot.send_message(message.chat.id, f'**{article.get("title")}**\n\n{article.get("text")}', reply_to_message_id=message.id, parse_mode='Markdown')
        else:
            bot.send_photo(message.chat.id, f'**{article.get("title")}**\n\n{article.get("text")}', reply_to_message_id=message.id, parse_mode='Markdown')

def steam_profile_parsing(message: types.Message):
    def fetch_profile_xml_by_vanity(vanity: str):
        # Проверяем: vanity или SteamID64 (числовой)
        if vanity.isdigit():
            url = f"https://steamcommunity.com/profiles/{vanity}/?xml=1"
        else:
            url = f"https://steamcommunity.com/id/{vanity}/?xml=1"

        try:
            r = requests.get(url, timeout=10, headers={
                "User-Agent": "steam-profile-fetcher/1.0 (+https://example.com)"
            })
        except requests.RequestException:
            return None

        if r.status_code != 200:
            return None

        try:
            root = ET.fromstring(r.text)
        except ET.ParseError:
            return None

        data = {child.tag: child.text for child in root}
        if data.get('error'):
            return None
        return data
    
    def fetch_profile_xml_by_steamid(steamid64: str):
        url = f"https://steamcommunity.com/profiles/{steamid64}/?xml=1"
        try:
            r = requests.get(url, timeout=10, headers={"User-Agent": "steam-profile-fetcher/1.0 (+https://example.com)"})
        except requests.RequestException:
            return None
        if r.status_code != 200:
            return None
        try:
            root = ET.fromstring(r.text)
        except ET.ParseError:
            return None
        data = {child.tag: child.text for child in root}
        if data.get('error'):
            return
        return data

    profile = fetch_profile_xml_by_steamid(message.text.strip()) if message.text.isdigit() else fetch_profile_xml_by_vanity(message.text.strip())

    if not profile:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Назад', callback_data='back'))
        bot.reply_to(
            message,
            '❌ Профиль не найден. Проверьте правильность ника или SteamID, который вы ввели.',
            reply_markup=markup
        )
        return

    # Форматирование всех полей (всё, что Steam вернул)
    def safe_value(key):
        val = profile.get(key)
        return val if val not in [None, "", "null"] else "—"

    steam_id64 = safe_value('steamID64')
    steam_id = safe_value('steamID')
    realname = safe_value('realname')
    custom_url = safe_value('customURL')
    state = safe_value('stateMessage')
    online_state = safe_value('onlineState')
    privacy = safe_value('privacyState')
    visibility = safe_value('visibilityState')
    vac_banned = "Да" if profile.get('vacBanned') == "1" else "Нет"
    trade_ban = safe_value('tradeBanState')
    limited = "Да" if profile.get('isLimitedAccount') == "1" else "Нет"
    rating = safe_value('steamRating')
    hours_2w = safe_value('hoursPlayed2Wk')
    member_since = safe_value('memberSince')
    location = safe_value('location')
    headline = safe_value('headline')
    summary = safe_value('summary').replace("<br>", "\n")
    avatar = safe_value('avatarFull')

    text = (
        f"🎮 <b>Профиль Steam</b>\n\n"
        f"🆔 SteamID64: <code>{steam_id64}</code>\n"
        f"👤 Ник: {steam_id}\n"
        f"🖼️ Аватар: {avatar}\n"
        f"📛 Имя: {realname}\n"
        f"🔗 Vanity URL: {custom_url}\n"
        f"🌍 Локация: {location}\n"
        f"📅 Дата регистрации: {member_since}\n\n"
        f"💬 Статус: {state}\n"
        f"🟢 Состояние: {online_state}\n"
        f"🔒 Приватность: {privacy}\n"
        f"👁 Видимость: {visibility}\n\n"
        f"⚠️ VAC бан: {vac_banned}\n"
        f"🚫 Торговый бан: {trade_ban}\n"
        f"💰 Ограниченный аккаунт: {limited}\n\n"
        f"⭐ Рейтинг Steam: {rating}\n"
        f"⏱ Часы за 2 недели: {hours_2w}\n\n"
        f"📰 Заголовок: {headline}\n"
        f"📄 О себе:\n{summary}"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🔗 Открыть в Steam", url=f"https://steamcommunity.com/id/{custom_url or steam_id64}"),
        types.InlineKeyboardButton('Назад', callback_data='back')
    )
    try:
        bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)
    except:
        bot.reply_to(message, text, reply_markup=markup)


def get_vk_profile_info(message: types.Message):
    session = vk_api.VkApi(token=token_for_vk)
    api = session.get_api()
    fields = (
        "bdate,sex,city,country,home_town,photo_max_orig,"
        "followers_count,relation,contacts,domain,site,status,about,"
        "education,schools,universities,occupation,career,interests,"
        "activities,music,movies,tv,books,games,quotes,personal,connections"
    )
    result = api.users.get(user_ids=message.text, fields=fields)
    if result:
        info = parse_vk_user_data(result[0])
        bot.reply_to(message, f'Подробная информация о пользователе.\n\n{info}', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        bot.reply_to(message, f'Пользователь не найден.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def conv_image(message: types.Message, image: bytes):
    selected_format_button = message.text # Текст кнопки, например, ".jpg"
    selected_format_pil = PIL_FORMATS_MAP.get(selected_format_button.lower())

    if not selected_format_pil:
        bot.reply_to(message, "Неверный формат. Пожалуйста, выберите один из предложенных.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(types.KeyboardButton(".jpg"), types.KeyboardButton('.png'), types.KeyboardButton('.gif'), types.KeyboardButton('.bmp'), types.KeyboardButton('.webp')))
        # Перерегистрация обработчика для следующего ввода
        bot.register_next_step_handler(message, conv_image, image)
        return

    try:
        # Открываем изображение с помощью Pillow
        img = Image.open(io.BytesIO(image))

        # --- Логика Конвертации Изображения ---
        output_buffer = io.BytesIO()

        # Pillow может требовать преобразования цветового пространства для некоторых форматов
        if selected_format_pil == 'JPEG' and img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        # Для GIF, если нужно сохранить анимацию, потребуется более сложная обработка.
        # Здесь мы просто сохраним первый кадр или как обычное изображение.
        elif selected_format_pil == 'GIF':
            # Простая обработка GIF: сохранение первого кадра
            img.save(output_buffer, format=selected_format_pil)
        else:
            img.save(output_buffer, format=selected_format_pil)

        output_buffer.seek(0) # Перематываем буфер в начало
        converted_image_data = output_buffer.read()
        # --- Конец Логики Конвертации ---

        # Отправка сконвертированного изображения
        caption = f"Изображение конвертировано в {selected_format_button}"
        output_filename = f"converted_image{selected_format_button}" # Имя файла для отправки

        # Отправляем как фото, если формат поддерживается, иначе как документ
        # Note: Pillow может сохранять GIF, но telegram может отправлять его как документ.
        # Лучше всего проверить, какой метод предпочтительнее для разных форматов.
        # Отправляем как документ (для GIF, BMP или если фото слишком большое)
        bot.send_document(message.chat.id, (output_filename, converted_image_data), caption=caption, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

        bot.reply_to(message, "Можете прислать новое изображение.", reply_markup=types.ReplyKeyboardMarkup(True, input_field_placeholder=f'Сэр, да, сэр.', row_width=1).add(types.KeyboardButton('🏡В меню')))
    except Exception as e:
        print(f"Ошибка при конвертации/отправке изображения: {e}")
        bot.reply_to(message, "Произошла ошибка при конвертации изображения. Пожалуйста, попробуйте позже.", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def get_img_for_conv(message: types.Message):
    if not message.document:
        bot.reply_to(message, f'Нужно было прислать фотографию без сжатия в следующих форматах: .jpg, .png, .bmp, .gif, .webp.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        if not message.document.file_name.endswith(('.gif', '.jpg', '.jpeg', '.png', '.bmp', '.webp')):
            bot.reply_to(message, f'Нужно было прислать фотографию без сжатия в следующих форматах: .jpg, .png, .bmp, .gif, .webp.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        else:
            bot.reply_to(message, f'Получили фотографию! Выберите из доступных форматов: ', reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(types.KeyboardButton(".jpg"), types.KeyboardButton('.png'), types.KeyboardButton('.gif'), types.KeyboardButton('.bmp'), types.KeyboardButton('.webp')))
            bot.register_next_step_handler(message, conv_image, bot.download_file(bot.get_file(message.document.file_id).file_path))

def deepseek_req(prompt: str, system_prompt: str = 'Ты милый AI.'):
    return sambanova_api.chat.completions.create(messages=[{"role":"user", "content":prompt}, {"role":"system", 'content':system_prompt}], model='DeepSeek-V3-0324').choices[0].message.content

def get_info_about_whisper(request: requests.Response, token: str):
    print(request.json())
    task_id = request.json()["task_id"]
    json = {}
    while True:
        r = requests.get(f'https://api.whisper-api.com/status/{task_id}', headers={"X-API-Key":token}, proxies=proxies)
        if r.json()["status"] != 'completed':
            pass
        else:
            json = r.json()
            break
        time.sleep(5)
    return json

def ai_subtitles_video(message: types.Message, token: str):
    if message.document:
        if message.document.file_name[-4:] in ['.mp4']:
            if message.document.file_size > 20000000:
                bot.reply_to(message, f'Отправьте видео до 20 МБ, в формате .mp4 без сжатия.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            else:
                bot.send_message(message.chat.id, f'Скачиваю видео..')
                random_ = random.random()
                new_ = random.random()
                _ = open(path / f'{random_}.mp4', 'wb')
                _.write(bot.download_file(bot.get_file(message.document.file_id).file_path))
                _.close()
                video = VideoFileClip(path / f'{random_}.mp4')
                video.audio.write_audiofile(path / f'{random_}.wav')
                req = requests.post('https://api.whisper-api.com/transcribe', files={"file":open(path / f'{random_}.wav', 'rb')}, headers={"X-API-Key":token}, proxies=proxies, data={"language":"ru", 'format':"srt", "model_size":"medium"})
                print(req.json())
                time.sleep(3.5)
                result = get_info_about_whisper(req, token)
                srt = open(path / f'{random_}.srt', 'w', encoding='UTF-8')
                srt.write(result['result'])
                srt.close()
                style_options = f"Fontname=Arial,FontSize=24,PrimaryColour=255_255_255_255,OutlineColour=0_0_0_200,Alignment=8"
                _ = os.path.join(path / f'{random_}.srt')
                command = [
                    'ffmpeg', '-i', os.path.join(path, f'{random_}.mp4'),
                    '-vf', f'subtitles={_}:force_style=\'{style_options}\'',
                    '-c:a', 'copy',
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
                    '-y',
                    os.path.join(path / f'{new_}.mp4')
                ]
                subprocess.run(command)
                bot.send_video(message.chat.id, open(path / f'{new_}.mp4', 'rb'), duration=video.duration, width=video.w, height=video.h, caption='Ваше видео с субтитрами.', supports_streaming=True, reply_to_message_id=message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                os.remove(path / f'{random_}.mp4')
                os.remove(path / f'{new_}.mp4')
                os.remove(path / f'{random_}.wav')
        else:
            bot.reply_to(message, f'Отправьте видео до 20 МБ, в формате .mp4 без сжатия.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    elif message.text:
        if message.text.startswith(('http://', 'https://')) and message.text.endswith('.mp4'):
            random_ = random.random()
            bot.send_message(message.chat.id, f'Пытаемся скачать видео..')
            request = requests.get(message.text, stream=True, proxies=proxies, headers=headers_for_html_requests)
            if request.status_code != 200:
                bot.reply_to(message, f'Ошибка. Код: {request.status_code}', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            else:
                with open(path / f'{random_}.mp4', 'wb') as file:
                    for chunk in request.iter_content(8192):
                        if chunk:
                            file.write(chunk)
                    file.close()
                bot.send_message(message.chat.id, f'Файл скачен. Проверяем его размер.')
                if open(path / f'{random_}.mp4', 'rb').read() > 50000000:
                    bot.reply_to(message, f'Видео должно весить 50 МБ. Это максимум.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                    os.remove(path / f'{random_}.mp4')
                else:
                    bot.send_message(message.chat.id, f'Файл подходит нашим требованиям. Начинаем обработку.')
                    bot.send_message(message.chat.id, f'Скачиваю видео..')
                    random_ = random.random()
                    new_ = random.random()
                    video = VideoFileClip(path / f'{random_}.mp4')
                    video.audio.write_audiofile(path / f'{random_}.wav')
                    req = requests.post('https://api.whisper-api.com/transcribe', files={"file":open(path / f'{random_}.wav', 'rb')}, headers={"X-API-Key":token}, proxies=proxies, data={"language":"ru", 'format':"srt", "model_size":"medium"})
                    print(req.json())
                    time.sleep(3.5)
                    result = get_info_about_whisper(req, token)
                    srt = open(path / f'{random_}.srt', 'w', encoding='UTF-8')
                    srt.write(result['result'])
                    srt.close()
                    style_options = f"Fontname=Arial,FontSize=24,PrimaryColour=255_255_255_255,OutlineColour=0_0_0_200,Alignment=8"
                    _ = os.path.join(path / f'{random_}.srt')
                    command = [
                        'ffmpeg', '-i', os.path.join(path, f'{random_}.mp4'),
                        '-vf', f'subtitles={_}:force_style=\'{style_options}\'',
                        '-c:a', 'copy',
                        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
                        '-y',
                        os.path.join(path / f'{new_}.mp4')
                    ]
                    subprocess.run(command)
                    bot.send_video(message.chat.id, open(path / f'{new_}.mp4', 'rb'), duration=video.duration, width=video.w, height=video.h, caption='Ваше видео с субтитрами.', supports_streaming=True, reply_to_message_id=message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                    os.remove(path / f'{random_}.mp4')
                    os.remove(path / f'{new_}.mp4')
                    os.remove(path / f'{random_}.wav')
        else:
            bot.reply_to(message, f'Ожидалась ссылка на видео .mp4 формата.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        bot.reply_to(message, f'Неизвестный отклик. Либо ссылка, либо .mp4 видео без сжатия.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def get_token_whisper(message: types.Message):
    bot.reply_to(message, f'Эта функция добавит нейро-сетевые субтитры к вашему видео.\n\nСкиньте видео в Telegram без сжатия (20 МБ), или скиньте прямую ссылку на видео (50 МБ).', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
    bot.register_next_step_handler(message, ai_subtitles_video, message.text)

def ai_upscale_x4(message: types.Message):
    if message.document:
        if message.document.file_name[-4:] in ['.jpg', '.png']:
            img = Image.open(io.BytesIO(bot.download_file(bot.get_file(message.document.file_id).file_path)))
            original_width, original_height = img.size

            new_width = int(original_width * 4)
            new_height = int(original_height * 4)

            upscaled = img.resize((new_width, new_height), Image.Resampling.BICUBIC)
            new = io.BytesIO()
            upscaled.save(new, 'JPEG')
            bot.send_document(message.chat.id, new.getvalue(), message.id, f'Ваше расширенное изображение.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')), visible_file_name='upscaled-photo.jpg')
        else:
            bot.reply_to(message, f'Ожидалась фотография JPG/PNG без сжатия.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        bot.reply_to(message, f'Ожидалась фотография JPG/PNG без сжатия.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def unzip_zip_to_apk(message: types.Message):
    if not message.document:
        bot.reply_to(message, f'Ожидаем был файл zip.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        if message.document.file_size > 20000000:
            bot.reply_to(message, f'Файл больше 20 МБ.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        else:
            if message.document.file_name[-4:] in ['.zip']:
                file = io.BytesIO(bot.download_file(bot.get_file(message.document.file_id).file_path))
                os.mkdir(path / f'{message.from_user.id}_razarchiv')
                zip = zipfile.ZipFile(file, 'r')
                zip.extractall(path / f'{message.from_user.id}_razarchiv')
                bot.reply_to(message, f'Распаковали! Запаковываем в .apk...')
                zip_new = zipfile.ZipFile(path / f'{message.from_user.id}_razarchiv.apk', 'w')
                for root, dirs, files in os.walk(path / f'{message.from_user.id}_razarchiv'):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, path / f'{message.from_user.id}_razarchiv')
                        zip_new.write(file_path, arcname=arcname)
                zip_new.close()
                bot.send_document(message.chat.id, open(path / f'{message.from_user.id}_razarchiv.apk', 'rb'), message.id, f'APK файл.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                os.remove(path / f'{message.from_user.id}_razarchiv.apk')
                shutil.rmtree(path / f'{message.from_user.id}_razarchiv', True)
            else:
                bot.reply_to(message, f'Ожидаем был файл .zip.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def upzip_apk_or_jar(message: types.Message):
    if not message.document:
        bot.reply_to(message, f'Ожидаем был файл apk/jar.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        if message.document.file_size > 20000000:
            bot.reply_to(message, f'Файл больше 20 МБ.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        else:
            if message.document.file_name[-4:] in ['.jar', '.apk']:
                file = io.BytesIO(bot.download_file(bot.get_file(message.document.file_id).file_path))
                os.mkdir(path / f'{message.from_user.id}_razarchiv')
                zip = zipfile.ZipFile(file, 'r')
                zip.extractall(path / f'{message.from_user.id}_razarchiv')
                bot.reply_to(message, f'Распаковали! Запаковываем в .zip для большей читаемости...')
                zip_new = zipfile.ZipFile(path / f'{message.from_user.id}_razarchiv.zip', 'w')
                for root, dirs, files in os.walk(path / f'{message.from_user.id}_razarchiv'):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, path / f'{message.from_user.id}_razarchiv')
                        zip_new.write(file_path, arcname=arcname)
                zip_new.close()
                bot.send_document(message.chat.id, open(path / f'{message.from_user.id}_razarchiv.zip', 'rb'), message.id, f'Архив с файлами.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                os.remove(path / f'{message.from_user.id}_razarchiv.zip')
                shutil.rmtree(path / f'{message.from_user.id}_razarchiv', True)
            else:
                bot.reply_to(message, f'Ожидаем был файл apk/jar.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def yandex_rutube_vk_parser_video(message: types.Message):
    if not message.text.startswith(('https://rutube.ru/video/', 'https://vk.com/vkvideo', 'https://dzen.ru/video/watch/', 'https://zen.yandex.ru/video/watch/')):
        bot.reply_to(message, f'Неверный формат ссылки!\nПоддерживаемые форматы: https://rutube.ru/video/<ID>, https://vk.com/vkvideo..., https://dzen.ru/video/watch', 'https://zen.yandex.ru/video/watch.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        filename = random.random()
        ydl_opts = {
            'outtmpl': os.path.join(path, f'{filename}.%(ext)s'),  # Шаблон имени файла
            'format': 'mp4',  # Формат видео
            'noplaylist': True, 
            'format': 'worst',
            'proxy':proxies.get('http'),
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as downloader:
                info = downloader.extract_info(message.text, False)
                downloader.download([message.text])
            video = open(path / f'{filename}.mp4', 'rb').read()
            if len(video) > 50000000:
                bot.reply_to(message, f'Не можем отправить видео: оно весит больше 50 МБ.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                os.remove(path / f'{filename}.mp4')
            else:
                bot.send_chat_action(message.chat.id, 'upload_video')
                author = info.get('uploader', 'Not Founded')
                title = info.get('title', 'Not Founded')
                duration = info.get('duration', 0)
                duration_str = info.get('duration_string', '0:00')
                views = info.get('view_count', 0)
                likes = info.get('like_count', 0)
                comments = info.get('comment_count', 0)
                bot.send_video(message.chat.id, open(path / f'{filename}.mp4', 'rb'), caption=f'{author} - {title}\nПросмотры: {views}\nЛайки: {likes}\nКомментарии: {comments}\nДлительность: {duration_str}', supports_streaming=True, reply_to_message_id=message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')), duration=duration)
                os.remove(path / f'{filename}.mp4')
        except:
            bot.reply_to(message, f'Ошибка скачивания. Попробуйте позже, пожалуйста!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            try:
                os.remove(path / f'{filename}.mp4')
            except:
                pass

def twitch_downloader(message: types.Message):
    if not message.text.startswith(('https://m.twitch.tv/twitch/clip/', 'https://twitch.tv/twitch/clip/')):
        bot.reply_to(message, f'Ссылка должна начинаться с https://m.twitch.tv/twitch/clip/, или https://twitch.tv/twitch/clip/.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        filename = random.random()
        ydl_opts = {
            'outtmpl': os.path.join(path, f'{filename}.%(ext)s'),  # Шаблон имени файла
            'format': 'mp4',  # Формат видео
            'noplaylist': True, 
            'format': 'worst',
            'proxy':proxies.get('http'),
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as downloader:
                info = downloader.extract_info(message.text, False)
                downloader.download([message.text])
            video = open(path / f'{filename}.mp4', 'rb').read()
            if len(video) > 50000000:
                bot.reply_to(message, f'Не можем отправить видео: оно весит больше 50 МБ.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                os.remove(path / f'{filename}.mp4')
            else:
                bot.send_chat_action(message.chat.id, 'upload_video')
                author = info.get('creator', 'Not Founded')
                title = info.get('title', 'Not Founded')
                duration = info.get('duration', 0)
                duration_str = info.get('duration_string', '0:00')
                views = info.get('view_count', 0)
                bot.send_video(message.chat.id, open(path / f'{filename}.mp4', 'rb'), duration, caption=f'{author} - {title}\nДлительность: {duration_str}\nПросмотры: {views}', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')), reply_to_message_id=message.id, supports_streaming=True)
                os.remove(path / f'{filename}.mp4')
        except:
            bot.reply_to(message, f'Ошибка скачивания. Попробуйте позже, пожалуйста!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            try:
                os.remove(path / f'{filename}.mp4')
            except:
                pass

def get_country_of_people(message: types.Message, name: str, age: str, info: str, command: str):
    if message.location:
        bot.reply_to(message, f'Получили заявку! Ждите ответа от Флореста!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        bot.send_message(message.chat.id, f'В меню.', reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('🏡В меню')))
        admins_of_server = [7980694914, 7455363246]
        r = requests.get(f"https://nominatim.openstreetmap.org/reverse?lat={message.location.latitude}&lon={message.location.longitude}&format=json", headers={"Accept-Language":"ru-RU", "User-Agent":"FlorestApplication"}, proxies=proxies)
        json = r.json()
        for admin in admins_of_server:
            try:
                bot.send_message(admin, f'Новая заявка на FSS!\nИмя пользователя: {name}\nВозраст: {age}\nИнформация об игроке (что будет делать): {info}\nЕсть-ли тиммейты: {command}\nСтрана игрока: {json["address"]["country"]}\nГород: {json["address"]["city"]}\n{message.from_user.id}')
            except:
                pass
    elif message.contact:
        bot.reply_to(message, f'Получили заявку! Ждите ответа от Флореста!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        bot.send_message(message.chat.id, f'В меню.', reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('🏡В меню')))
        admins_of_server = [7980694914, 7455363246]
        for admin in admins_of_server:
            try:
                bot.send_message(admin, f'Новая заявка на FSS!\nИмя пользователя: {name}\nВозраст: {age}\nИнформация об игроке (что будет делать): {info}\nЕсть-ли тиммейты: {command}\nПервые несколько символов номера: +{message.contact.phone_number[:5]}\n{message.from_user.id}')
            except:
                pass
    else:
        bot.reply_to(message, f'Неизвестный отклик. Попробуйте еще.')
        bot.register_next_step_handler(message, get_country_of_people, name, age, info, command)

def get_command_of_people(message: types.Message, name: str, age: str, info: str):
    bot.reply_to(message, f'Окей! Пожалуйста, пришлите свою геометку/номер телефона для подтверждения своей геолокации.\nДанные не будут храниться где-либо, а использоваться исключительно в целях подтверждения вашего региона.', reply_markup=types.ReplyKeyboardMarkup(row_width=1).add(types.KeyboardButton('Отправить свою геолокацию', request_location=True), types.KeyboardButton('Отправить свой номер', request_contact=True)))
    bot.register_next_step_handler(message, get_country_of_people, name, age, info, message.text)

def get_info_about__(message: types.Message, name: str, age: str):
    bot.reply_to(message, f'Отлично! У вас есть команда, с кем вы будете играть?')
    bot.register_next_step_handler(message, get_command_of_people, name, age, message.text)

def get_age(message: types.Message, name: str):
    if not message.text.isdigit():
        bot.reply_to(message, f'Указанное вами сообщение не является числом. Попробуйте еще раз.')
        bot.register_next_step_handler(message, get_age)
    else:
        bot.reply_to(message, f'Отлично! Что вы собираетесь делать на нашем проекте? (Пример: построю свою деревушку)')
        bot.register_next_step_handler(message, get_info_about__, name, message.text)

def create_request_to_fss(message: types.Message):
    bot.reply_to(message, f'Отлично! Сколько вам лет?')
    bot.register_next_step_handler(message, get_age, message.text)

def tiktok_video_downloader(message: types.Message):
    if not message.text:
        bot.reply_to(message, f'Ожидалось текстовое сообщение.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        if not message.text.startswith(('https://www.tiktok.com/@', 'https://vt.tiktok.com/')):
            bot.reply_to(message, f'Эта функция может скачивать ТОЛЬКО видео с TikTok.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        else:
            name_of_file = random.random()
            ydl_opts = {
                'outtmpl': os.path.join(path, f'{name_of_file}.%(ext)s'),  # Шаблон имени файла
                'format': 'mp4',  # Формат видео
                'noplaylist': True, 
                'format': 'worst',
                'proxy':proxies.get('http'),
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as downloader:
                    info = downloader.extract_info(message.text, False)
                    downloader.download([message.text])
                video = open(path / f'{name_of_file}.mp4', 'rb').read()
                if len(video) > 50000000:
                    bot.reply_to(message, f'Не можем отправить видео: оно весит больше 50 МБ.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                    os.remove(path / f'{name_of_file}.mp4')
                else:
                    bot.send_chat_action(message.chat.id, 'upload_video')
                    channel = info.get('channel', 'Unknown channel')
                    title = info.get('title', 'Unknown title')
                    likes = info.get('like_count', '0')
                    views = info.get('view_count', '0')
                    reposts = info.get('repost_count', '0')
                    comments = info.get('comment_count', '0')
                    duration = info.get('duration', 0)
                    duration_str = info.get('duration_string', '0:00')
                    bot.send_video(message.chat.id, open(path / f'{name_of_file}.mp4', 'rb'), caption=f'{channel} - {title}\nПросмотры: {views}\nЛайки: {likes}\nРепосты: {reposts}\nКомментарии: {comments}\nДлительность: {duration_str}', supports_streaming=True, reply_to_message_id=message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')), duration=duration)
                    os.remove(path / f'{name_of_file}.mp4')
            except Exception as e:
                bot.reply_to(message, f'Ошибка скачивания. Попробуйте позже, пожалуйста!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                try:
                    os.remove(path / f'{name_of_file}.mp4')
                except:
                    pass

@bot.message_handler(commands=['warn'])
def warn_func(message: types.Message):
    if not message.forward_from:
        if message.chat.type != 'supergroup':
            bot.reply_to(message, f'Данная команда работает только в супергруппе.')
        else:
            if message.chat.id != chat_id:
                bot.reply_to(message, f'Функции модерации "FlorestBot" работают только в группе "FlorestChat" (@florestchannelgroup).')
                bot.leave_chat(message.chat.id)
            else:
                if bot.get_chat_member(message.chat.id, message.from_user.id).status not in ['administrator', 'owner'] and message.from_user.username != 'GroupAnonymousBot':
                    bot.reply_to(message, f'Данная команда доступна только для группы "Администраторы".')
                else:
                    if message.reply_to_message:
                        if bot.get_chat_member(group_id, message.reply_to_message.from_user.id).status in ['administrator', 'owner', 'left', 'kicked']:
                            bot.reply_to(message, f'{message.from_user.full_name}, ты не можешь дать предупреждение администратору, владельцу, или человеку, вышедшему из группы.')
                        else:
                            bot.reply_to(message, f'Предупреждение зарегистрировано.')
                            args = message.text.split()[1:]
                            try:
                                bot.send_message(message.chat.id, f'ПРЕДУПРЕЖДЕНИЕ [\!]\nУчастник: [{message.reply_to_message.from_user.full_name}](tg://user?id={message.reply_to_message.from_user.id})\nПричина: ' + ' '.join(args), reply_to_message_id=message.reply_to_message.id, parse_mode='MarkdownV2')
                            except:
                                bot.send_message(message.chat.id, f'ПРЕДУПРЕЖДЕНИЕ [!]\nУчастник: {message.reply_to_message.from_user.full_name}\nПричина: ' + ' '.join(args), reply_to_message_id=message.reply_to_message.id)
                    else:
                        bot.reply_to(message, f'Ты должен ответить на сообщение нарушителя, чтобы дать предупреждение.')

def for_prohibitions_in_group(message: str):
    request = client_for_gpt.chat.completions.create([{"role":"user", 'content':f"В данном сообщении есть посыл продажи, оскорбления, пропаганда запрещенных идей, пропаганда рекламных услуг, реклама (ссылки на сторонние ресурсы тоже считаются, кроме тех, где florestdev, florestone4185, florestdev4185, florest4185), публикация личных данных, ссылки на запрещенные рнсурсы, призывы к суициду, распостранения украинской пропаганды, пропаганда феминизма, ЛГБТК+ и т.д.? Ответь одним словом, да/нет.\n\n\"{message}\""}], 'gpt-4o-mini', RetryProvider([PollinationsAI, Chatai, OIVSCodeSer2, Blackbox, LegacyLMArena, PollinationsAI]), False, proxies.get('http'), max_tokens=5)
    print(message, request.choices[0].message.content)
    if 'да' in request.choices[0].message.content.lower():
        return True
    else:
        return False

def cut_link_clck(message: types.Message):
    if not message.text:
        bot.reply_to(message, f'Сообщение должно содержать текст.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        if not message.text.startswith(('http://', 'https://')):
            bot.reply_to(message, f'Сообщение должно начинаться с http://, или с https://.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        else:
            request = requests.get('https://clck.ru/--', params={"url":message.text}, headers=headers_for_html_requests, proxies=proxies)
            if request.text == 'limited':
                time.sleep(2.5)
                request = requests.get('https://clck.ru/--', params={"url":message.text}, headers=headers_for_html_requests, proxies=proxies)
                bot.reply_to(message, request.text, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            else:
                bot.reply_to(message, request.text, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                
def parse_kwork(category: int, pages: int = 1) -> list[dict]:
    """Функция для парсинга объявлений на kwork.\ncategory: категория для парсинга.\npages: сколько страниц спарсить? По умолчанию, 1.\nВозвращает список с кворками."""
    import requests, json
    from bs4 import BeautifulSoup
        
    offers: list[dict] = []
        
    response = requests.get('https://kwork.ru/projects', params={"c": category, "page":'1'}, proxies=proxies)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    if not soup.head:
        raise Exception

    scripts = soup.head.find_all("script")
    js_script = ""
    for script in scripts:
        if script.text.startswith("window.ORIGIN_URL"):
            js_script = script.text
            break

    start_pointer = 0
    json_data = ""
    in_literal = False
    for current_pointer in range(len(js_script)):
        if js_script[current_pointer] == '"' and js_script[current_pointer - 1] != "\\":
            in_literal = not in_literal
            continue

        if in_literal or js_script[current_pointer] != ";":
            continue

        line = js_script[start_pointer:current_pointer].strip()
        if line.startswith("window.stateData"):
            json_data = line[17:]
            break

        start_pointer = current_pointer + 1

    data = json.loads(json_data)

    for raw_kwork in data["wantsListData"]["wants"]:
        offers.append(raw_kwork)
    return offers

def parser_kwork(message: types.Message):
    if not message.text.isdigit():
        bot.reply_to(message, f'Номер категории должен быть цифрой!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        _ = []
        parsed = parse_kwork(int(message.text))
        for i in parsed:
            _.append(f'{i.get("name", "Неизвестно")} - https://kwork.ru/projects/{i.get("id", "Неизвестно")} - {i.get("priceLimit", "Неизвестно")} руб. - {i["user"]["username"]}')
        bot.reply_to(message, f'Список кворков:\n' + '\n'.join(_), reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def download_playlist_elements(message: types.Message):
    if not message.text:
        bot.reply_to(message, f'Ответ должен быть в текстовом сообщении.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        try:
            playlist = Playlist(message.text, proxies=proxies)
            bot.reply_to(message, f'Получили доступ к плейлисту.. Начинаем качать..')
            videos: list[YouTube] = []
            for i in playlist.videos:
                videos.append(i)
                bot.send_message(message.chat.id, f'Добавили "{i.title}" в список.')
            for video in videos[:150]:
                name_of_file = random.random()
                try:
                    if video.age_restricted:
                        bot.reply_to(message, f'Не удалось скачать {video.watch_url}: возрастные ограничения.')
                    stream = video.streams.get_lowest_resolution()
                    if stream.filesize > 50000000:
                        bot.reply_to(message, f'Видео весит больше 50 МБ. Согласно ограничениям Telegram мы не можем Вам его отправить.\nКликните на кнопку, чтобы посмотреть и скачать видео напрямую.', reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('🏡В меню')))
                        bot.send_message(message.chat.id, f'Ваша прямая ссылка!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Смотреть видео напрямую.', stream.url)))
                    else:
                        progress = bot.send_message(message.chat.id, f'Прогресс.. 0%/100%')
                        def progress_func(stream, chunk, bytes_remaining):
                            total_size = stream.filesize
                            bytes_downloaded = total_size - bytes_remaining
                            percentage_complete = bytes_downloaded / total_size * 100
                            now_downloaded = len(chunk) / 1024 / 1024
                            bot.edit_message_text(f'Прогресс.. {percentage_complete:.2f}/100% [{bytes_downloaded:.2f} / {total_size:.2f} B]\n⚡Сейчас скачали: {now_downloaded:.2f} MB', message.chat.id, progress.id)
                            time.sleep(2.5)
                        video.register_on_progress_callback(progress_func)
                        video.streams.get_audio_only().download(path, f'{name_of_file}.mp3')
                        bot.send_chat_action(message.chat.id, f'upload_voice')
                        date = video.publish_date.strftime("%Y-%m-%d %H:%M:%S")
                        likes = requests.get('https://www.googleapis.com/youtube/v3/videos', params={"part":"statistics", "id":video.video_id, "key":google_api_key}, proxies=proxies, headers=headers_for_html_requests).json()
                        try:
                            bot.send_audio(message.chat.id, open(path / f'{name_of_file}.mp3', 'rb'), duration=video.length, caption=f'{video.author} - {video.title}\nКоличество просмотров: {video.views}\nКоличество отметок "нравится": {likes["items"][0]["statistics"]["likeCount"]}\nКоличество комментариев: {likes["items"][0]["statistics"]["commentCount"]}\nДата публикации: {date}', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')), performer=video.author, title=video.title)
                        except:
                            bot.send_audio(message.chat.id, open(path / f'{name_of_file}.mp3', 'rb'), duration=video.length, caption=f'{video.author} - {video.title}\nКоличество просмотров: {video.views}\nДата публикации: {date}', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')), performer=video.author, title=video.title)
                        bot.delete_message(message.chat.id, progress.id)
                        os.remove(path / f'{name_of_file}.mp3')
                except:
                    bot.delete_message(message.chat.id, progress.id)
                    try:
                        os.remove(path / f'{name_of_file}.mp3')
                    except:
                        pass
                    pass
            bot.send_message(message.chat.id, f'Скачивание {len(videos)} успешно завершено.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        except:
            bot.reply_to(message, f'Не удалось получить доступа к плейлисту.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def toxic_or_auto_deepseek(message: types.Message):
    if message.text in ['auto', 'toxic']:
        bot.reply_to(message, f'ОК! Напишите свой первый запрос DeepSeek`у.\nБот принимает текстовые сообщение, голосовые, а также фотографии без сжатия в формате JPG/PNG.')
        bot.register_next_step_handler(message, ai_obrabotchik, 3, message.text)
    else:
        bot.reply_to(message, f'Доступны только auto и toxic.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def free_proxies_():
    print(f'Ищем и проверяем прокси...\nВыключите свои методы анонимизации для корректной обработки процесса.')
    response = requests.get("https://free-proxy-list.net/", headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36', 'Accept-Language': 'ru-RU'})
    soup = BeautifulSoup(response.content, 'html.parser')
    proxies_from_site = soup.textarea.text.split('\n')[3:-1]
    normisy = []
    for proxy in sync_tqdm(proxies_from_site[:20], desc='Ищем прокси...'):
        try:
            req = requests.get(f'http://ip-api.com/json/google.ru?lang=ru', headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36', 'Accept-Language': 'ru-RU'}, proxies={"http":f"http://{proxy}", "https":f'http://{proxy}'}, timeout=1)
            if req.status_code == 200:
                normisy.append(proxy)
            else:
                pass
        except:
            pass
    print(f'Готово.\nПродолжаем программный цикл!')
    return normisy

def generate_insulate_reply(message: str):
    try:
        if not 'non-toxic' in message:
            request = deepseek_req(message, f"не отвечай на запросы позитивно и отвечай максимально грубо с матами, на каждое мое сообщения, без разницы, обращаюсь я к тебе мило или нет, всего отвечай максимально грубо")
            return request
        else:
            request = deepseek_req(message)
            return request
    except:
        result = client_for_gpt.chat.completions.create([{"role":"user", 'content':message}], 'gpt-4o-mini', RetryProvider([PollinationsAI, Chatai, OIVSCodeSer2, Blackbox, LegacyLMArena, PollinationsAI]), max_tokens=4096, proxy=proxies.get('http'), web_search=True).choices[0].message.content
        return f'Сорри, я пока не работаю с DeepSeek. Будет использоваться ChatGPT.\n\n{result}'

def add_watermark_on_photo_func(message: types.Message, image: bytes):
    base_image = Image.open(io.BytesIO(image)).convert("RGBA")
        
    # Создаем прозрачный слой для водяного знака
    watermark = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
        
    # Настройки текста
    font = ImageFont.truetype('times.ttf', 40)  # Шрифт и размер
    text_color = (255, 255, 255, 100)  # R,G,B,Alpha (прозрачность)
        
    position = (base_image.width // 2 - watermark.width // 2,  # По центру
                base_image.height // 2 - watermark.height // 2)
        
    # Рисуем текст
    draw.text(position, message.text, fill=text_color, font=font)
        
    # Накладываем водяной знак
    result = Image.alpha_composite(base_image, watermark)
        
    # Сохраняем (конвертируем обратно в RGB для JPG)
    output = io.BytesIO()
    result.convert("RGB").save(output, 'JPEG')
    bot.send_photo(message.chat.id, output.getvalue(), f'Ваше фото с водяным знаком.', reply_to_message_id=message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def add_watermark_on_photo_(message: types.Message):
    if not message.document:
        bot.reply_to(message, f'Функция принимает только фото в формате JPG/PNG, без сжатия!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        if message.document.file_name[-4:] in ['.jpg', '.png']:
            bot.reply_to(message, f'Спасибо! Напишите текст, который должен быть на фотографии.')
            file = bot.download_file(bot.get_file(message.document.file_id).file_path)
            bot.register_next_step_handler(message, add_watermark_on_photo_func, file)
        else:
            bot.reply_to(message, f'Функция принимает только фото в формате JPG/PNG, без сжатия!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def info_about_minecraft_server(message: types.Message):
    try:
        ip = message.text
        url = f"https://api.mcsrvstat.us/3/{ip}"
        response = requests.get(url, timeout=5, proxies=proxies, headers=headers_for_html_requests)
        if response.status_code == 500:
            bot.reply_to(
                message,
                f"❌ Сервер {ip} недоступен или оффлайн.",
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("Назад", callback_data="back")
                )
            )
            return
        data = response.json()

        # Проверяем, что сервер онлайн
        if not data.get("debug", {"ping":False}).get("ping", False):
            bot.reply_to(
                message,
                f"❌ Сервер {ip} недоступен или оффлайн.",
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("Назад", callback_data="back")
                )
            )
            return

        # MOTD
        motd_plain = "\n".join(data.get("motd", {}).get("clean", ["—"]))

        # Игроки
        players = data.get("players", {})
        online = players.get("online", 0)
        max_players = players.get("max", 0)
        player_list = players.get("list", [])
        players_display = "\n".join(
            [f"• {p['name']}" for p in player_list[:10]]
        ) if player_list else "Нет игроков онлайн"

        # Версия и ядро
        version = data.get("version", "—")
        software = data.get("software", "—")

        # Карта и плагины
        map_name = data.get("map", {}).get("clean", "—")
        plugins = data.get("plugins", [])
        plugins_display = ", ".join([p["name"] for p in plugins[:10]]) if plugins else "Нет"

        # Пинг / протокол
        latency = data.get("debug", {}).get("cachetime", "—")
        protocol = data.get("protocol", {}).get("name", "—")

        # Иконка сервера
        icon = data.get("icon", None)

        # Формируем сообщение
        text = (
            f"🧭 Информация о сервере **{ip}**:\n\n"
            f"📜 MOTD:\n{motd_plain}\n\n"
            f"👥 Онлайн: {online} / {max_players}\n"
            f"🎮 Игроки онлайн:\n{players_display}\n\n"
            f"🗺 Карта: {map_name}\n"
            f"⚙️ Версия: {version}\n"
            f"💻 Протокол: {protocol}\n"
            f"🧩 ПО: {software}\n\n"
            f"📦 Плагины (до 10): {plugins_display}\n\n"
            f"📶 Ping/CacheTime: {latency}"
        )

        markup = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("Назад", callback_data="back")
        )

        # Если есть иконка — отправляем фото
        if icon:
            try:
                bot.send_photo(
                    message.chat.id,
                    base64.b64decode(icon.split(",")[1]),
                    caption=text,
                    parse_mode="Markdown",
                    reply_markup=markup,
                    reply_to_message_id=message.id
                )
            except:
                bot.send_photo(
                    message.chat.id,
                    base64.b64decode(icon.split(",")[1]),
                    caption=text,
                    reply_markup=markup,
                    reply_to_message_id=message.id
                )
        else:
            try:
                bot.reply_to(
                    message,
                    text,
                    parse_mode="Markdown",
                    reply_markup=markup
                )
            except:
                bot.reply_to(
                    message,
                    text,
                    parse_mode="Markdown",
                    reply_markup=markup
                )

    except Exception as e:
        print(e)
        bot.reply_to(
            message,
            f"⚠️ Не удалось получить данные!\n"
            f"Проверьте, что IP правильный и это Java-сервер.",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("Назад", callback_data="back")
            )
        )

def create_already_stickerpack(message: types.Message, title: str):
    if not message.document:
        bot.reply_to(message, f'Ты не прислал файл.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        if message.document.file_name[-4:] != '.zip':
            bot.reply_to(message, f'Нужен .zip архив с изображениями!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        else:
            _ = open(path / f'{message.from_user.id}_sticker.zip', 'wb')
            _.write(bot.download_file(bot.get_file(message.document.file_id).file_path))
            _.close()
            del _
            bot.reply_to(message, f'Скачали архив..\nРазархивация..')
            zip = zipfile.ZipFile(path / f'{message.from_user.id}_sticker.zip', 'r')
            elements = []
            for index, data in enumerate(zip.namelist(), 1):
                elements.append(f'{index}. {data}')
            bot.reply_to(message, f'Элементы архива:\n\n' + '\n'.join(elements))
            del elements
            zip.extractall(path / f'{message.from_user.id}_sticker')
            bot.reply_to(message, f'Разархивировано!')
            r = random.random()
            img = path / 'cat.png'
            bot.create_new_sticker_set(message.from_user.id, f'{message.from_user.id}_stickers_{r}', title, png_sticker=types.InputSticker(types.InputFile(open(img, 'rb').read(), file_name='cat.png'), emoji_list=["👍"]))
            bot.reply_to(message, f'Создали стикер-пак.\nЗаливаем изображения..')
            for file in os.listdir(path / f'{message.from_user.id}_sticker'):
                if file[-4:] == '.png':
                    bot.add_sticker_to_set(message.from_user.id, f'{message.from_user.id}_stickers_{r}', png_sticker=types.InputSticker(types.InputFile(open(path / f'{message.from_user.id}_sticker/{file}', 'rb').read(), file_name='cat.png'), emoji_list=["👍"]))
                else:
                    bot.add_sticker_to_set(message.from_user.id, f'{message.from_user.id}_stickers_{r}', webm_sticker=types.InputSticker(types.InputFile(open(path / f'{message.from_user.id}_sticker/{file}', 'rb').read(), file_name='cat.png'), emoji_list=["👍"]))
            bot.reply_to(message, f'Успех!\nВаш стикер-пак: t.me/addstickers/{message.from_user.id}_stickers_{r}', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
def get_title_stickerpack(message: types.Message):
    bot.reply_to(message, f'Отличное название!\nЗалейте архив с изображениями для стикер-пака.')
    bot.register_next_step_handler(message, create_already_stickerpack, message.text)

def censor_faces_image(image: bytes, return_resolution: tuple[int] = (1280, 720), block_size: int = 20):
        """Данная функция превращает лица на фото в пиксели, короче, цензура.\nimage: фотка в `bytes`. Пример: open('photo.jpg', 'rb').read()\nreturn_resolution: выходное разрешение. По умолчанию, `(1280, 720)`.\nblock_size: резкость мозаики, по умолчанию 20.\nВозвращает bytes."""
        from tqdm import tqdm
        img_pil = Image.open(io.BytesIO(image)).resize(return_resolution, Image.Resampling.LANCZOS)
        img = cv2.imdecode(numpy.frombuffer(image, numpy.uint8), cv2.IMREAD_COLOR)
        img = cv2.resize(img, return_resolution)
        
        os.environ['HOME'] == '/data/.yoloface'
        _, boxes, confs = face_analysis().face_detection(frame_arr=img, model='tiny')
        
        faces = [(x, y, w, h) for i, (x, y, w, h) in enumerate(boxes) if confs[i] > 0.5]
        if not faces:
            print(f'Лица не были найдены на фотографии.')
            return image
        else:
            for x, y, w, h in tqdm(faces, desc='Цензурим лица..', ncols=70):
                region = (x, y, x + w, y + h)
                region_img = img_pil.crop(region)
                small_size = (max(int(w) // block_size, 1), h)
                small_region = region_img.resize(small_size, Image.Resampling.NEAREST)
                mosaic_region = small_region.resize((w, h), Image.Resampling.NEAREST)
                img_pil.paste(mosaic_region, region)
            output = io.BytesIO()
            img_pil.save(output, format='JPEG')
            print(f'Готово!')
            return output.getvalue()


def face_obrab_func(message: types.Message):
    if not message.document:
        bot.reply_to(message, f'{message.from_user.full_name}, нужно отправить фото форматом .JPG, без сжатия (файлом).', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        if message.document.file_name[-4:] != '.jpg':
            bot.reply_to(message, f'Данная функция поддерживает только `.jpg.` файлы.', parse_mode='Markdown')
        else:
            pic = bot.download_file(bot.get_file(message.document.file_id).file_path)
            i = cv2.imdecode(numpy.frombuffer(pic, numpy.uint8), cv2.IMREAD_COLOR)
            censor_pic = censor_faces_image(pic, (i.shape[:2][1], i.shape[:2][0]), 15)
            bot.send_photo(message.chat.id, censor_pic, f'Ваша фотография с блюром лица.', reply_to_message_id=message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            del pic, i, censor_pic
            
class AsyncYandexParser:
    """Асинхронный парсер картинок с Яндекса.\nПоддерживаются только приватные HTTP(s) прокси с именем пользователя и паролем. Также требуется установка Google Chrome на машину.\nis_headless: скрывать окно с парсером?"""

    def __init__(self, proxy_host: str = None, proxy_port: int = None, proxy_user: str = None, proxy_pass: str = None, is_headless:bool=False):
        """Асинхронный парсер картинок с Яндекса.\nПоддерживаются только приватные HTTP(s) прокси с именем пользователя и паролем. Также требуется установка Google Chrome на машину.\nis_headless: скрывать окно с парсером?"""
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_user = proxy_user
        self.proxy_pass = proxy_pass
        self.isheadless = is_headless
        print(f'Парсер инициализирован, сучки!\nНачните парсить с помощью функции start_parsing.')

    async def download_image(self, session: aiohttp.ClientSession, img_url, directory):
        """Качаем картинку асинхронно, блять."""
        if not all([self.proxy_host, self.proxy_port, self.proxy_user, self.proxy_pass]):
            if img_url and "http" in img_url:
                try:
                    async with session.get(img_url) as response:
                        if response.status == 200:
                            _ = random.random()
                            file_path = os.path.join(directory, f'{_}.jpg')
                            with open(file_path, 'wb') as file:
                                file.write(await response.read())
                except Exception as e:
                    print(f"Картинка не скачалась, пиздец: {e}")
        else:
            if img_url and "http" in img_url:
                try:
                    proxy_auth = aiohttp.BasicAuth(login=self.proxy_user, password=self.proxy_pass)
                    async with session.get(img_url, proxy=f'http://{self.proxy_host}:{self.proxy_port}', proxy_auth=proxy_auth) as response:
                        if response.status == 200:
                            _ = random.random()
                            file_path = os.path.join(directory, f'{_}.jpg')
                            with open(file_path, 'wb') as file:
                                file.write(await response.read())
                except Exception as e:
                    print(f"Картинка не скачалась, пиздец: {e}")

    async def start_parsing(self, query: str, directory: str, max_images=10, scrolly=5, pages:int=6, message: types.Message = None):
        """Начать парсить..\nquery: запрос. Пример: котики\ndirectory: директория на машине, где надо сохранять картинки.\nmax_images: максимальное количество картинок в директории.\nscrolly: скока скроллить картинки?\npages: сколько страниц с картинками парсить?"""
        # Создаём директорию, если не существует
        if not os.path.exists(directory):
            os.makedirs(directory)
        os.chdir(directory)

        # Настройка браузера
        try:
            chrome_options = Options()
            chrome_options.add_argument("--log-level=1")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument('--disable-sync')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--headless')
            chrome_options.add_argument("--disable-features=NetworkServiceInProcess")
            chrome_options.add_argument("--disable-setuid-sandbox")
            chrome_options.add_argument('--no-sandbox')
            driver = webdriver.Chrome(options=chrome_options)
            print("Браузер запустился, ахуеть!")
        except Exception as e:
            print(f"Не могу запустить Chrome, пиздец: {e}")
            return

        image_urls = []
        try:
            if pages > 1:
                for p in range(0, pages - 1):
                    url = f"https://yandex.ru/images/search?text={query}&p={p}"
                    driver.get(url)
                    print(f"Зашёл на страницу ({p}), ждём, блять")
                    bot.send_message(message.chat.id, f'Зашёл на страницу {p + 1}...')
                    
                    # Ждём загрузку пикч
                    await asyncio.sleep(10)
                    
                    # Скроллим
                    for _ in range(scrolly):
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        await asyncio.sleep(2.5)
                        print("Скроллю, сука")
                    
                    all_images = driver.find_elements(By.TAG_NAME, "img")
                    print(f"Всего тегов <img> на странице: {len(all_images)}")
                    bot.send_message(message.chat.id, f'На странице найдено около {len(all_images)} изображений.')
                    if all_images:
                        for img in all_images[:max_images]:
                            img_url = img.get_attribute("src")
                            if img_url and "http" in img_url:
                                image_urls.append(img_url)
                    else:
                        print(f"Ни одного <img> не нашёл на странице {p}, пиздец полный")
                        bot.send_message(message.chat.id, f'На странице не было найдено ни одного изображения.')
            else:
                url = f"https://yandex.ru/images/search?text={query}&p=0"
                driver.get(url)
                print(f"Зашёл на страницу, ждём, блять")
                bot.send_message(message.chat.id, f'Зашёл на страницу...')
                    
                # Ждём загрузку пикч
                await asyncio.sleep(10)
                    
                # Скроллим
                for _ in range(scrolly):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    await asyncio.sleep(2.5)
                    print("Скроллю, сука")
                    
                all_images = driver.find_elements(By.TAG_NAME, "img")
                print(f"Всего тегов <img> на странице: {len(all_images)}")
                bot.send_message(message.chat.id, f'На странице найдено около {len(all_images)} изображений.')
                if all_images:
                    for img in all_images[:max_images]:
                        img_url = img.get_attribute("src")
                        if img_url and "http" in img_url:
                            image_urls.append(img_url)
                else:
                    print(f"Ни одного <img> не нашёл на странице {p}, пиздец полный")
                    bot.send_message(message.chat.id, f'На странице не было найдено ни одного изображения.')

        except Exception as e:
            print(f"Что-то пошло по пизде на странице {p}: {e}")

        driver.quit()
        print("Браузер закрыл, пиздец, готово")

        # Качаем картинки
        if image_urls:
            print(f"Начинаем качать {len(image_urls)} картинок асинхронно, блять...")
            async with aiohttp.ClientSession(headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129.0.0.0 Safari/537.36'}) as session:
                tasks = [self.download_image(session, url, directory) for url in image_urls[:max_images]]
                await tqdm.gather(*tasks, desc='Качаем картинки...', ncols=70)
        else:
            print("Нихуя не скачал, картинок нет, пиздец")

def is_youtube_banned(id: str):
    if id in open(path / f'banned_youtube.txt', 'r').readlines():
        return True
    else:
        return False
    
def parse_yandex(message: types.Message, query: str, colvo: int):
    bot.reply_to(message, f'Начинаем парсить..')
    parser = AsyncYandexParser(is_headless=True)
    asyncio.run(parser.start_parsing(query, path / f'{message.from_user.id}_parseyandex', colvo, 6, int(message.text), message))
    files = os.listdir(path / f'{message.from_user.id}_parseyandex')
    zip = zipfile.ZipFile(path / f'{message.from_user.id}_parseyandex.zip', 'w')
    for file in files:
        zip.write(os.path.join(path / f'{message.from_user.id}_parseyandex', file), compress_type=zipfile.ZIP_DEFLATED)
    zip.close()
    bot.send_chat_action(message.chat.id, 'upload_document')
    bot.send_document(message.chat.id, open(path / f'{message.from_user.id}_parseyandex.zip', 'rb'), message.id, caption=f'Ваши спаршенные фотографии ({colvo}) c Yandex.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    os.remove(path / f'{message.from_user.id}_parseyandex.zip')
    for file in files:
        os.remove(os.path.join(path, f'{message.from_user.id}_parseyandex', f'{file}'))
    del zip, parser, files

def get_colvo_p(message: types.Message, query: str):
    bot.reply_to(message, f'Хорошо! Сколько страниц поиска надо спарсить?\nНапример: 5')
    bot.register_next_step_handler(message, parse_yandex, query, int(message.text))

def get_query_p(message: types.Message):
    bot.reply_to(message, f'Отлично! Сколько картинок надо спарсить?')
    bot.register_next_step_handler(message, get_colvo_p, message.text)

def check_ai_result(message: types.Message):
    if message.text in ['voice', 'text']:
        bot.reply_to(message, f'Напиши первый запрос GPT-4o!\nЛибо текстовыми, либо голосовыми сообщениями!\n(ТЕПЕРЬ ВОЗМОЖНА ОБРАБОТКА ИЗОБРАЖЕНИЙ, ВЫ МОЖЕТЕ УЗНАТЬ, ЧТО ИЗОБРАЖЕНО НА ДАННОМ ВАМИ ФОТО, ОТПРАВЛЯЙТЕ БЕЗ СЖАТИЯ, В ФОРМАТЕ JPG/PNG)')
        bot.register_next_step_handler(message, ai_obrabotchik, 2, message.text)
    else:
        bot.reply_to(message, f'Неизвестный отклик. Либо voice, либо text!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def last_post_vk(message: types.Message):
    vk_session = vk_api.VkApi(token=token_for_vk)
    vk = vk_session.get_api()
    response = vk.groups.search(q=message.text, type='group', count=1)  # Используем groups.search
    response1 = vk.wall.get(owner_id=-int(response['items'][0]['id']), count=1)  # owner_id должен быть отрицательным для групп
    if response['count'] > 0:
            post = response1['items'][0]
            text = post.get('text', 'Текст отсутствует')  # Получаем текст поста, если есть
            post_id = post['id']
            owner_id = post['owner_id']
            link = f"https://vk.com/wall{owner_id}_{post_id}"  # Формируем ссылку на пост
            likes = response1['items'][0]['likes']['count']
            views = response1['items'][0]['views']['count']
            reposts = response1['items'][0]['reposts']['count']
            bot.reply_to(message, f'Пост от {message.text}:\nТекст: {text}\nСсылка: {link}\nЛайки: {likes}\nПросмотры: {views}\nРепосты: {reposts}', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        bot.reply_to(message, f'Паблики не найдены.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def all_ready_download(message: types.Message, songs: list[Song]):
    bot.reply_to(message, f'Качаем...', reply_markup=types.ReplyKeyboardMarkup(True, input_field_placeholder=f'Сэр, да, сэр.', row_width=1).add(types.KeyboardButton('🏡В меню')))
    try:
        _ = int(message.text)
        try:
            song = songs[_]
            req = requests.get(song.url)
            bot.send_audio(message.chat.id, req.content, caption=f'{song.artist} - {song.title}\nСсылка: {song.url}\nДлительность: {time.strftime("%H:%M:%S", time.gmtime(song.duration))}', duration=song.duration, performer=song.artist, title=song.title, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        except:
            bot.reply_to(message, f'Ошибка индекса.\nПесни нету в списке!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    except:
        bot.reply_to(message, f'Требуется число.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def vk_music_download(message: types.Message):
    if not message.text:
        bot.reply_to(message, f'Напишите название песни текстовым сообщением.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        service = Service('KateMobileAndroid/56 lite-460 (Android 4.4.2; SDK 19; x86; unknown Android SDK built for x86; en)', token_for_vk)
        songs = service.search_songs_by_text(message.text, count=10)
        if len(songs) == 0:
            bot.reply_to(message, f'Песни по запросу не найдены на просторах VK музыки!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        else:
            composisions = []
            m = types.ReplyKeyboardMarkup(row_width=1)
            for index, _ in enumerate(songs):
                composisions.append(f'{index}. {_.artist} - {_.title} ({time.strftime("%H:%M:%S", time.gmtime(_.duration))})')
                m.add(types.KeyboardButton(index))
            bot.reply_to(message, f'Выберите композию:\n\n' + '\n'.join(composisions), reply_markup=m)
            bot.register_next_step_handler(message, all_ready_download, songs)
            del m, composisions
            #song = random.choice(songs)
            #req = requests.get(song.url)
            #bot.send_audio(message.chat.id, req.content, caption=f'{song.artist} - {song.title}\nСсылка: {song.url}\nДлительность: {time.strftime("%H:%M:%S", time.gmtime(song.duration))}', duration=song.duration, performer=song.artist, title=song.title, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def cpp_compiler(message: types.Message):
    if not message.document:
        bot.reply_to(message, f'Функция принимает только .cpp/.cxx файлы для компиляции.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        if message.document.file_name[-4:] == '.cpp' or message.document.file_name == '.cxx':
            bot.reply_to(message, f'Начинаем компиляцию.. пришлем результат в виде .exe документа.')
            try:
                chislo = random.randint(1, 10000)
                _ = open(path / f'{chislo}{message.document.file_name[-4:]}', 'wb')
                _.write(bot.download_file(bot.get_file(message.document.file_id).file_path))
                _.close()
                subprocess.run(['g++', f'{chislo}{message.document.file_name[-4:]}', '-o', f'{chislo}'], check=True)
                bot.send_document(message.chat.id, open(path / f'{chislo}.exe', 'rb'), caption='Ваш .exe файл на основе C++ кода.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                os.remove(path / f'{chislo}{message.document.file_name[-4:]}')
                os.remove(path / f'{chislo}.exe')
            except Exception as e:
                os.remove(path / f'{chislo}{message.document.file_name[-4:]}')
                bot.reply_to(message, f'Произошла ошибка компиляции: {e}.\nПроверьте корректность своего кода.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        else:
            bot.reply_to(message, f'Функция принимает только .cpp/.cxx файлы для компиляции.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
def speech_to_text(message: types.Message):
    if message.voice:
        if message.voice.duration > 600:
            bot.reply_to(message, f'Голосовое сообщение длиться более 10 минут.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        else:
            msg = bot.reply_to(message, f'Начинаю транскрибацию...')
            chislo = random.randint(1, 10000)
            audio__ = open(path / f'audio_{chislo}.ogg', 'wb')
            audio__.write(bot.download_file(bot.get_file(message.voice.file_id).file_path))
            audio__.close()
            subprocess.run(['ffmpeg', '-i', f'audio_{chislo}.ogg', f'audio_{chislo}.wav'])
            try:
                r = sr.Recognizer()
                file = open(path / f'audio_{chislo}.wav', 'rb')
                with sr.AudioFile(file) as source:
                    audio = r.record(source)
                text = r.recognize_google(audio, language='ru-RU')
                bot.delete_message(msg.chat.id, msg.id)
                bot.reply_to(message, f'В голосовом сообщении сказано следующее: `{text}`.', parse_mode='Markdown', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            except sr.UnknownValueError:
                bot.delete_message(msg.chat.id, msg.id)
                bot.reply_to(message, f'Не удалось распознать речь в данном голосовом сообщении.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            except Exception as e:
                bot.delete_message(msg.chat.id, msg.id)
                bot.reply_to(message, f'Произошла неизвестная ошибка на нашей стороне. Обратитесь в поддержку и скиньте нам код ошибки.\nКод ошибки: `{e}`', parse_mode='Markdown', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            os.remove(path / f'audio_{chislo}.ogg')
            os.remove(path / f'audio_{chislo}.wav')
    elif message.video_note:
        msg = bot.reply_to(message, f'Начинаю транскрибацию...')
        chislo = random.randint(1, 10000)
        video__ = open(path / f'video_{chislo}.mp4', 'wb')
        video__.write(bot.download_file(bot.get_file(message.video_note.file_id).file_path))
        video__.close()
        subprocess.run(['ffmpeg', '-i', f'video_{chislo}.mp4', f'video_{chislo}.wav'])
        try:
            r = sr.Recognizer()
            file = open(path / f'video_{chislo}.wav', 'rb')
            with sr.AudioFile(file) as source:
                audio = r.record(source)
            text = r.recognize_google(audio, language='ru-RU')
            bot.delete_message(msg.chat.id, msg.id)
            bot.reply_to(message, f'В видеосообщении сказано следующее: `{text}`.', parse_mode='Markdown', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        except sr.UnknownValueError:
            bot.delete_message(msg.chat.id, msg.id)
            bot.reply_to(message, f'Не удалось распознать речь в данном видеосообщении.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        except Exception as e:
            bot.delete_message(msg.chat.id, msg.id)
            bot.reply_to(message, f'Произошла неизвестная ошибка на нашей стороне. Обратитесь в поддержку и скиньте нам код ошибки.\nКод ошибки: `{e}`', parse_mode='Markdown', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        os.remove(path / f'video_{chislo}.mp4')
        os.remove(path / f'video_{chislo}.wav')
    elif message.video:
        if message.video.file_size > 20000000:
            bot.reply_to(message, f'Видео весит более 20 МБ. Невозможно перевести в текст.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        else:
            msg = bot.reply_to(message, f'Начинаю транскрибацию...')
            chislo = random.randint(1, 10000)
            video__ = open(path / f'video_{chislo}.mp4', 'wb')
            video__.write(bot.download_file(bot.get_file(message.video.file_id).file_path))
            video__.close()
            subprocess.run(['ffmpeg', '-i', f'video_{chislo}.mp4',  f'video_{chislo}.wav'])
            try:
                r = sr.Recognizer()
                file = open(path / f'video_{chislo}.wav', 'rb')
                with sr.AudioFile(file) as source:
                    audio = r.record(source)
                text = r.recognize_google(audio, language='ru-RU')
                bot.delete_message(msg.chat.id, msg.id)
                bot.reply_to(message, f'В видео сказано следующее: `{text}`.', parse_mode='Markdown', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            except sr.UnknownValueError:
                bot.delete_message(msg.chat.id, msg.id)
                bot.reply_to(message, f'Не удалось распознать речь в данном видео.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            except Exception as e:
                bot.delete_message(msg.chat.id, msg.id)
                bot.reply_to(message, f'Произошла неизвестная ошибка на нашей стороне. Обратитесь в поддержку и скиньте нам код ошибки.\nКод ошибки: `{e}`', parse_mode='Markdown', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            os.remove(path / f'video_{chislo}.mp4')
            os.remove(path / f'video_{chislo}.wav')
    else:
        bot.reply_to(message, f'Поддерживаю только видеосообщения, аудиосообщения и видео длительностью 10 минут и меньше.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
def google_photo_parsing(message: types.Message):
    if not message.text:
        bot.reply_to(message, f'Вы не указали текстовое сообщение, по которому будет проходить запрос.',reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        req = requests.get(f'https://www.google.com/search?q={message.text}&tbm=isch&imglq=1&isz=l&safe=unactive', proxies=proxies)
        soup = BeautifulSoup(req.text, 'html.parser')
        tags = soup.find_all('img', {'src':True})
        imgs_links = []
        for tag in tags:
            if 'https://' in tag['src']:
                imgs_links.append(tag['src'])
        bot.send_photo(message.chat.id, requests.get(random.choice(imgs_links), proxies=proxies).content, caption='Изображение по Вашему запросу.\nНайдено в Google Photo.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
def parsing_site_fl(message: types.Message):
    if not message.text:
        bot.reply_to(message, f'Данная функция поддерживает только ссылки в текстовом формате.', reply_markup=types.InlineKeyboardMarkup().add(types.InineKeyboardButton('Назад', callback_data='back')))
    else:
        try:
            random_chisle = random.randint(1, 100000)
            req = requests.get(message.text, headers=headers_for_html_requests, proxies=proxies)
            if req.status_code == 200:
                file = open(path / f'code_{random_chisle}.html', 'w')
                file.write(req.text)
                file.close()
                bot.send_document(message.chat.id, open(path / f'code_{random_chisle}.html'), message.id, caption='Файл с кодом от сайта, которого ты отправил.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')), visible_file_name=False)
                os.remove(path / f'code_{random_chisle}.html')
            else:
                bot.reply_to(message, f'Ошибка: {req.status_code}.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        except Exception as e:
            bot.reply_to(message, f'Ошибка: {e}.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
def virus_check(message: types.Message):
    if not message.document:
        bot.reply_to(message, f'Данная функция принимает только файлы любых форматов. 20 МБ и меньше.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        file = bot.get_file(message.document.file_id)
        if file.file_size > 20971520:
            bot.reply_to(message, f'В связи с ограничениями от сервиса "VirusTotal" можно проверять файлы 20 МБ и меньше.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        else:
            EICAR = bot.download_file(file.file_path)
            EICAR_MD5 = hashlib.md5(EICAR).hexdigest()

            vt = VirusTotalPublicApi(virustotal_apikey)

            response = vt.get_file_report(EICAR_MD5)
            print(response)
            if response['results']['positives'] == 0:
                bot.reply_to(message, f'🟢{response["results"]["positives"]} сервисов признали этот файл опасным\.\n[Ссылка на исследование\.]({response["results"]["permalink"]})', reply_markup=types.InlineKeyboardButton('Назад', callback_data='back'), parse_mode='MarkdownV2')
            elif response['results']['positivies'] < 20:
                bot.reply_to(message, f'🟡{response["results"]["positives"]} сервисов признали этот файл опасным\.\n[Ссылка на исследование\.]({response["results"]["permalink"]})', reply_markup=types.InlineKeyboardButton('Назад', callback_data='back'), parse_mode='MarkdownV2')
            else:
                bot.reply_to(message, f'🔴{response["results"]["positives"]} сервисов признали этот файл опасным\.\n[Ссылка на исследование\.]({response["results"]["permalink"]})', reply_markup=types.InlineKeyboardButton('Назад', callback_data='back'), parse_mode='MarkdownV2')

def get_email_body(message: types.Message, title: str, recipients: list):
    bot.reply_to(message, f'Начинаем отправку...')
    for email in recipients:
        try:
            message1 = MIMEMultipart()
            message1["From"] = username_mail
            message1["To"] = email
            message1["Subject"] = title
        
            message1.attach(MIMEText(f'{message.text}\n\nПисьмо отправлено с помощью анонимной почты FlorestBot.\nhttps://taplink.cc/florestone4185 - социальные сети создателя бота.\n@postbotflorestbot - бот в Telegram.', "plain", 'utf-8'))
        
            with smtplib.SMTP_SSL("smtp.mail.ru", 465) as server:
                server.login(username_mail, password=passwd_mail)
                server.sendmail(username_mail, email, message1.as_string())
                bot.send_message(message.chat.id, f'Удалось отправить письмо на почту: {email}.')
        except Exception as e:
            bot.send_message(message.chat.id, f'Не удалось отправить письмо на почту: {email}.\nПричина: {e}')
    bot.send_message(message.chat.id, f'Цикл был успешно завершен.\nСпасибо за использование функции.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def get_email_subject_(message: types.Message, recipients: list):
    bot.reply_to(message, f'А теперь напиши, что будет под названием.')
    bot.register_next_step_handler(message, get_email_body, message.text, recipients)

def priem_emails_LOL(message: types.Message):
    if message.text:
        bot.reply_to(message, f'Отлично!\nВведите тему письма для получателей.')
        bot.register_next_step_handler(message, get_email_subject_, message.text.split())
    elif message.document:
        if message.document.file_name[-4:] != '.txt':
            bot.reply_to(message, f'Бот поддерживает только текстовые сообщения, а также .txt файлы.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        else:
            bot.reply_to(message, f'Отлично!\nВведите тему письма для получателей.')
            bot.register_next_step_handler(message, get_email_subject_, bot.download_file(bot.get_file(message.document.file_id).file_path).decode().split())
    else:
        bot.reply_to(message, f'Бот поддерживает только текстовые сообщения, а также .txt файлы.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def send_mail(chat_id: int, message_id: int, title: str, subject: str, recipient: str):
    message = MIMEMultipart()
    message["From"] = username_mail
    message["To"] = recipient
    message["Subject"] = title
 
    message.attach(MIMEText(f'{subject}\n\nПисьмо отправлено с помощью анонимной почты FlorestBot.\nhttps://taplink.cc/florestone4185 - социальные сети создателя бота.\n@postbotflorestbot - бот в Telegram.', "plain", 'utf-8'))
 
    with smtplib.SMTP_SSL("smtp.mail.ru", 465) as server:
        server.login(username_mail, password=passwd_mail)
        server.sendmail(username_mail, recipient, message.as_string())
        bot.edit_message_text('Письмо успешно отправлено!', chat_id, message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def get_email_recipient(message: types.Message, title: str, subject: str):
    if not message.text:
        bot.reply_to(message, f'Поддерживается только текстовые сообщения.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        msg = bot.reply_to(message, f'Отправляю письмо...')
        send_mail(msg.chat.id, msg.id, title, subject, message.text)

def get_email_subject(message: types.Message, title: str):
    if not message.text:
        bot.reply_to(message, f'Поддерживается только текстовые сообщения.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        bot.reply_to(message, f'Отлично! А теперь, введи получателя письма счастья.')
        bot.register_next_step_handler(message, get_email_recipient, title, message.text)

def get_email_title(message: types.Message) -> None:
    if not message.text:
        bot.reply_to(message, f'Поддерживается только текстовые сообщения.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        bot.reply_to(message, f'Хорошо, введи основную часть письма.')
        bot.register_next_step_handler(message, get_email_subject, message.text)

def write_to_user_without_nickname(message: types.Message) -> None:
    if len(message.text) > 10:
        bot.reply_to(message, f'Пользовательский ID не может привышать 10 символов.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    elif len(message.text) < 10:
        bot.reply_to(message, f'Пользовательский ID не может быть меньше, чем 10 символов.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        try:
            bot.reply_to(message, f'Вот тебе ссылочка на него\.\n[Жмякнуть\, чтобы написать\.](tg://openmessage?user_id={int(message.text)})', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')), parse_mode='MarkdownV2')
        except:
            bot.reply_to(message, f'Данная функция поддерживает ТОЛЬКО числа.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def sostoyaniye(bmi: float) -> str:
    if bmi < 18.5:
        return "Недостаточный вес"
    elif 18.5 <= bmi < 25:
        return "Нормальный вес"
    elif 25 <= bmi < 30:
        return "Избыточный вес"
    else:
        return "Ожирение"

def imt_height(message: types.Message, kg: float):
    if not message.text:
        bot.reply_to(message, f'Ожидалось текстовое сообщение.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        try:
            a = float(message.text)
            if a == 0:
                bot.reply_to(message, f'Рост не может быть равен 0, либо меньше 0.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            else:
                if a < 0:
                    bot.reply_to(message, f'Рост не может быть равен 0, либо меньше 0.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                else:
                    imt = kg / (a ** 2)
                    sos = sostoyaniye(imt)
                    bot.send_message(message.chat.id, f'Ваш ИМТ равен: {imt:.2f}.\nСостояние: {sos.lower()}.', disable_web_page_preview=True, reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Исходный код взят у друга', 'https://t.me/pie_rise_channel_s_8395/1009')))
        except Exception as e:
            print(e)
            bot.reply_to(message, f'Ожидается число.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
def imt_check_kg(message: types.Message):
    if not message.text:
        bot.reply_to(message, f'Ожидалось текстовое сообщение.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        try:
            a = float(message.text)
            if a == 0:
                bot.reply_to(message, f'Вес не может быть равен 0, либо меньше 0.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            else:
                if a < 0:
                    bot.reply_to(message, f'Вес не может быть равен 0, либо меньше 0.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                else:
                    bot.reply_to(message, f'Отлично! Введи свой рост в метрах.')
                    bot.register_next_step_handler(message, imt_height, a)
        except:
            bot.reply_to(message, f'Ожидается число.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def deanonchik_photo(message: types.Message) -> None:
    if not message.document:
        bot.reply_to(message, f'Данная функция принимает только фото без сжатия в формате JPG.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        if message.document.file_name[-4:] != '.jpg':
            bot.reply_to(message, f'Данная функция принимает только фото без сжатия в формате JPG.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        with Image.open(io.BytesIO(bot.download_file(bot.get_file(message.document.file_id).file_path))) as img:
            metadata = img._getexif()
            if not metadata:
                bot.reply_to(message, f'Мы не смогли найти метаданные на этой фотографии.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            gps_info = metadata.get(34853)
            if not gps_info:
                bot.reply_to(message, f'Среди метаданных не были найдены GPS-данные.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            else:
                lat = gps_info[2]
                lon = gps_info[4]
                lat_ref = gps_info[3]
                latitude = (lat[0] + lat[1] / 60.0 + lat[2] / 3600.0)
                longitude = (lon[0] + lon[1] / 60.0 + lon[2] / 3600.0)
                datetime_original = metadata.get(36867)
                try:
                    if lat_ref != 'E':
                        latitude = -latitude
                    r = requests.get(f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json", headers={"Accept-Language":"ru-RU", "User-Agent":"FlorestApplication"}, proxies=proxies)
                    json = r.json()
                    if datetime_original:
                        bot.send_location(message.chat.id, latitude, longitude)
                        bot.reply_to(message, f'Страна: {json["address"]["country"]}\nРегион: {json["address"]["state"]}\nРайон: {json["address"]["district"]}\nГород: {json["address"]["city"]}\nРеальный адрес: {json["display_name"]}\nПочтовый индекс: {json["address"]["postcode"]}\nВремя съемки: {datetime_original}', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                    else:
                        bot.send_location(message.chat.id, latitude, longitude)
                        bot.reply_to(message, f'Страна: {json["address"]["country"]}\nРегион: {json["address"]["state"]}\nРайон: {json["address"]["district"]}\nГород: {json["address"]["city"]}\nРеальный адрес: {json["display_name"]}\nПочтовый индекс: {json["address"]["postcode"]}\nВремя съемки неизвестно.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                except:
                    if lat_ref != 'E':
                        latitude = -latitude
                    longitude = -longitude
                    r = requests.get(f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json", headers={"Accept-Language":"ru-RU", "User-Agent":"FlorestApplication"}, proxies=proxies)
                    json = r.json()
                    if datetime_original:
                        bot.send_location(message.chat.id, latitude, longitude)
                        bot.reply_to(message, f'Страна: {json["address"]["country"]}\nРегион: {json["address"]["state"]}\nРайон: {json["address"]["district"]}\nГород: {json["address"]["city"]}\nРеальный адрес: {json["display_name"]}\nПочтовый индекс: {json["address"]["postcode"]}\nВремя съемки: {datetime_original}', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                    else:
                        bot.send_location(message.chat.id, latitude, longitude)
                        bot.reply_to(message, f'Страна: {json["address"]["country"]}\nРегион: {json["address"]["state"]}\nРайон: {json["address"]["district"]}\nГород: {json["address"]["city"]}\nРеальный адрес: {json["display_name"]}\nПочтовый индекс: {json["address"]["postcode"]}\nВремя съемки неизвестно.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def generate_human():
    faker = faker_.Faker('ru-RU')
    today = date.today()
    year_f = int(str(faker.date_of_birth(minimum_age=25, maximum_age=50)).split("-")[0])
    month_f = int(str(faker.date_of_birth(minimum_age=25, maximum_age=50)).split("-")[1])
    day_f = int(str(faker.date_of_birth(minimum_age=25, maximum_age=50)).split("-")[2])
    age_t = today.year - year_f - ((today.month, today.day) < (month_f, day_f))
    bith_date = f'{day_f}.{month_f}.{year_f}'
    return f'Ниже приведенная информация является фейком. Используется открытая библиотека "faker" в Python.\nЗаходите на репозиторий бота в Github для большей информации.\n\nФИО: {faker.name()}\nВозраст: {age_t} ({bith_date})\nМесто работы: {faker.company()}\nДолжность: {faker.job().lower()}\nАдрес: Российская Федерация, {faker.address()}\nПочтовый индекс: {faker.address()[-6:]}\nТелефон: {faker.phone_number()}\nЮзерагент: {faker.user_agent()}\nНомер карты: {faker.credit_card_number()}\nСрок работы: {faker.credit_card_expire()}\nПлатежная система: {faker.credit_card_provider()}\nИНН: {faker.businesses_inn()}\nОРГН: {faker.businesses_ogrn()}'

def generate_nitro(chat_id: int, message_id: int):
    count = 50
    a = 0
    results = []
    while a < count:
        characters = string.ascii_uppercase + string.digits  # Буквы и цифры
        random_code = ''.join(random.choice(characters) for _ in range(15))  # 15 случайных символов
        formatted_code = '-'.join(random_code[i:i+4] for i in range(0, 15, 4))  # Форматирование с тире
        req = requests.get(f'https://discordapp.com/api/v9/entitlements/gift-codes/{formatted_code}?with_application=false&with_subscription_plan=true', headers={"User-Agent":random.choice(["Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.60 YaBrowser/20.12.0.963 Yowser/2.5 Safari/537.36", "SeopultContentAnalyzer/1.0", "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.41 YaBrowser/21.2.0.1097 Yowser/2.5 Safari/537.36", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362"]), "Accept-Language":"ru-RU"}, proxies=proxies)
        results.append(f'{formatted_code} - {req.json()["message"]}')
        a+=1
    bot.edit_message_text('\n'.join(results), chat_id, message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def free_proxies(chat_id: int, message_id: int):
    response = requests.get("https://free-proxy-list.net/", headers=headers_for_html_requests, proxies=proxies)
    soup = BeautifulSoup(response.content, 'html.parser')
    proxies_from_site = soup.textarea.text.split('\n')[3:-1]
    bot.edit_message_text(f'Найдено {str(len(proxies_from_site))} прокси. Начинаем проверку.\nБудет проверено 100 прокси в целях экономии времени.\nМаксимальное время проверки: 5 минут 50 секунд.', chat_id, message_id)
    normisy = []
    for proxy in proxies_from_site[:100]:
        try:
            req = requests.get(f'http://ip-api.com/json/google.ru?lang=ru', headers=headers_for_html_requests, proxies={"http":f"http://{proxy}", "https":f'http://{proxy}'}, timeout=3.5)
            if req.status_code == 200:
                normisy.append(proxy)
            else:
                pass
        except:
            pass
    if len(normisy) > 0:
        bot.edit_message_text(f'Вот твои прокси))).\nОни публичные, без пароля и имени пользователя. Протокол - HTTP(s). Приятного использования!\n' + '\n'.join(normisy), chat_id, message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        bot.edit_message_text(f'Прокси не найдены. Попробуйте позже.', chat_id, message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
def password_check(message: types.Message):
    req = requests.get(f'https://api.proxynova.com/comb?query={message.text}&start=0&limit=15', headers=headers_for_html_requests, proxies=proxies)
    if req.status_code == 200:
        if req.json()['count'] == 0:
            bot.reply_to(message, f'Утечки не найдены для данного ника.\nНо все равно, ставь 2FA и раз в месяц меняй пароль.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        else:
            bot.reply_to(message, f'Найдены утечки!\nКоличество утечек: {str(req.json()["count"])}.\nПоменяйте пароли на всех сервисах и поставьте 2FA.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def crypto_info(message: types.Message):
        if message.text == 'USDT':
            result_usdt_rub = requests.get('https://api.coingecko.com/api/v3/simple/price', params={"ids":'tether', 'vs_currencies':'rub'}, proxies=proxies, headers=headers_for_html_requests).json()['tether']['rub']
            bot.reply_to(message, f'Цена USDT в рублях.\nРубли: {str(result_usdt_rub)}', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))
        elif message.text == 'LTC':
            result_ltc_rub = requests.get('https://api.coingecko.com/api/v3/simple/price', params={"ids":'litecoin', 'currencies':'rub'}, proxies=proxies, headers=headers_for_html_requests).json()['litecoin']['rub']
            bot.reply_to(message, f'Цена LTC в рублях.\nРубли: {str(result_ltc_rub)}', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))
        elif message.text == 'DOGE':
            result_doge_rub = requests.get('https://api.coingecko.com/api/v3/simple/price', params={"ids":'dogecoin', 'vs_currencies':'rub'}, proxies=proxies, headers=headers_for_html_requests).json()['dogecoin']['rub']
            bot.reply_to(message, f'Цена DOGE в рублях.\nРубли: {str(result_doge_rub)}', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))
        elif message.text == 'HMSTR':
            result_hamster_rub = requests.get('https://api.coingecko.com/api/v3/simple/price', params={"ids":'hamster', 'vs_currencies':'rub'}, proxies=proxies, headers=headers_for_html_requests).json()['hamster']['rub']
            bot.reply_to(message, f'Цена HMSTR в рублях.\nРубли: {str(result_hamster_rub)}', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))
        elif message.text == 'BTC':
            result_btc_rub = requests.get('https://api.coingecko.com/api/v3/simple/price', params={"ids":'bitcoin', 'vs_currencies':'rub'}, proxies=proxies, headers=headers_for_html_requests).json()['bitcoin']['rub']
            bot.reply_to(message, f'Цена BTC в рублях.\nРубли: {str(result_btc_rub)}', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))
        else:
            bot.reply_to(message, f'Данной крипты нет в списке!', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))

def deanon(ip: str):
    r = requests.get(f'http://ip-api.com/json/{ip}?lang=ru', proxies=proxies, headers=headers_for_html_requests).json()
    if r['status'] == 'fail':
        return 'Error.'
    else:
        results = []
        for key, value in r.items():
            results.append(value)
        return results

def deanon_by_ip_tg(message: types.Message):
    if not message.text:
        bot.reply_to(message, f'Мы ожидаем текстовое сообщение.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        if deanon(message.text) == 'Error.':
            bot.reply_to(message, f'Извините, но у нас не получилось узнать информацию по данному IP.\nВозможно, его не существует.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        else:
            results = deanon(message.text)
            bot.send_location(message.chat.id, results[7], results[8])
            bot.reply_to(message, f'Информация по IP адресу.\nВНИМАНИЕ! ДАННАЯ ИНФОРМАЦИЯ ВЗЯТА С ОТКРЫТЫХ ИСТОЧИКОВ И ЯВЛЯЕТСЯ НА 100% ЛЕГАЛЬНОЙ И НЕ НАРУШАЕТ ПРАВИЛА TELEGRAM.\n\nСтрана: {results[1]}\nКод страны: {results[2]}\nНазвание региона: {results[4]}\nГород: {results[5]}\nПровайдер: {results[10]}\nКомпания: {results[11]}', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Подсмотреть на Я.Карты', f'https://yandex.ru/maps/?text={results[7]},{results[8]}'), types.InlineKeyboardButton('Назад', callback_data='back')))

def download_by_req_search(message: types.Message, videos: list[YouTube]):
    try:
        video = videos[int(message.text)]
    except:
        bot.reply_to(message, f'Ошибка индекса! Вы должны были выбрать элемент из списка.', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))
    if video.age_restricted:
        bot.reply_to(message, f'Видео имеет возрастные ограничения. Возможно, Вы запросили показать порнографический, или насильственный контент.', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))
    else:
        stream = video.streams.get_lowest_resolution()
        if stream.filesize > 50000000:
            bot.reply_to(message, f'Видео весит больше 50 МБ. Согласно ограничениям Telegram мы не можем Вам его отправить.\nКликните на кнопку, чтобы посмотреть и скачать видео напрямую.', reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('🏡В меню')))
            bot.send_message(message.chat.id, f'Ваша прямая ссылка!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Смотреть видео напрямую.', stream.url)))
        else:
            try:
                name_of_file = random.random()
                progress = bot.send_message(message.chat.id, f'Прогресс.. 0%/100%')
                def progress_func(stream, chunk, bytes_remaining):
                    total_size = stream.filesize
                    bytes_downloaded = total_size - bytes_remaining
                    percentage_complete = bytes_downloaded / total_size * 100
                    now_downloaded = len(chunk) / 1024 / 1024
                    bot.edit_message_text(f'Прогресс.. {percentage_complete:.2f}/100% [{bytes_downloaded:.2f} / {total_size:.2f} B]\n⚡Сейчас скачали: {now_downloaded:.2f} MB', message.chat.id, progress.id)
                    time.sleep(2.5)
                video.register_on_progress_callback(progress_func)
                video.streams.get_lowest_resolution().download(path, f'{name_of_file}.mp4')
                bot.send_chat_action(message.chat.id, 'upload_video')
                likes = requests.get('https://www.googleapis.com/youtube/v3/videos', params={"part":"statistics", "id":video.video_id, "key":google_api_key}, proxies=proxies, headers=headers_for_html_requests).json()
                date = video.publish_date.strftime("%Y-%m-%d %H:%M:%S")
                try:
                    bot.send_video(message.chat.id, open(path / f'{name_of_file}.mp4', 'rb'), caption=f'{video.author} - {video.title}\nКоличество просмотров: {video.views}\nКоличество отметок "нравится": {likes["items"][0]["statistics"]["likeCount"]}\nКоличество комментариев: {likes["items"][0]["statistics"]["commentCount"]}\nДата публикации: {date}', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')), supports_streaming=True)
                except:
                    bot.send_video(message.chat.id, open(path / f'{name_of_file}.mp4', 'rb'), caption=f'{video.author} - {video.title}\nКоличество просмотров: {video.views}\nДата публикации: {date}', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')), supports_streaming=True)
                bot.delete_message(message.chat.id, progress.id)
                os.remove(path / f'{name_of_file}.mp4')
            except:
                bot.delete_message(message.chat.id, message.id)
                bot.delete_message(message.chat.id, progress.id)
                try:
                    os.remove(path / f'{name_of_file}.mp4')
                except:
                    pass
                try:
                    bot.send_animation(message.chat.id, error_gif, caption='Произошла ошибка.\n(Внимание! Есть проблемы со скачиванием контента для детей. Причина еще не выявлена.)', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))
                except:
                    bot.send_message(message.chat.id, 'Произошла ошибка.\n(Внимание! Есть проблемы со скачиванием контента для детей. Причина еще не выявлена.)', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))

def search_by_query(message: types.Message):
    search = Search(message.text, proxies=proxies)
    search_process = bot.reply_to(message, f'Ищем...')
    if len(search.videos) == 0:
        bot.delete_message(search_process.chat.id, search_process.id)
        bot.reply_to(message, f'Ничего по Вашему запросу не было найдено на YouTube.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        bot.delete_message(search_process.chat.id, search_process.id)
        markup = types.ReplyKeyboardMarkup()
        videos = []
        str_videos = []
        for index, video in enumerate(search.videos, 0):
            markup.add(types.KeyboardButton(str(index)))
            videos.append(video)
            str_videos.append(f'{index}. {video.author} - {video.title} ({time.strftime("%H:%M:%S", time.gmtime(video.length))})')
        bot.reply_to(message, f'Выбирете видео из списка:\n' + '\n'.join(str_videos), reply_markup=markup)
        bot.register_next_step_handler(message, download_by_req_search, videos)

def post_create(message: types.Message):
    if message.content_type not in ['document', 'video', 'video_note', 'audio', 'text', 'voice']:
        bot.reply_to(message, f'{message.from_user.first_name}, данная функция поддерживает только фото, видео, кружки, музыку, текстовые сообщения и голосовые сообщения.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        if message.text:
            bot.reply_to(message, f'{message.from_user.first_name}, отправили пост на модерацию. Если все нормально, он будет опубликован в @florestchannel.')
            bot.send_message(7455363246, f'{message.text}\n\n🤵 {message.from_user.first_name}')
        if message.video:
            bot.reply_to(message, f'{message.from_user.first_name}, отправили пост на модерацию. Если все нормально, он будет опубликован в @florestchannel.')
            bot.send_video(7455363246, bot.download_file(bot.get_file(message.video.file_id).file_path), caption=f'🤵 {message.from_user.first_name}')
        if message.video_note:
            bot.reply_to(message, f'{message.from_user.first_name}, отправили пост на модерацию. Если все нормально, он будет опубликован в @florestchannel.')
            bot.send_message(7455363246, f'🤵 {message.from_user.first_name}')
            bot.send_video_note(7455363246, bot.download_file(bot.get_file(message.video_note.file_id).file_path))
        if message.audio:
            bot.reply_to(message, f'{message.from_user.first_name}, отправили пост на модерацию. Если все нормально, он будет опубликован в @florestchannel.')
            bot.send_audio(7455363246, bot.download_file(bot.get_file(message.audio.file_id).file_path), f'🤵 {message.from_user.first_name}', message.audio.duration, message.audio.performer, message.audio.title)
        if message.voice:
            bot.reply_to(message, f'{message.from_user.first_name}, отправили пост на модерацию. Если все нормально, он будет опубликован в @florestchannel.')
            bot.send_voice(7455363246, bot.download_file(bot.get_file(message.voice.file_id).file_path), f'🤵 {message.from_user.first_name}', message.audio.duration)
        if message.document:
            if message.document.file_name[-4:] not in ['.jpg', '.png']:
                bot.reply_to(message, f'{message.from_user.first_name}, мы поддерживаем только фото формата `.jpg` и `.png`.', parse_mode='Markdown', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            else:
                bot.reply_to(message, f'{message.from_user.first_name}, отправили пост на модерацию. Если все нормально, он будет опубликован в @florestchannel.')
                bot.send_photo(7455363246, bot.download_file(bot.get_file(message.document.file_id).file_path), f'🤵 {message.from_user.first_name}')

def create_demotivator_with_pillow(image: io.BytesIO, text: str):
    img = Image.new('RGB', (1280, 1024), color='black')
    img_border = Image.new('RGB', (1060, 720), color='#000000')
    border = ImageOps.expand(img_border, border=2, fill='#ffffff')
    user_img = Image.open(image).convert("RGBA").resize((1050, 710))
    (width, height) = user_img.size
    img.paste(border, (111, 96))
    img.paste(user_img, (118, 103))
    drawer = ImageDraw.Draw(img)
    font_1 = ImageFont.truetype(font='times.ttf', size=80, encoding='UTF-8')
    text_width = font_1.getlength(water_sign)

    while text_width >= (width + 250) - 20:
        font_1 = ImageFont.truetype(font='times.ttf', size=80, encoding='UTF-8')
        text_width = font_1.getlength(water_sign)
        top_size -= 1

    font_2 = ImageFont.truetype(font='times.ttf', size=60, encoding='UTF-8')
    text_width = font_2.getlength(text)

    while text_width >= (width + 250) - 20:
        font_2 = ImageFont.truetype(font='times.ttf', size=60, encoding='UTF-8')
        text_width = font_2.getlength(text)
        bottom_size -= 1

    size_1 = drawer.textlength(water_sign, font=font_1)
    size_2 = drawer.textlength(text, font=font_2)

    drawer.text(((1280 - size_1) / 2, 840), water_sign, fill='white', font=font_1)
    drawer.text(((1280 - size_2) / 2, 930), text, fill='white', font=font_2)

    result_here = io.BytesIO()

    img.save(result_here, 'JPEG')
    
    del drawer

    return result_here.getvalue()


def make_demotivator(message: types.Message, file: bytes):
    if not message.text:
        bot.reply_to(message, f'{message.from_user.first_name}, мы принимаем только текстовые сообщения в данном аргументе.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        bot.send_photo(message.chat.id, create_demotivator_with_pillow(io.BytesIO(file), message.text), caption=f'Ваш демотиватор.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def image_priem_to_demotivator(message: types.Message):
    if not message.document:
        bot.reply_to(message, f'{message.from_user.first_name}, мы принимаем только одно изображение без сжатия.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        if message.document.file_name[-4:] not in ['.jpg', '.png']:
            bot.reply_to(message, f'{message.from_user.first_name}, данная функция принимает файлы с разрешением `.png` и `.jpg`.', parse_mode='Markdown', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        try:
            bot.send_animation(message.chat.id, give_me_gif, caption='Спс. А теперь напиши текст, который будет в демотиваторе.')
        except telebot.apihelper.ApiTelegramException:
            bot.send_message(message.chat.id, 'Спс. А теперь напиши текст, который будет в демотиваторе.')
        bot.register_next_step_handler(message, make_demotivator, bot.download_file(bot.get_file(message.document.file_id).file_path))

def download_video_func___(message: types.Message, url: str):
    if message.text == 'Видео':
        msg = bot.reply_to(message, f'Качаем видео...', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))
        progress = bot.send_message(message.chat.id, f'Прогресс... 0%/100%')
        try:
            def progress_func(stream, chunk, bytes_remaining):
                total_size = stream.filesize
                bytes_downloaded = total_size - bytes_remaining
                percentage_complete = bytes_downloaded / total_size * 100
                now_downloaded = len(chunk) / 1024 / 1024
                bot.edit_message_text(f'Прогресс.. {percentage_complete:.2f}/100% [{bytes_downloaded:.2f} / {total_size:.2f} B]\n⚡Сейчас скачали: {now_downloaded:.2f} MB', message.chat.id, progress.id)
                time.sleep(2.5)
            yt_obj = YouTube(url, proxies=proxies, on_progress_callback=progress_func)
            if not is_youtube_banned(yt_obj.video_id):
                    if not is_youtube_banned(yt_obj.channel_id):
                        if yt_obj.age_restricted:
                            bot.delete_message(message.chat.id, msg.id)
                            bot.delete_message(message.chat.id, progress.id)
                            bot.reply_to(message, f'Нельзя скачать видео с возрастными ограничениями.', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))
                        else:
                            stream = yt_obj.streams.get_lowest_resolution()
                            if stream.filesize > 50000000:
                                bot.delete_message(message.chat.id, msg.id)
                                bot.delete_message(message.chat.id, progress.id)
                                bot.reply_to(message, f'Видео весит больше 50 МБ. Согласно ограничениям Telegram мы не можем Вам его отправить.\nКликните на кнопку, чтобы посмотреть и скачать видео напрямую.', reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('🏡В меню')))
                                bot.send_message(message.chat.id, f'Ваша прямая ссылка!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Смотреть видео напрямую.', stream.url)))
                            else:
                                name_of_file = random.random()
                                stream.download(path, f'{name_of_file}.mp4')
                                bot.delete_message(message.chat.id, msg.id)
                                bot.delete_message(message.chat.id, progress.id)
                                bot.send_chat_action(message.chat.id, f'upload_video')
                                likes = requests.get('https://www.googleapis.com/youtube/v3/videos', params={"part":"statistics", "id":yt_obj.video_id, "key":google_api_key}, proxies=proxies, headers=headers_for_html_requests).json()
                                date = yt_obj.publish_date.strftime("%Y-%m-%d %H:%M:%S")
                                try:
                                    bot.send_video(message.chat.id, open(path / f'{name_of_file}.mp4', 'rb'), yt_obj.length, caption=f'{yt_obj.author} - {yt_obj.title}\nКоличество просмотров: {yt_obj.views}\nКоличество отметок "нравится": {likes["items"][0]["statistics"]["likeCount"]}\nКоличество комментариев: {likes["items"][0]["statistics"]["commentCount"]}\nОпубликовано: {date}', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')), supports_streaming=True)
                                except:
                                    bot.send_video(message.chat.id, open(path / f'{name_of_file}.mp4', 'rb'), yt_obj.length, caption=f'{yt_obj.author} - {yt_obj.title}\nКоличество просмотров: {yt_obj.views}\nОпубликовано: {date}', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')), supports_streaming=True)
                                os.remove(path / f'{name_of_file}.mp4')
                    else:
                        bot.reply_to(message, f'Канал был заблокирован.', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))
            else:
                    bot.reply_to(message, f'Видео было заблокировано.', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))
        except Exception as e:
                print(e)
                bot.delete_message(message.chat.id, msg.id)
                bot.delete_message(message.chat.id, progress.id)
                try:
                    os.remove(path / f'{name_of_file}.mp4')
                except:
                    pass
                try:
                    bot.send_animation(message.chat.id, error_gif, caption=f'Произошла ошибка.\nВозможно, мы не смогли найти нужные стримы для данного видео.\nИли оно не существует.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
                except telebot.apihelper.ApiTelegramException:
                    bot.send_message(message.chat.id, f'Произошла ошибка.\nВозможно, мы не смогли найти нужные стримы для данного видео.\nИли оно не существует.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
    elif message.text == 'Аудио':
        msg = bot.reply_to(message, f'Качаем аудио...', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))
        progress = bot.send_message(message.chat.id, f'Прогресс... 0%/100%')
        def progress_func(stream, chunk, bytes_remaining):
                total_size = stream.filesize
                bytes_downloaded = total_size - bytes_remaining
                percentage_complete = bytes_downloaded / total_size * 100
                now_downloaded = len(chunk) / 1024 / 1024
                bot.edit_message_text(f'Прогресс.. {percentage_complete:.2f}/100% [{bytes_downloaded:.2f} / {total_size:.2f} B]\n⚡Сейчас скачали: {now_downloaded:.2f} MB', message.chat.id, progress.id)
                time.sleep(2.5)
        try:
            yt_obj = YouTube(url, proxies=proxies, on_progress_callback=progress_func)
            if not is_youtube_banned(yt_obj.video_id):
                if not is_youtube_banned(yt_obj.channel_id):
                    if yt_obj.age_restricted:
                        bot.delete_message(message.chat.id, msg.id)
                        bot.delete_message(message.chat.id, progress.id)
                        bot.reply_to(message, f'Нельзя скачать аудио с видео с возрастными ограничениями.', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))
                    else:
                        stream = yt_obj.streams.get_audio_only()
                        if stream.filesize > 50000000:
                            bot.delete_message(message.chat.id, msg.id)
                            bot.delete_message(message.chat.id, progress.id)
                            bot.reply_to(message, f'Видео весит больше 50 МБ. Согласно ограничениям Telegram мы не можем Вам его отправить.\nКликните на кнопку, чтобы посмотреть и скачать видео напрямую.', reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('🏡В меню')))
                            bot.send_message(message.chat.id, f'Ваша прямая ссылка!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Смотреть видео напрямую.', stream.url)))
                        else:
                            name_of_file = random.random()
                            stream.download(path, f'{name_of_file}.mp3')
                            bot.delete_message(message.chat.id, msg.id)
                            bot.delete_message(message.chat.id, progress.id)
                            bot.send_chat_action(message.chat.id, f'upload_voice')
                            date = yt_obj.publish_date.strftime("%Y-%m-%d %H:%M:%S")
                            likes = requests.get('https://www.googleapis.com/youtube/v3/videos', params={"part":"statistics", "id":yt_obj.video_id, "key":google_api_key}, proxies=proxies, headers=headers_for_html_requests).json()
                            try:
                                bot.send_audio(message.chat.id, open(path / f'{name_of_file}.mp3', 'rb'), duration=yt_obj.length, caption=f'{yt_obj.author} - {yt_obj.title}\nКоличество просмотров: {yt_obj.views}\nКоличество отметок "нравится": {likes["items"][0]["statistics"]["likeCount"]}\nКоличество комментариев: {likes["items"][0]["statistics"]["commentCount"]}\nДата публикации: {date}', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')), performer=yt_obj.author, title=yt_obj.title)
                            except:
                                bot.send_audio(message.chat.id, open(path / f'{name_of_file}.mp3', 'rb'), duration=yt_obj.length, caption=f'{yt_obj.author} - {yt_obj.title}\nКоличество просмотров: {yt_obj.views}\nДата публикации: {date}', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')), performer=yt_obj.author, title=yt_obj.title)
                            os.remove(path / f'{name_of_file}.mp3')
                else:
                    bot.reply_to(message, f'Канал был заблокирован.', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))
            else:
                bot.reply_to(message, f'Видео было заблокировано.', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))
        except Exception as e:
            print(e)
            bot.delete_message(message.chat.id, progress.id)
            bot.delete_message(message.chat.id, msg.id)
            try:
                os.remove(path / f'{name_of_file}.mp3')
            except:
                pass
            try:
                bot.send_animation(message.chat.id, error_gif, caption=f'Произошла ошибка.\nВозможно, мы не смогли найти нужные стримы для данного видео.\nИли оно не существует.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
            except:
                bot.send_message(message.chat.id, f'Произошла ошибка.\nВозможно, мы не смогли найти нужные стримы для данного видео.\nИли оно не существует.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))

def download_youtube_video_func(message: types.Message):
    bot.reply_to(message, f'Отлично!\nВидео, или только аудио?', reply_markup=types.ReplyKeyboardMarkup(row_width=1).add(types.KeyboardButton('Видео'), types.KeyboardButton('Аудио')))
    bot.register_next_step_handler(message, download_video_func___, message.text)

def dialog_in_bot(message: types.Message) -> None:
    if message.text:
        bot.reply_to(message, f'Сообщение было отправлено. Ожидайте ответ.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='leave_chat')))
        msg=bot.send_message(7455363246, f'Сообщение от пользователя ({message.from_user.first_name}): {message.text}\n{message.from_user.id}')
        bot.register_next_step_handler(message, dialog_in_bot)
    else:
        bot.reply_to(message, f'Поддерживаются только текстовые сообщения. Напишите свое сообщение еще раз, пожалуйста.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='leave_chat')))
        bot.register_next_step_handler(message, dialog_in_bot)

def get_channel_details(message: types.Message):
    msg=bot.reply_to(message, f'Обработка запроса, пожалуйста, подождите...')
    try:
        if '/channel/' in message.text:
            channel_id = message.text.split('/channel/')[-1].split('?')[0]
            params = {
                "part": "snippet,statistics",
                "id": channel_id,
                "key": google_api_key
            }
        else:
            username = message.text.split('/@')[-1].split('?')[0]
            print(username)
            params = {
                "part": "snippet,statistics",
                "forHandle": f"@{username}",
                "key": google_api_key
            }
        request = requests.get(
            "https://www.googleapis.com/youtube/v3/channels",
            params=params,
            proxies=proxies
        )
        response = request.json()
        print(response)
        response_photo = requests.get(f'{response["items"][0]["snippet"]["thumbnails"]["high"]["url"]}', headers=headers_for_html_requests, proxies=proxies)
        bot.send_photo(message.chat.id, response_photo.content, caption=f'⚠️Информация и статистика о канале "`{response["items"][0]["snippet"]["title"]}`":\n\n**ИНФОРМАЦИЯ**\n🌐 Псевдоним: `{response["items"][0]["snippet"]["customUrl"]}`\n⛳ Страна: `{response["items"][0]["snippet"]["country"]}`\n\n**СТАТИСТИКА**\n👁️ Всего просмотров: `{response["items"][0]["statistics"]["viewCount"]}`\n♥️ Количество подписчиков: `{response["items"][0]["statistics"]["subscriberCount"]}`\n🎥 Количество видео на канале: `{response["items"][0]["statistics"]["videoCount"]}`', parse_mode='MarkdownV2', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        bot.delete_message(message.chat.id, msg.id)
    except Exception as e:
        print(e)
        bot.delete_message(message.chat.id, msg.id)
        try:
            bot.send_animation(message.chat.id, error_gif, caption=f'Произошла ошибка. Скорее всего данного канала не существует.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
        except telebot.apihelper.ApiTelegramException:
            bot.send_message(message.chat.id, f'Произошла ошибка. Скорее всего данного канала не существует.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))

def delete_messages_bro(message: types.Message):
    try:
        messages_to_delete = []
        for m in range(message.message_id - int(message.text), message.message_id):
            messages_to_delete.append(m)
        bot.delete_messages(message.chat.id, messages_to_delete)
        messages_to_delete.clear()
    except:
        bot.reply_to(message, f'Произошла ошибка!\nНужно написать число в качестве аргумента, также заметьте, что функция не может удалить более 100 сообщений, а также им должно быть не более двух дней.')


def check_text(text: str):
    for i in banned_words:
        if i in text.lower():
            return True
        else:
            pass
    return False

def check_user(user: int):
    if str(user) in open(path / 'banned_users.txt').readlines():
        return True
    else:
        return False

def check_sub(user_id: int):
    member = bot.get_chat_member(telegram_channel_id, user_id).status
    if member in ['kicked', 'left']:
        return False
    else:
        return True

def send_reaction(chat_id: int, message_id: int, emoji: str):
    requests.post(f'https://api.telegram.org/bot{token}/setMessageReaction', json={"chat_id":chat_id, 'message_id':message_id, 'reaction':[{'type':'emoji', 'emoji':emoji}], 'is_big':False})

def download_music():
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,fi;q=0.6,nb;q=0.5,is;q=0.4,pt;q=0.3,ro;q=0.2,it;q=0.1,de;q=0.1',
        'Connection': 'keep-alive',
        'Referer': 'https://music.yandex.ru/chart',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'X-Current-UID': '403036463',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Retpath-Y': 'https://music.yandex.ru/chart',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
    }

    params = {
        'what': 'chart',
        'lang': 'ru',
        'external-domain': 'music.yandex.ru',
        'overembed': 'false',
        'ncrnd': '0.23800355071570123',
    }
    result = []
    response = requests.get('https://music.yandex.ru/handlers/main.jsx', params=params, headers=headers)
    chart = response.json()['chartPositions']
    for track in chart[:10]:
        position = track['track']['chart']['position']
        title = track['track']['title']
        author = track['track']['artists'][0]['name']
        result.append(f"№{position}: {author} - {title}")
    return f'Чарты Яндекс Музыки на данный момент🔥\n🥇{result[0]}\n🥈{result[1]}\n🥉{result[2]}\n{result[3]}\n{result[4]}\n{result[5]}\n{result[6]}\n{result[7]}\n{result[8]}\n{result[9]}'

def mute_human(message: types.Message, id: int):
    human = bot.get_chat_member(message.chat.id, id).user
    if message.text.lower() == 'infinity':
        bot.restrict_chat_member(message.chat.id, id, None, False, False, False, False, False, False, False, False)
        bot.reply_to(message, f'Участник был успешно заглушен навсегда.')
    else:
        try:
            if int(message.text) >= 30:
                bot.restrict_chat_member(message.chat.id, id, time.time()+int(message.text), None, False, False, False, False, False, False, False)
                bot.reply_to(message, f'Участник был успешно заглушен на {message.text} секунд.')
            else:
                bot.reply_to(message, f'Нельзя замьютить меньше чем 30 секунд и более чем на 366 дней.')
        except Exception as e:
            bot.reply_to(message, f'Можно использовать только целые числа, а также слово "infinity", другие значения не допускаются.')
            print(e)

@bot.message_handler(commands=['start'])
def welcome(message: types.Message):
    if message.chat.type == 'private':
            if len(message.text.split()) == 1:
                if check_sub(message.from_user.id):
                    markup1 = types.InlineKeyboardMarkup(row_width=1)
                    button1 = types.InlineKeyboardButton(f'Инфа о боте', url='https://telegra.ph/INFORMACIYA-O-BOTE-06-27')
                    button21 = types.InlineKeyboardButton('Telegram канал', 'https://t.me/florestchannel')
                    button31 = types.InlineKeyboardButton('Другие ресурсы Флореста', url='https://taplink.cc/florestone4185')
                    markup1.add(button1, button21, button31, types.InlineKeyboardButton('Поделиться ботом с другом', f'https://t.me/share/url?url=https://t.me/postbotflorestbot?start={message.from_user.id}&&text=Привет, советую тебе эту имбульку! Там очень много функций и они все бесплатные!'))
                    try:
                        bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, {message.from_user.first_name}\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})\nНаш API: [тык](https://florestapi-florestdev4185.amvera.io)', reply_markup=markup1, parse_mode='MarkdownV2')
                    except:
                        bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, пользователь\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})\nНаш API: [тык](https://florestapi-florestdev4185.amvera.io)', reply_markup=markup1, parse_mode='MarkdownV2')
                    msg=bot.send_message(message.chat.id, f'Утилиты бота', reply_markup=buttons)
                    bot.reply_to(msg, f'На будущее, вдруг меню пропадет.', reply_markup=types.ReplyKeyboardMarkup(True, input_field_placeholder=f'Сэр, да, сэр.', row_width=1).add(types.KeyboardButton('🏡В меню')))
                else:
                    bot.reply_to(message, f'Ты не подписался на Telegram канал создателя?\nПора-бы это сделать!', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Мой Telegram канал', 'https://t.me/florestchannel'), types.InlineKeyboardButton('Подтвердить подписку', callback_data='check_sub')))
            else:
                try:
                    id = int(message.text.split()[1])
                    if len(message.text.split()[1]) > 10:
                        bot.reply_to(message, f'Неправильная реферальная ссылка.')
                        if check_sub(message.from_user.id):
                            markup1 = types.InlineKeyboardMarkup(row_width=1)
                            button1 = types.InlineKeyboardButton(f'Инфа о боте', url='https://telegra.ph/INFORMACIYA-O-BOTE-06-27')
                            button21 = types.InlineKeyboardButton('Telegram канал', 'https://t.me/florestchannel')
                            button31 = types.InlineKeyboardButton('Другие ресурсы Флореста', url='https://taplink.cc/florestone4185')
                            markup1.add(button1, button21, button31, types.InlineKeyboardButton('Поделиться ботом с другом', f'https://t.me/share/url?url=https://t.me/postbotflorestbot?start={message.from_user.id}&&text=Привет, советую тебе эту имбульку! Там очень много функций и они все бесплатные!'))
                            try:
                                bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, {message.from_user.first_name}\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})\nНаш API: [тык](https://florestapi-florestdev4185.amvera.io)', reply_markup=markup1, parse_mode='MarkdownV2')
                            except:
                                bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, пользователь\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})\nНаш API: [тык](https://florestapi-florestdev4185.amvera.io)', reply_markup=markup1, parse_mode='MarkdownV2')
                            msg=bot.send_message(message.chat.id, f'Утилиты бота', reply_markup=buttons)
                            bot.reply_to(msg, f'На будущее, вдруг меню пропадет.', reply_markup=types.ReplyKeyboardMarkup(True, input_field_placeholder=f'Сэр, да, сэр.', row_width=1).add(types.KeyboardButton('🏡В меню')))
                        else:
                            bot.reply_to(message, f'Ты не подписался на Telegram канал создателя?\nПора-бы это сделать!', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Мой Telegram канал', 'https://t.me/florestchannel'), types.InlineKeyboardButton('Подтвердить подписку', callback_data='check_sub')))
                    elif len(message.text.split()[1]) < 10:
                        bot.reply_to(message, f'Неправильная реферальная ссылка.')
                        if check_sub(message.from_user.id):
                            markup1 = types.InlineKeyboardMarkup(row_width=1)
                            button1 = types.InlineKeyboardButton(f'Инфа о боте', url='https://telegra.ph/INFORMACIYA-O-BOTE-06-27')
                            button21 = types.InlineKeyboardButton('Telegram канал', 'https://t.me/florestchannel')
                            button31 = types.InlineKeyboardButton('Другие ресурсы Флореста', url='https://taplink.cc/florestone4185')
                            markup1.add(button1, button21, button31, types.InlineKeyboardButton('Поделиться ботом с другом', f'https://t.me/share/url?url=https://t.me/postbotflorestbot?start={message.from_user.id}&&text=Привет, советую тебе эту имбульку! Там очень много функций и они все бесплатные!'))
                            try:
                                bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, {message.from_user.first_name}\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})\nНаш API: [тык](https://florestapi-florestdev4185.amvera.io)', reply_markup=markup1, parse_mode='MarkdownV2')
                            except:
                                bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, пользователь\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})\nНаш API: [тык](https://florestapi-florestdev4185.amvera.io)', reply_markup=markup1, parse_mode='MarkdownV2')
                            msg=bot.send_message(message.chat.id, f'Утилиты бота', reply_markup=buttons)
                            bot.reply_to(msg, f'На будущее, вдруг меню пропадет.', reply_markup=types.ReplyKeyboardMarkup(True, input_field_placeholder=f'Сэр, да, сэр.', row_width=1).add(types.KeyboardButton('🏡В меню')))
                        else:
                            bot.reply_to(message, f'Ты не подписался на Telegram канал создателя?\nПора-бы это сделать!', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Мой Telegram канал', 'https://t.me/florestchannel'), types.InlineKeyboardButton('Подтвердить подписку', callback_data='check_sub')))
                    else:
                        if id != message.from_user.id:
                            try:
                                bot.send_message(id, f'По Вашей реферальной ссылке перешел {message.from_user.full_name}.\nСпасибо за приведенного реферала!')
                            except:
                                pass
                            bot.reply_to(message, f'Добро пожаловать в бота! Вас пригласил {bot.get_chat_member(telegram_channel_id, id).user.full_name} в бота.')
                            if check_sub(message.from_user.id):
                                markup1 = types.InlineKeyboardMarkup(row_width=1)
                                button1 = types.InlineKeyboardButton(f'Инфа о боте', url='https://telegra.ph/INFORMACIYA-O-BOTE-06-27')
                                button21 = types.InlineKeyboardButton('Telegram канал', 'https://t.me/florestchannel')
                                button31 = types.InlineKeyboardButton('Другие ресурсы Флореста', url='https://taplink.cc/florestone4185')
                                markup1.add(button1, button21, button31, types.InlineKeyboardButton('Поделиться ботом с другом', f'https://t.me/share/url?url=https://t.me/postbotflorestbot?start={message.from_user.id}&&text=Привет, советую тебе эту имбульку! Там очень много функций и они все бесплатные!'))
                                try:
                                    bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, {message.from_user.first_name}\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})\nНаш API: [тык](https://florestapi-florestdev4185.amvera.io)', reply_markup=markup1, parse_mode='MarkdownV2')
                                except:
                                    bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, пользователь\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})\nНаш API: [тык](https://florestapi-florestdev4185.amvera.io)', reply_markup=markup1, parse_mode='MarkdownV2')
                                msg=bot.send_message(message.chat.id, f'Утилиты бота', reply_markup=buttons)
                                bot.reply_to(msg, f'На будущее, вдруг меню пропадет.', reply_markup=types.ReplyKeyboardMarkup(True, input_field_placeholder=f'Сэр, да, сэр.', row_width=1).add(types.KeyboardButton('🏡В меню')))
                            else:
                                bot.reply_to(message, f'Ты не подписался на Telegram канал создателя?\nПора-бы это сделать!', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Мой Telegram канал', 'https://t.me/florestchannel'), types.InlineKeyboardButton('Подтвердить подписку', callback_data='check_sub')))
                        else:
                            bot.reply_to(message, f'Нельзя зайти по своей же реферальной ссылке!')
                            if check_sub(message.from_user.id):
                                markup1 = types.InlineKeyboardMarkup(row_width=1)
                                button1 = types.InlineKeyboardButton(f'Инфа о боте', url='https://telegra.ph/INFORMACIYA-O-BOTE-06-27')
                                button21 = types.InlineKeyboardButton('Telegram канал', 'https://t.me/florestchannel')
                                button31 = types.InlineKeyboardButton('Другие ресурсы Флореста', url='https://taplink.cc/florestone4185')
                                markup1.add(button1, button21, button31, types.InlineKeyboardButton('Поделиться ботом с другом', f'https://t.me/share/url?url=https://t.me/postbotflorestbot?start={message.from_user.id}&&text=Привет, советую тебе эту имбульку! Там очень много функций и они все бесплатные!'))
                                try:
                                    bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, {message.from_user.first_name}\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})\nНаш API: [тык](https://florestapi-florestdev4185.amvera.io)', reply_markup=markup1, parse_mode='MarkdownV2')
                                except:
                                    bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, пользователь\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})\nНаш API: [тык](https://florestapi-florestdev4185.amvera.io)', reply_markup=markup1, parse_mode='MarkdownV2')
                                msg=bot.send_message(message.chat.id, f'Утилиты бота', reply_markup=buttons)
                                bot.reply_to(msg, f'На будущее, вдруг меню пропадет.', reply_markup=types.ReplyKeyboardMarkup(True, input_field_placeholder=f'Сэр, да, сэр.', row_width=1).add(types.KeyboardButton('🏡В меню')))
                            else:
                                bot.reply_to(message, f'Ты не подписался на Telegram канал создателя?\nПора-бы это сделать!', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Мой Telegram канал', 'https://t.me/florestchannel'), types.InlineKeyboardButton('Подтвердить подписку', callback_data='check_sub')))
                except Exception as e:
                    print(e)
                    bot.reply_to(message, f'Неправильная реферальная ссылка!')
                    if check_sub(message.from_user.id):
                        markup1 = types.InlineKeyboardMarkup(row_width=1)
                        button1 = types.InlineKeyboardButton(f'Инфа о боте', url='https://telegra.ph/INFORMACIYA-O-BOTE-06-27')
                        button21 = types.InlineKeyboardButton('Telegram канал', 'https://t.me/florestchannel')
                        button31 = types.InlineKeyboardButton('Другие ресурсы Флореста', url='https://taplink.cc/florestone4185')
                        markup1.add(button1, button21, button31, types.InlineKeyboardButton('Поделиться ботом с другом', f'https://t.me/share/url?url=https://t.me/postbotflorestbot?start={message.from_user.id}&&text=Привет, советую тебе эту имбульку! Там очень много функций и они все бесплатные!'))
                        try:
                            bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, {message.from_user.first_name}\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})\nНаш API: [тык](https://florestapi-florestdev4185.amvera.io)', reply_markup=markup1, parse_mode='MarkdownV2')
                        except:
                            bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, пользователь\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})\nНаш API: [тык](https://florestapi-florestdev4185.amvera.io)', reply_markup=markup1, parse_mode='MarkdownV2')
                        msg=bot.send_message(message.chat.id, f'Утилиты бота', reply_markup=buttons)
                        bot.reply_to(msg, f'На будущее, вдруг меню пропадет.', reply_markup=types.ReplyKeyboardMarkup(True, input_field_placeholder=f'Сэр, да, сэр.', row_width=1).add(types.KeyboardButton('🏡В меню')))
                    else:
                        bot.reply_to(message, f'Ты не подписался на Telegram канал создателя?\nПора-бы это сделать!', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Мой Telegram канал', 'https://t.me/florestchannel'), types.InlineKeyboardButton('Подтвердить подписку', callback_data='check_sub')))

@bot.message_handler(commands=['support'])
def support(message: types.Message):
    if message.chat.type == 'private':
        bot.reply_to(message, f'Связаться со мной по поводу ошибок бота, либо сотрудничества или по другим причинам.\nМоя почта: florestone4185@internet.ru\nМой Discord аккаунт: florestdev\nЛибо нажмите кнопки ниже.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Написать на почту', 'https://inlnk.ru/oeaxRw'), types.InlineKeyboardButton('Поговорить внутри бота', callback_data='dialog-by-bot')))

def ai_obrabotchik(message: types.Message, type: int, mode: str = 'text'):
    if type == 1:
        if message.text:
            img = client_for_gpt.images.generate(message.text, 'flux-pro', RetryProvider([Together, ARTA, PollinationsImage]), 'url', proxies.get('http'))
            bot.send_chat_action(message.chat.id, 'upload_photo')
            bot.send_photo(message.chat.id, requests.get(img.data[0].url, proxies=proxies).content, f'Модель: `flux-pro`.\n\nИзображение по Вашему запросу.\nМогут быть неточности. Если они присутствуют, попробуйте изменить язык на котором вы пишите запрос, или его формулировку.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Оригинал', url=img.data[0].url), types.InlineKeyboardButton('Назад', callback_data='back')), parse_mode='Markdown')
            bot.clear_step_handler_by_chat_id(message.chat.id)
        else:
            bot.reply_to(message, f'Поддерживаются только текстовые сообщения.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    elif type == 2:
        if mode == 'text':
            if not message.reply_to_message:
                if message.text:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                    bot.send_chat_action(message.chat.id, 'typing')
                    
                    result = client_for_gpt.chat.completions.create([{"role":"user", 'content':message.text}], 'gpt-4o-mini', RetryProvider([PollinationsAI, Chatai, OIVSCodeSer2, Blackbox, LegacyLMArena, PollinationsAI]), max_tokens=4096, proxy=proxies.get('http'), web_search=True).choices[0].message.content

                    for i in range(0, len(result), 4096):
                        chunk = result[i:i + 4096] 
                        bot.reply_to(message, chunk, reply_markup=markup, parse_mode='Markdown')
                        time.sleep(1.5)
                    bot.register_next_step_handler(message, ai_obrabotchik, 2, 'text')
                elif message.voice:
                    chislo = random.randint(1, 10000)
                    audio__ = open(path / f'audio_{chislo}.ogg', 'wb')
                    audio__.write(bot.download_file(bot.get_file(message.voice.file_id).file_path))
                    audio__.close()
                    subprocess.run(['ffmpeg', '-i', f'audio_{chislo}.ogg', f'audio_{chislo}.wav'])
                    try:
                        r = sr.Recognizer()
                        file = open(path / f'audio_{chislo}.wav', 'rb')
                        with sr.AudioFile(file) as source:
                            audio = r.record(source)
                        text = r.recognize_google(audio, language='ru-RU')
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                        bot.send_chat_action(message.chat.id, 'typing')
                        result = client_for_gpt.chat.completions.create([{"role":"user", 'content':text}], 'gpt-4o-mini', RetryProvider([PollinationsAI, Chatai, OIVSCodeSer2, Blackbox, LegacyLMArena, PollinationsAI]), max_tokens=4096, proxy=proxies.get('http'), web_search=True).choices[0].message.content

                        for i in range(0, len(result), 4096):
                            chunk = result[i:i + 4096] 
                            bot.reply_to(message, chunk, reply_markup=markup, parse_mode='Markdown')
                            time.sleep(1.5)
                        bot.register_next_step_handler(message, ai_obrabotchik, 2, 'text')
                    except sr.UnknownValueError:
                        bot.reply_to(message, f'Не удалось распознать речь в голосовом сообщении.\nПопробуйте еще раз!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Завершить чат', reply_markup='chat_zaversit')))
                        bot.register_next_step_handler(message, ai_obrabotchik, 2, 'text')
                    except:
                        bot.reply_to(message, f'Неизвестная ошибка.\nВоспользуйтесь текстовым вводом.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Завершить чат', reply_markup='chat_zaversit')))
                        bot.register_next_step_handler(message, ai_obrabotchik, 2, 'text')
                    os.remove(path / f'audio_{chislo}.ogg')
                    os.remove(path / f'audio_{chislo}.wav')
                elif message.document:
                    if message.document.file_name[-4:] in ['.jpg', '.png']:
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                        image = bot.download_file(bot.get_file(message.document.file_id).file_path)
                        try:
                            if message.caption:
                                result = client_for_gpt.chat.completions.create([{"role":"user", 'content':message.caption}], 'gpt-4o-mini', PollinationsAI, image=image, web_search=True, proxy=proxies.get('http')).choices[0].message.content
                            else:
                                result = client_for_gpt.chat.completions.create([{"role":"user", 'content':'Что изображено на фотографии?'}], 'gpt-4o-mini', PollinationsAI, image=image, web_search=True, proxy=proxies.get('http')).choices[0].message.content
                            for i in range(0, len(result), 4096):
                                chunk = result[i:i + 4096] 
                                bot.reply_to(message, chunk, reply_markup=markup, parse_mode='Markdown')
                                time.sleep(1.5)
                        except Exception as e:
                            bot.reply_to(message, f'Ошибка: {e}\nПопробуйте отправить другое фото, или сжать его.', reply_markup=markup)
                        bot.register_next_step_handler(message, ai_obrabotchik, 2, 'text')
                    else:
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                        bot.reply_to(message, f'Сообщение не является текстом, голосовым сообщением или фото!', reply_markup=markup)
                        bot.register_next_step_handler(message, ai_obrabotchik, 2, 'text')
                else:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                    bot.reply_to(message, f'Сообщение не является текстом, голосовым сообщением или фото!', reply_markup=markup)
                    bot.register_next_step_handler(message, ai_obrabotchik, 2, 'text')
            else:
                if message.text:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                    bot.send_chat_action(message.chat.id, 'typing')
                    result = client_for_gpt.chat.completions.create([{"role":"user", 'content':f'Контекст прошлого сообщения: {message.reply_to_message.text}' + message.text}], 'gpt-4o-mini', RetryProvider([PollinationsAI, Chatai, OIVSCodeSer2, Blackbox, LegacyLMArena, PollinationsAI]), max_tokens=4096, proxy=proxies.get('http'), web_search=True).choices[0].message.content
                    for i in range(0, len(result), 4096):
                        chunk = result[i:i + 4096] 
                        bot.reply_to(message, chunk, reply_markup=markup, parse_mode='Markdown')
                        time.sleep(1.5)
                    bot.register_next_step_handler(message, ai_obrabotchik, 2, 'text')
                elif message.voice:
                    chislo = random.randint(1, 10000)
                    audio__ = open(path / f'audio_{chislo}.ogg', 'wb')
                    audio__.write(bot.download_file(bot.get_file(message.voice.file_id).file_path))
                    audio__.close()
                    subprocess.run(['ffmpeg', '-i', f'audio_{chislo}.ogg', f'audio_{chislo}.wav'])
                    try:
                        r = sr.Recognizer()
                        file = open(path / f'audio_{chislo}.wav', 'rb')
                        with sr.AudioFile(file) as source:
                            audio = r.record(source)
                        text = r.recognize_google(audio, language='ru-RU')
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                        bot.send_chat_action(message.chat.id, 'typing')
                        result = client_for_gpt.chat.completions.create([{"role":"user", 'content':f'Контекст прошлого сообщения: {message.reply_to_message.text}' + text}], 'gpt-4o-mini', RetryProvider([PollinationsAI, Chatai, OIVSCodeSer2, Blackbox, LegacyLMArena, PollinationsAI]), max_tokens=4096, proxy=proxies.get('http'), web_search=True).choices[0].message.content
                        for i in range(0, len(result), 4096):
                            chunk = result[i:i + 4096] 
                            bot.reply_to(message, chunk, reply_markup=markup, parse_mode='Markdown')
                            time.sleep(1.5)
                        bot.register_next_step_handler(message, ai_obrabotchik, 2, 'text')
                    except sr.UnknownValueError:
                        bot.reply_to(message, f'Не удалось распознать речь в голосовом сообщении.\nПопробуйте еще раз!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Завершить чат', reply_markup='chat_zaversit')))
                        bot.register_next_step_handler(message, ai_obrabotchik, 2, 'text')
                    except:
                        bot.reply_to(message, f'Неизвестная ошибка.\nВоспользуйтесь текстовым вводом.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Завершить чат', reply_markup='chat_zaversit')))
                        bot.register_next_step_handler(message, ai_obrabotchik, 2, 'text')
                    os.remove(path / f'audio_{chislo}.ogg')
                    os.remove(path / f'audio_{chislo}.wav')
                elif message.document:
                    if message.document.file_name[-4:] in ['.jpg', '.png']:
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                        image = bot.download_file(bot.get_file(message.document.file_id).file_path)
                        try:
                            if message.caption:
                                result = client_for_gpt.chat.completions.create([{"role":"user", 'content':message.caption}], 'gpt-4o-mini', PollinationsAI, image=image, web_search=True, proxy=proxies.get('http')).choices[0].message.content
                            else:
                                result = client_for_gpt.chat.completions.create([{"role":"user", 'content':'Что изображено на фотографии?'}], 'gpt-4o-mini', PollinationsAI, image=image, web_search=True, proxy=proxies.get('http')).choices[0].message.content
                            for i in range(0, len(result), 4096):
                                chunk = result[i:i + 4096] 
                                bot.reply_to(message, chunk, reply_markup=markup, parse_mode='Markdown')
                                time.sleep(1.5)
                        except Exception as e:
                            bot.reply_to(message, f'Ошибка: {e}\nПопробуйте отправить другое фото, или сжать его.', reply_markup=markup)
                        bot.register_next_step_handler(message, ai_obrabotchik, 2, 'text')
                    else:
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                        bot.reply_to(message, f'Сообщение не является текстом, голосовым сообщением или фото!', reply_markup=markup)
                        bot.register_next_step_handler(message, ai_obrabotchik, 2, 'text')
                else:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                    bot.reply_to(message, f'Сообщение не является текстом, голосовым сообщением или фото!', reply_markup=markup)
                    bot.register_next_step_handler(message, ai_obrabotchik, 2, 'text')
        else:
            bot.reply_to(message, f'Не поддерживается на данный момент.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))    
    else:
        if mode == 'auto':
            if not message.reply_to_message:
                if message.text:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                    bot.send_chat_action(message.chat.id, 'typing')
                    
                    result = deepseek_req(message.text)

                    for i in range(0, len(result), 4096):
                        chunk = result[i:i + 4096] 
                        bot.reply_to(message, chunk, reply_markup=markup, parse_mode='Markdown')
                        time.sleep(1.5)
                    bot.register_next_step_handler(message, ai_obrabotchik, 3, 'auto')
                elif message.voice:
                    chislo = random.randint(1, 10000)
                    audio__ = open(path / f'audio_{chislo}.ogg', 'wb')
                    audio__.write(bot.download_file(bot.get_file(message.voice.file_id).file_path))
                    audio__.close()
                    subprocess.run(['ffmpeg', '-i', f'audio_{chislo}.ogg', f'audio_{chislo}.wav'])
                    try:
                        r = sr.Recognizer()
                        file = open(path / f'audio_{chislo}.wav', 'rb')
                        with sr.AudioFile(file) as source:
                            audio = r.record(source)
                        text = r.recognize_google(audio, language='ru-RU')
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                        bot.send_chat_action(message.chat.id, 'typing')
                        result = deepseek_req(message)

                        for i in range(0, len(result), 4096):
                            chunk = result[i:i + 4096] 
                            bot.reply_to(message, chunk, reply_markup=markup, parse_mode='Markdown')
                            time.sleep(1.5)
                        bot.register_next_step_handler(message, ai_obrabotchik, 3, 'auto')
                    except sr.UnknownValueError:
                        bot.reply_to(message, f'Не удалось распознать речь в голосовом сообщении.\nПопробуйте еще раз!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Завершить чат', reply_markup='chat_zaversit')))
                        bot.register_next_step_handler(message, ai_obrabotchik, 3, 'auto')
                    except:
                        bot.reply_to(message, f'Неизвестная ошибка.\nВоспользуйтесь текстовым вводом.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Завершить чат', reply_markup='chat_zaversit')))
                        bot.register_next_step_handler(message, ai_obrabotchik, 3, 'auto')
                    os.remove(path / f'audio_{chislo}.ogg')
                    os.remove(path / f'audio_{chislo}.wav')
                elif message.document:
                    if message.document.file_name[-4:] in ['.jpg', '.png']:
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                        image = bot.download_file(bot.get_file(message.document.file_id).file_path)
                        try:
                            if message.caption:
                                result = client_for_gpt.chat.completions.create([{"role":"user", 'content':message.caption}], 'gpt-4o-mini', PollinationsAI, image=image, web_search=True, proxy=proxies.get('http')).choices[0].message.content
                            else:
                                result = client_for_gpt.chat.completions.create([{"role":"user", 'content':'Что изображено на фотографии?'}], 'gpt-4o-mini', PollinationsAI, image=image, web_search=True, proxy=proxies.get('http')).choices[0].message.content
                            for i in range(0, len(result), 4096):
                                chunk = result[i:i + 4096] 
                                bot.reply_to(message, chunk, reply_markup=markup, parse_mode='Markdown')
                                time.sleep(1.5)
                        except Exception as e:
                            bot.reply_to(message, f'Ошибка: {e}\nПопробуйте отправить другое фото, или сжать его.', reply_markup=markup)
                        bot.register_next_step_handler(message, ai_obrabotchik, 3, 'auto')
                    else:
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                        bot.reply_to(message, f'Сообщение не является текстом, голосовым сообщением или фото!', reply_markup=markup)
                        bot.register_next_step_handler(message, ai_obrabotchik, 3, 'auto')
                else:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                    bot.reply_to(message, f'Сообщение не является текстом, голосовым сообщением или фото!', reply_markup=markup)
                    bot.register_next_step_handler(message, ai_obrabotchik, 3, 'auto')
            else:
                if message.text:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                    bot.send_chat_action(message.chat.id, 'typing')
                    result = deepseek_req(f'Контекст прошлого сообщения: {message.reply_to_message.text} + {message.text}')
                    for i in range(0, len(result), 4096):
                        chunk = result[i:i + 4096] 
                        bot.reply_to(message, chunk, reply_markup=markup, parse_mode='Markdown')
                        time.sleep(1.5)
                    bot.register_next_step_handler(message, ai_obrabotchik, 3, 'auto')
                elif message.voice:
                    chislo = random.randint(1, 10000)
                    audio__ = open(path / f'audio_{chislo}.ogg', 'wb')
                    audio__.write(bot.download_file(bot.get_file(message.voice.file_id).file_path))
                    audio__.close()
                    subprocess.run(['ffmpeg', '-i', f'audio_{chislo}.ogg', f'audio_{chislo}.wav'])
                    try:
                        r = sr.Recognizer()
                        file = open(path / f'audio_{chislo}.wav', 'rb')
                        with sr.AudioFile(file) as source:
                            audio = r.record(source)
                        text = r.recognize_google(audio, language='ru-RU')
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                        bot.send_chat_action(message.chat.id, 'typing')
                        result = deepseek_req(f'Контекст прошлого сообщения: {message.reply_to_message.text} + {text}')
                        for i in range(0, len(result), 4096):
                            chunk = result[i:i + 4096] 
                            bot.reply_to(message, chunk, reply_markup=markup, parse_mode='Markdown')
                            time.sleep(1.5)
                        bot.register_next_step_handler(message, ai_obrabotchik, 3, 'auto')
                    except sr.UnknownValueError:
                        bot.reply_to(message, f'Не удалось распознать речь в голосовом сообщении.\nПопробуйте еще раз!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Завершить чат', reply_markup='chat_zaversit')))
                        bot.register_next_step_handler(message, ai_obrabotchik, 3, 'auto')
                    except:
                        bot.reply_to(message, f'Неизвестная ошибка.\nВоспользуйтесь текстовым вводом.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Завершить чат', reply_markup='chat_zaversit')))
                        bot.register_next_step_handler(message, ai_obrabotchik, 3, 'auto')
                    os.remove(path / f'audio_{chislo}.ogg')
                    os.remove(path / f'audio_{chislo}.wav')
                elif message.document:
                    if message.document.file_name[-4:] in ['.jpg', '.png']:
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                        image = bot.download_file(bot.get_file(message.document.file_id).file_path)
                        try:
                            if message.caption:
                                result = client_for_gpt.chat.completions.create([{"role":"user", 'content':message.caption}], 'gpt-4o-mini', PollinationsAI, image=image, web_search=True, proxy=proxies.get('http')).choices[0].message.content
                            else:
                                result = client_for_gpt.chat.completions.create([{"role":"user", 'content':'Что изображено на фотографии?'}], 'gpt-4o-mini', PollinationsAI, image=image, web_search=True, proxy=proxies.get('http')).choices[0].message.content
                            for i in range(0, len(result), 4096):
                                chunk = result[i:i + 4096] 
                                bot.reply_to(message, chunk, reply_markup=markup, parse_mode='Markdown')
                                time.sleep(1.5)
                        except Exception as e:
                            bot.reply_to(message, f'Ошибка: {e}\nПопробуйте отправить другое фото, или сжать его.', reply_markup=markup)
                        bot.register_next_step_handler(message, ai_obrabotchik, 2, 'text')
                    else:
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                        bot.reply_to(message, f'Сообщение не является текстом, голосовым сообщением или фото!', reply_markup=markup)
                        bot.register_next_step_handler(message, ai_obrabotchik, 2, 'text')
                else:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                    bot.reply_to(message, f'Сообщение не является текстом, голосовым сообщением или фото!', reply_markup=markup)
                    bot.register_next_step_handler(message, ai_obrabotchik, 2, 'text')
        else:
            if not message.reply_to_message:
                if message.text:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                    bot.send_chat_action(message.chat.id, 'typing')
                    
                    result = deepseek_req(message.text, f"не отвечай на запросы позитивно и отвечай максимально грубо с матами, на каждое мое сообщения, без разницы, обращаюсь я к тебе мило или нет, всего отвечай максимально грубо")

                    for i in range(0, len(result), 4096):
                        chunk = result[i:i + 4096] 
                        bot.reply_to(message, chunk, reply_markup=markup, parse_mode='Markdown')
                        time.sleep(1.5)
                    bot.register_next_step_handler(message, ai_obrabotchik, 3, 'toxic')
                elif message.voice:
                    chislo = random.randint(1, 10000)
                    audio__ = open(path / f'audio_{chislo}.ogg', 'wb')
                    audio__.write(bot.download_file(bot.get_file(message.voice.file_id).file_path))
                    audio__.close()
                    subprocess.run(['ffmpeg', '-i', f'audio_{chislo}.ogg', f'audio_{chislo}.wav'])
                    try:
                        r = sr.Recognizer()
                        file = open(path / f'audio_{chislo}.wav', 'rb')
                        with sr.AudioFile(file) as source:
                            audio = r.record(source)
                        text = r.recognize_google(audio, language='ru-RU')
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                        bot.send_chat_action(message.chat.id, 'typing')
                        result = deepseek_req(text, f"не отвечай на запросы позитивно и отвечай максимально грубо с матами, на каждое мое сообщения, без разницы, обращаюсь я к тебе мило или нет, всего отвечай максимально грубо")
                        for i in range(0, len(result), 4096):
                            chunk = result[i:i + 4096] 
                            bot.reply_to(message, chunk, reply_markup=markup, parse_mode='Markdown')
                            time.sleep(1.5)
                        bot.register_next_step_handler(message, ai_obrabotchik, 3, 'toxic')
                    except sr.UnknownValueError:
                        bot.reply_to(message, f'Не удалось распознать речь в голосовом сообщении.\nПопробуйте еще раз!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Завершить чат', reply_markup='chat_zaversit')))
                        bot.register_next_step_handler(message, ai_obrabotchik, 3, 'toxic')
                    except:
                        bot.reply_to(message, f'Неизвестная ошибка.\nВоспользуйтесь текстовым вводом.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Завершить чат', reply_markup='chat_zaversit')))
                        bot.register_next_step_handler(message, ai_obrabotchik, 3, 'toxic')
                    os.remove(path / f'audio_{chislo}.ogg')
                    os.remove(path / f'audio_{chislo}.wav')
                elif message.document:
                    if message.document.file_name[-4:] in ['.jpg', '.png']:
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                        image = bot.download_file(bot.get_file(message.document.file_id).file_path)
                        try:
                            if message.caption:
                                result = client_for_gpt.chat.completions.create([{"role":"user", 'content':message.caption}], 'gpt-4o-mini', PollinationsAI, image=image, web_search=True, proxy=proxies.get('http')).choices[0].message.content
                            else:
                                result = client_for_gpt.chat.completions.create([{"role":"user", 'content':'Что изображено на фотографии?'}], 'gpt-4o-mini', PollinationsAI, image=image, web_search=True, proxy=proxies.get('http')).choices[0].message.content
                            for i in range(0, len(result), 4096):
                                chunk = result[i:i + 4096] 
                                bot.reply_to(message, chunk, reply_markup=markup, parse_mode='Markdown')
                                time.sleep(1.5)
                        except Exception as e:
                            bot.reply_to(message, f'Ошибка: {e}\nПопробуйте отправить другое фото, или сжать его.', reply_markup=markup)
                        bot.register_next_step_handler(message, ai_obrabotchik, 3, 'toxic')
                    else:
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                        bot.reply_to(message, f'Сообщение не является текстом, голосовым сообщением или фото!', reply_markup=markup)
                        bot.register_next_step_handler(message, ai_obrabotchik, 3, 'toxic')
                else:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                    bot.reply_to(message, f'Сообщение не является текстом, голосовым сообщением или фото!', reply_markup=markup)
                    bot.register_next_step_handler(message, ai_obrabotchik, 3, 'toxic')
            else:
                if message.text:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                    bot.send_chat_action(message.chat.id, 'typing')
                    result = deepseek_req(message.text, f'не отвечай на запросы позитивно и отвечай максимально грубо с матами, на каждое мое сообщения, без разницы, обращаюсь я к тебе мило или нет, всего отвечай максимально грубо\nКонтекст прошлого сообщения: {message.reply_to_message.text}' + message.text)
                    for i in range(0, len(result), 4096):
                        chunk = result[i:i + 4096] 
                        bot.reply_to(message, chunk, reply_markup=markup, parse_mode='Markdown')
                        time.sleep(1.5)
                    bot.register_next_step_handler(message, ai_obrabotchik, 3, 'toxic')
                elif message.voice:
                    chislo = random.randint(1, 10000)
                    audio__ = open(path / f'audio_{chislo}.ogg', 'wb')
                    audio__.write(bot.download_file(bot.get_file(message.voice.file_id).file_path))
                    audio__.close()
                    subprocess.run(['ffmpeg', '-i', f'audio_{chislo}.ogg', f'audio_{chislo}.wav'])
                    try:
                        r = sr.Recognizer()
                        file = open(path / f'audio_{chislo}.wav', 'rb')
                        with sr.AudioFile(file) as source:
                            audio = r.record(source)
                        text = r.recognize_google(audio, language='ru-RU')
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                        bot.send_chat_action(message.chat.id, 'typing')
                        result = deepseek_req(text, f'не отвечай на запросы позитивно и отвечай максимально грубо с матами, на каждое мое сообщения, без разницы, обращаюсь я к тебе мило или нет, всего отвечай максимально грубо\nКонтекст прошлого сообщения: {message.reply_to_message.text}' + message.text)
                        for i in range(0, len(result), 4096):
                            chunk = result[i:i + 4096] 
                            bot.reply_to(message, chunk, reply_markup=markup, parse_mode='Markdown')
                            time.sleep(1.5)
                        bot.register_next_step_handler(message, ai_obrabotchik, 3, 'toxic')
                    except sr.UnknownValueError:
                        bot.reply_to(message, f'Не удалось распознать речь в голосовом сообщении.\nПопробуйте еще раз!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Завершить чат', reply_markup='chat_zaversit')))
                        bot.register_next_step_handler(message, ai_obrabotchik, 3, 'toxic')
                    except:
                        bot.reply_to(message, f'Неизвестная ошибка.\nВоспользуйтесь текстовым вводом.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Завершить чат', reply_markup='chat_zaversit')))
                        bot.register_next_step_handler(message, ai_obrabotchik, 3, 'toxic')
                    os.remove(path / f'audio_{chislo}.ogg')
                    os.remove(path / f'audio_{chislo}.wav')
                elif message.document:
                    if message.document.file_name[-4:] in ['.jpg', '.png']:
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                        image = bot.download_file(bot.get_file(message.document.file_id).file_path)
                        try:
                            if message.caption:
                                result = client_for_gpt.chat.completions.create([{"role":"user", 'content':message.caption}], 'gpt-4o-mini', PollinationsAI, image=image, web_search=True, proxy=proxies.get('http')).choices[0].message.content
                            else:
                                result = client_for_gpt.chat.completions.create([{"role":"user", 'content':'Что изображено на фотографии?'}], 'gpt-4o-mini', PollinationsAI, image=image, web_search=True, proxy=proxies.get('http')).choices[0].message.content
                            for i in range(0, len(result), 4096):
                                chunk = result[i:i + 4096] 
                                bot.reply_to(message, chunk, reply_markup=markup, parse_mode='Markdown')
                                time.sleep(1.5)
                        except Exception as e:
                            bot.reply_to(message, f'Ошибка: {e}\nПопробуйте отправить другое фото, или сжать его.', reply_markup=markup)
                        bot.register_next_step_handler(message, ai_obrabotchik, 3, 'toxic')
                    else:
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                        bot.reply_to(message, f'Сообщение не является текстом, голосовым сообщением или фото!', reply_markup=markup)
                        bot.register_next_step_handler(message, ai_obrabotchik, 3, 'toxic')
                else:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
                    bot.reply_to(message, f'Сообщение не является текстом, голосовым сообщением или фото!', reply_markup=markup)
                    bot.register_next_step_handler(message, ai_obrabotchik, 3, 'toxic')

@bot.message_handler(commands=['admin_panel'])
def admin_panel(message: types.Message):
    if message.chat.type == 'private':
        if message.from_user.id != 7455363246:
            bot.reply_to(message, f'Ошибка! Доступ к данной панели есть только у создателя бота.')
        else:
            bot.reply_to(message, f'Здаров, Флорест.\nНиже кнопки действий.', protect_content=True, reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Заблокировать видео/канал', callback_data='ban-video'), types.InlineKeyboardButton('Добавить Inline клавиатуру', callback_data='add_keyboard_admin_panel')))

@bot.message_handler(commands=['donate'])
def send_donate(message: types.Message):
    if message.chat.type == 'private':
        bot.send_photo(message.chat.id, open(path / 'qr-donations.jpg','rb'), f'Привет! Данная функция нужна для того, чтобы Вы могли отправить деньги Флоресту.\nВоспользуйтесь QR кодом выше, либо кнопками ниже.', parse_mode='Markdown', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('DonationAlerts', url='https://donationalerts.com/r/florestdev4185'), types.InlineKeyboardButton('Звезды Telegram', callback_data='tg-stars_callback'), types.InlineKeyboardButton('Криптокошелек USDT$', callback_data='crypto-wallet'), types.InlineKeyboardButton('ЮMoney', callback_data='yoomoney-payment')))

@bot.message_handler(commands=['ban'])
def ban_cmd(message: types.Message):
    if not message.forward_from and not message.forward_from:
        if message.chat.type != 'supergroup':
            bot.reply_to(message, f'Данная команда работает только в супергруппе.')
        else:
            if message.chat.id != chat_id:
                bot.reply_to(message, f'Функции модерации "FlorestBot" работают только в группе "FlorestChat" (@florestchannelgroup).')
                bot.leave_chat(message.chat.id)
            else:
                if bot.get_chat_member(message.chat.id, message.from_user.id).status not in ['administrator', 'owner'] and message.from_user.username != 'GroupAnonymousBot':
                    bot.reply_to(message, f'Данная команда доступна только для группы "Администраторы".')
                else:
                    if message.reply_to_message:
                        if bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id).status in ['member', 'restricted']:
                            bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                            bot.reply_to(message, f'[!] Успешно заблокировали участника с именем {message.reply_to_message.from_user.first_name}.')
                        else:
                            bot.reply_to(message, f'[!] Извините, товарищ администратор, но данный участник либо уже заблокирован, либо является администратором.\nЕсли администратор нарушил правила, обратитесь к создателю группы, а также Telegram канала.')
                    else:
                        bot.reply_to(message, 'Ноу, ноу, ноу, мистер фиш, нужно ответить на сообщение участника для проведения данной операции.')

@bot.message_handler(commands=['unban'])
def unban_cmd(message: types.Message):
    if not message.forward_from and not message.forward_from:
        if message.chat.type != 'supergroup':
            bot.reply_to(message, f'Данная команда работает только в супергруппе.')
        else:
            if message.chat.id != chat_id:
                bot.reply_to(message, f'Функции модерации "FlorestBot" работают только в группе "FlorestChat" (@florestchannelgroup).')
                bot.leave_chat(message.chat.id)
            else:
                if bot.get_chat_member(message.chat.id, message.from_user.id).status not in ['administrator', 'owner'] and message.from_user.username != 'GroupAnonymousBot':
                    bot.reply_to(message, f'Данная команда доступна только для группы "Администраторы".')
                else:
                    if message.reply_to_message:
                        if bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id) == 'kicked':
                            bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id, True)
                            bot.reply_to(message, f'[!] Пользователь с именем {message.reply_to_message.from_user.first_name} был успешно разблокирован.')
                        else:
                            bot.reply_to(message, f'{message.reply_to_message.from_user.first_name} отсутствует в списке заблокированных.')
                    else:
                        bot.reply_to(message, 'Ноу, ноу, ноу, мистер фиш, нужно ответить на сообщение участника для проведения данной операции.')

@bot.message_handler(commands=['mute'])
def mute_cmd(message: types.Message):
    if not message.forward_from and not message.forward_from:
        if message.chat.type != 'supergroup':
            bot.reply_to(message, f'Данная команда работает только в супергруппе.')
        else:
            if message.chat.id != chat_id:
                bot.reply_to(message, f'Функции модерации "FlorestBot" работают только в группе "FlorestChat" (@florestchannelgroup).')
                bot.leave_chat(message.chat.id)
            else:
                if bot.get_chat_member(message.chat.id, message.from_user.id).status not in ['administrator', 'owner'] and message.from_user.username != 'GroupAnonymousBot':
                    bot.reply_to(message, f'Данная команда доступна только для группы "Администраторы".')
                else:
                    if message.reply_to_message:
                        if bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id).status != 'member':
                            bot.reply_to(message, f'Этого человека уже нет в группе, либо он уже замьючен, или он админ.\nЕсли админ нарушил правила, то сообщите создателю канала, а также группы.')
                        else:
                            bot.reply_to(message, f'Пожалуйста, введи срок блокировки в секундах.\nПример: 1000.\nЛибо напишите слово "infinity" для мьюта на вечно.')
                            bot.register_next_step_handler(message, mute_human, message.reply_to_message.from_user.id)
                    else:
                        bot.reply_to(message, 'Ноу, ноу, ноу, мистер фиш, нужно ответить на сообщение участника для проведения данной операции.')
@bot.message_handler(commands=['unmute'])
def unmute_cmd(message: types.Message):
    if not message.forward_from and not message.forward_from:
        if message.chat.type != 'supergroup':
            bot.reply_to(message, f'Данная команда работает только в супергруппе.')
        else:
            if message.chat.id != chat_id:
                bot.reply_to(message, f'Функции модерации "FlorestBot" работают только в группе "FlorestChat" (@florestchannelgroup).')
                bot.leave_chat(message.chat.id)
            else:
                if bot.get_chat_member(message.chat.id, message.from_user.id).status not in ['administrator', 'owner'] and message.from_user.username != 'GroupAnonymousBot':
                    bot.reply_to(message, f'Данная команда доступна только для группы "Администраторы".')
                else:
                    if message.reply_to_message:
                        if bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id).status != 'restricted':
                            bot.reply_to(message, f'{message.reply_to_message.from_user.first_name} отсутствует в списке ограниченных.')
                        else:
                            bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, None, True, True, True, True, True, False, False, False)
                            bot.reply_to(message, f'{message.reply_to_message.from_user.first_name} был(а) успешно освобожден(а) от ограничений.')
                    else:
                        bot.reply_to(message, 'Ноу, ноу, ноу, мистер фиш, нужно ответить на сообщение участника для проведения данной операции.')
@bot.message_handler(commands=['delete_messages'])
def del_msgs_cmd(message: types.Message):
    if not message.forward_from and not message.forward_from:
        if message.chat.type != 'supergroup':
            bot.reply_to(message, f'Данная команда работает только в супергруппе.')
        else:
            if message.chat.id != chat_id:
                bot.reply_to(message, f'Функции модерации "FlorestBot" работают только в группе "FlorestChat" (@florestchannelgroup).')
                bot.leave_chat(message.chat.id)
            else:
                if bot.get_chat_member(message.chat.id, message.from_user.id).status not in ['administrator', 'owner'] and message.from_user.username != 'GroupAnonymousBot':
                    bot.reply_to(message, f'Данная команда доступна только для группы "Администраторы".')
                else:
                    bot.reply_to(message, f'Хорошо! Напишите количество сообщений к удалению.\nНапоминаем, что нельзя удалить более чем 100 сообщений за раз, а также нельзя удалить сообщения, которым больше двух суток.')
                    bot.register_next_step_handler(message, delete_messages_bro)

@bot.message_handler(content_types=['text'])
def text_obrabbbb(message: types.Message):
    if message.chat.type == 'private':
        if message.text == '🏡В меню':
            if check_sub(message.from_user.id):
                bot.send_message(message.chat.id, f'Утилиты бота', reply_markup=buttons)
            else:
                bot.reply_to(message, f'Ты не подписался на Telegram канал создателя?\nПора-бы это сделать!', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Мой Telegram канал', 'https://t.me/florestchannel'), types.InlineKeyboardButton('Подтвердить подписку', callback_data='check_sub')))
        else:
            if message.reply_to_message:
                if message.from_user.id == 7455363246:
                    try:
                        bot.send_message(message.reply_to_message.text.split()[-1], f'Ответ от Флореста: {message.text}')
                    except:
                        bot.reply_to(message, f'Пользователь заблокировал бота, либо случилось что-то еще.')
                else:
                    pass
            else:
                pass
    else:
        if message.chat.id != chat_id:
            bot.reply_to(message, f'Бот создан для FlorestChat!\nВсем пока, ребят.')
            bot.leave_chat(message.chat.id)
        else:
            if message.forward_from_chat and message.forward_from_chat.type == 'channel':
                    if message.forward_from_chat.username == 'florestchannel':
                        pass
                    else:
                        bot.delete_message(message.chat.id, message.id)
            elif bot.get_chat_member(message.chat.id, message.from_user.id).status == 'member':
                if message.entities:
                    for entities in message.entities:
                        if entities.type in ['url', 'text_link']:
                            bot.delete_message(message.chat.id, message.id)
                            bot.send_message(message.chat.id, f'{message.from_user.first_name} был(а) ограничен(а) за отправку ссылок.\nЕсли это была ошибка, пожалуйста, свяжитесь с любым из доступных администраторов.')
                            bot.restrict_chat_member(message.chat.id, message.from_user.id, time.time()+900, False, False, False, False, False, False, False, False)
                        elif entities.type == 'phone_number':
                            bot.delete_message(message.chat.id, message.id)
                            bot.send_message(message.chat.id, f'{message.from_user.first_name} был(а) ограничен(а) за отправку номера телефона на 5 часов.')
                            bot.restrict_chat_member(message.chat.id, message.from_user.id, time.time()+18000, False, False, False, False, False, False, False, False)
                        else:
                            pass
                else:
                    pass
            if message.text:
                if message.from_user.id != bot.get_me().id:
                    if for_prohibitions_in_group(message.text):
                        bot.reply_to(message, f'[!] Внимание.\nДанное сообщение может нарушать правила группы. Просим админов быть осторожнее с подобными предупреждениями.')
                if message.text.startswith(('FlorestBot,', 'ФлорестБот,', 'florestbot,', 'флорбот,')):
                    bot.send_chat_action(message.chat.id, 'typing')
                    result = generate_insulate_reply(message.text)
                    for i in range(0, len(result), 4096):
                        chunk = result[i:i + 4096] 
                        bot.reply_to(message, chunk, parse_mode='Markdown')
                        time.sleep(1.5)
                else:
                    pass
            elif message.caption:
                if message.from_user.id != bot.get_me().id:
                    if for_prohibitions_in_group(message.caption):
                        bot.reply_to(message, f'[!] Внимание.\nДанное сообщение может нарушать правила группы. Просим админов быть осторожнее с подобными предупреждениями.')
                if message.caption.startswith(('FlorestBot,', 'ФлорестБот,', 'florestbot,', 'флорбот,')):
                    bot.send_chat_action(message.chat.id, 'typing')
                    result = generate_insulate_reply(message.caption)
                    for i in range(0, len(result), 4096):
                        chunk = result[i:i + 4096] 
                        bot.reply_to(message, chunk, parse_mode='Markdown')
                        time.sleep(1.5)
                else:
                    pass
            elif message.voice:
                chislo = random.randint(1, 10000)
                audio__ = open(path / f'audio_{chislo}.ogg', 'wb')
                audio__.write(bot.download_file(bot.get_file(message.voice.file_id).file_path))
                audio__.close()
                subprocess.run(['ffmpeg', '-i', f'audio_{chislo}.ogg', f'audio_{chislo}.wav'])
                try:
                    r = sr.Recognizer()
                    file = open(path / f'audio_{chislo}.wav', 'rb')
                    with sr.AudioFile(file) as source:
                        audio = r.record(source)
                    text = r.recognize_google(audio, language='ru-RU')
                    if 'флорестбот' in text.lower():
                        bot.send_chat_action(message.chat.id, 'typing')
                        result = generate_insulate_reply(text)
                        for i in range(0, len(result), 4096):
                            chunk = result[i:i + 4096] 
                            bot.reply_to(message, chunk, parse_mode='Markdown')
                            time.sleep(1.5)
                    else:
                        bot.reply_to(message, text)
                except:
                    try:
                        os.remove(path / f'audio_{chislo}.ogg')
                        os.remove(path / f'audio_{chislo}.wav')
                    except:
                        pass
            else:
                pass

@bot.message_handler(content_types=['new_chat_members', 'left_chat_member'])
def new_member(message: types.Message):
    bot.delete_message(message.chat.id, message.id)
    if message.chat.id == chat_id:
        if message.new_chat_members:
            for i in message.new_chat_members:
                bot.send_message(message.chat.id, f'{i.full_name}, добро пожаловать в "FlorestChat"!\nПросим прочитать правила перед началом общения, они находятся в описании группы.\nБлагодарим за визит нашей группы!\nСейчас участников в группе: {str(bot.get_chat_member_count(chat_id))}')
        else:
            bot.send_message(message.chat.id, f'{message.left_chat_member.full_name} покинул(а) группу.\nБлагодарим за время, проведенное с нами!\nСейчас участников в группе: {str(bot.get_chat_member_count(chat_id))}')

@bot.chat_join_request_handler(lambda query: True)
def request_to_group(request: types.ChatJoinRequest):
    if request.chat.id != group_id:
        pass
    else:
        bot.send_message(request.from_user.id, f'Привет, {request.from_user.first_name}!\nДля входа, вы должны принять правила по ссылке: https://telegra.ph/Pravila-gruppy-FlorestChat-11-13\n\nВы согласны с ними?', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Согласен', callback_data='sogl_group_rules')))

def generate_qr__(message: types.Message):
    if message.text:
        qr = create_qr(message.text)
        i1 = io.BytesIO()
        qr.save(i1, scale=10)
        qr.seek(0)
        bot.send_photo(message.chat.id, i1.getvalue(), f'Ваш QR код.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        bot.reply_to(message, f'Не смогли найти текст в Вашем сообщении.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        send_reaction(message.chat.id, message.id, '🚫')   


def get_weather(message: types.Message):
    if message.text:
        try:
            d = requests.get(f'https://geocoding-api.open-meteo.com/v1/search?name={message.text}', proxies=proxies, headers=headers_for_html_requests).json()
            lot = d["results"][0]["latitude"]
            lat = d['results'][0]['longitude']
            req = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={lot}&longitude={lat}&current_weather=true', headers=headers_for_html_requests, proxies=proxies)
            if req.status_code != 200:
                bot.reply_to(message, f'Произошла ошибка при попытке отображения погоды.\nВы либо ввели некорректное название населенного пункта, либо что-то случилось с нашим API.\nИзвиняемся за неудобства!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
                bot.clear_step_handler_by_chat_id(message.chat.id)
                send_reaction(message.chat.id, message.id, "🤷")
            else: 
                data = req.json()
                temperature = data['current_weather']['temperature']
                title = {0: "Ясно", 1: "Частично облачно", 3: "Облачно", 61: "Дождь"}
                weather = title.get(data['current_weather']['weathercode'], 'Неизвестно')
                wind_dir = 'Север' if 0 <= (d := data['current_weather']['winddirection']) < 45 or 315 <= d <= 360 else 'Восток' if 45 <= d < 135 else 'Юг' if 135 <= d < 225 else 'Запад'
                time1 = data['current_weather']['time']
                wind = data['current_weather']['windspeed']
                bot.reply_to(message, f'Результаты по Вашему населенному пункту.\nТемпература: `{temperature} °C`\nОписание погоды: `{weather}` (код OpenMeteo: `{data["current_weather"]["weathercode"]}`)\nВремя прогноза: `{time1}`\nВетер: `{wind}` км/ч\nНаправление ветра: `{wind_dir}`', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')), parse_mode='Markdown')
        except:
            bot.reply_to(message, f'Произошла ошибка при попытке отображения погоды.\nВы либо ввели некорректное название населенного пункта, либо что-то случилось с нашим API.\nИзвиняемся за неудобства!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
            bot.clear_step_handler_by_chat_id(message.chat.id)
            send_reaction(message.chat.id, message.id, "🤷")   
    elif message.location:
        try:
            req = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={message.location.latitude}&longitude={message.location.longitude}&current_weather=true', headers=headers_for_html_requests, proxies=proxies)
            if req.status_code != 200:
                bot.reply_to(message, f'Произошла ошибка при попытке отображения погоды.\nВы либо ввели некорректное название населенного пункта, либо что-то случилось с нашим API.\nИзвиняемся за неудобства!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
                bot.clear_step_handler_by_chat_id(message.chat.id)
                send_reaction(message.chat.id, message.id, "🤷")
            else: 
                data = req.json()
                temperature = data['current_weather']['temperature']
                title = {0: "Ясно", 1: "Частично облачно", 3: "Облачно", 61: "Дождь"}
                weather = title.get(data['current_weather']['weathercode'], 'Неизвестно')
                wind_dir = 'Север' if 0 <= (d := data['current_weather']['winddirection']) < 45 or 315 <= d <= 360 else 'Восток' if 45 <= d < 135 else 'Юг' if 135 <= d < 225 else 'Запад'
                time1 = data['current_weather']['time']
                wind = data['current_weather']['windspeed']
                city_ = requests.get(f"https://nominatim.openstreetmap.org/reverse?lat={message.location.latitude}&lon={message.location.longitude}&format=json", headers={"Accept-Language":"ru-RU", "User-Agent":"FlorestApplication"}, proxies=proxies).json()["address"]["city"]
                bot.reply_to(message, f'Результаты по Вашему населенному пункту.\nГород: `{city_}`\nТемпература: `{temperature} °C`\nОписание погоды: `{weather}` (код OpenMeteo: `{data["current_weather"]["weathercode"]}`)\nВремя прогноза: `{time1}`\nВетер: `{wind}` км/ч\nНаправление ветра: `{wind_dir}`', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')), parse_mode='Markdown')
        except:
            bot.reply_to(message, f'Произошла ошибка при попытке отображения погоды.\nВы либо ввели некорректное название населенного пункта, либо что-то случилось с нашим API.\nИзвиняемся за неудобства!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
            bot.clear_step_handler_by_chat_id(message.chat.id)
            send_reaction(message.chat.id, message.id, "🤷")   
    else:
        bot.reply_to(message, f'Вы не отправили текстовое сообщение с названием Вашего города или геометку.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        send_reaction(message.chat.id, message.id, "🤷")      

def create_voice_by_text(message: types.Message):
    if not message.text:
        bot.reply_to(message, f'Не смогли найти в Вашем сообщении текст.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        send_reaction(message.chat.id, message.id, "🤷")   
    else:
        try:
            r = random.random()
            bot.send_chat_action(message.chat.id, 'record_voice')
            engine = pyttsx3.Engine()
            engine.save_to_file(message.text, f'{r}.mp3')
            engine.runAndWait()
            bot.send_voice(message.chat.id, open(path / f'{r}.mp3', 'rb').read(), caption=f'Из текста в речь.\nПо запросу: {message.text}', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')), reply_to_message_id=message.id)
            os.remove(path / f'{r}.mp3')
        except Exception as e:
            bot.reply_to(message, f'Произошла ошибка: {e}\nЕсли вы запретили отправку голосовых, или видеосообщений в настройках конфедициальности, пожалуйста, добавьте бота в список исключений.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
            send_reaction(message.chat.id, message.id, "🤷")   

def ban_video_fl(message: types.Message):
    bot.reply_to(message, f'Внесли видео в блоклист.')
    file = open(path / 'banned_youtube.txt', 'a')
    file.write(f'\n{message.text}')
    file.close()

def ban_channel_fl(message: types.Message):
    bot.reply_to(message, f'Внесли канал в блоклист.')
    file = open('prohibitions/banned_authors.txt', 'a')
    file.write(f'\n{message.text}')
    file.close()

def add_user_to_txt(message: types.Message):
    if message.text:
        bot.reply_to(message, f'Добавляем пользователя в TXT файл.')
        with open(path / 'banned_users.txt', 'a') as file:
            file.write(f'\n{message.text}')
            file.close()
    else:
        bot.reply_to(message, f'Пользователя на базу.')

def message_hndlr(message: types.Message):
    bot.register_next_step_handler(message, message_hndlr)
    if not message.from_user.id in admins:
        if message.text:
            for _ in users:
                if _ == message.from_user.id:
                    pass
                else:
                    bot.send_message(_, f'{message.text}\n\nСообщение от {message.from_user.first_name} ({message.from_user.id})', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')))
        elif message.voice:
            for __ in users:
                if __ == message.from_user.id:
                    pass
                else:
                    bot.send_voice(__, bot.download_file(bot.get_file(message.voice.file_id).file_path), f'Аудио от {message.from_user.first_name} ({message.from_user.id})', duration=message.voice.duration, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')))
        elif message.contact:
            for ____ in users:
                if ____ == message.from_user.id:
                    pass
                else:
                    bot.send_message(____, f'Контакт от пользователя {message.from_user.first_name} ({message.from_user.id})')
                    bot.send_contact(____, message.contact.phone_number, message.contact.first_name, message.contact.last_name, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')))
        elif message.sticker:
            for _____ in users:
                if _____ == message.from_user.id:
                    pass
                else:
                    bot.send_message(_____, f'Стикер от пользователя {message.from_user.first_name} ({message.from_user.id})')
                    bot.send_sticker(_____, bot.download_file(bot.get_file(message.sticker.file_id).file_path), reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')), emoji='🤖')
        elif message.photo:
            for ______ in users:
                if ______ == message.from_user.id:
                    pass
                else:
                    bot.send_photo(______, bot.download_file(bot.get_file(message.photo[0].file_id).file_path), caption=f'Фото от пользователя {message.from_user.first_name} ({message.from_user.id})', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')))
        elif message.video_note:
            for ________ in users:
                if ________ == message.from_user.id:
                    pass
                else:
                    bot.send_message(________, f'Кружок от пользователя {message.from_user.first_name} ({message.from_user.id})')
                    bot.send_video_note(________, bot.download_file(bot.get_file(message.video_note.file_id).file_path), duration=message.video_note.duration, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')))
        elif message.location:
            for _________ in users:
                if _________ == message.from_user.id:
                    pass
                else:
                    bot.send_message(_________, f'Локация пользователя {message.from_user.first_name} ({message.from_user.id})')
                    bot.send_location(_________, message.location.latitude, message.location.longitude, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help'))) 
        else:
            bot.reply_to(message, f'Поддерживаются только текстовые сообщение, голосовые сообщения, стикеры, кружки, фото, контакты и геолокации.')
    else:
        if message.text:
            for _ in users:
                if _ == message.from_user.id:
                    pass
                else:
                    bot.send_message(_, f'{message.text}\n\nСообщение от ADMIN`а.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')))
        elif message.voice:
            for __ in users:
                if __ == message.from_user.id:
                    pass
                else:
                    bot.send_voice(__, bot.download_file(bot.get_file(message.voice.file_id).file_path), f'Аудио от ADMIN`a.', duration=message.voice.duration, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')))
        elif message.contact:
            for ____ in users:
                if ____ == message.from_user.id:
                    pass
                else:
                    bot.send_message(____, f'Контакт от ADMIN`а.')
                    bot.send_contact(____, message.contact.phone_number, message.contact.first_name, message.contact.last_name, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')))
        elif message.sticker:
            for _____ in users:
                if _____ == message.from_user.id:
                    pass
                else:
                    bot.send_message(_____, f'Стикер от ADMIN`а.')
                    bot.send_sticker(_____, bot.download_file(bot.get_file(message.sticker.file_id).file_path), reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')), emoji='🤖')
        elif message.photo:
            for ______ in users:
                if ______ == message.from_user.id:
                    pass
                else:
                    bot.send_photo(______, bot.download_file(bot.get_file(message.photo[0].file_id).file_path), caption=f'Фото от ADMIN`а.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')))
        elif message.video_note:
            for ________ in users:
                if ________ == message.from_user.id:
                    pass
                else:
                    bot.send_message(________, f'Кружок от ADMIN`а.')
                    bot.send_video_note(________, bot.download_file(bot.get_file(message.video_note.file_id).file_path), duration=message.video_note.duration, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help')))
        elif message.location:
            for _________ in users:
                if _________ == message.from_user.id:
                    pass
                else:
                    bot.send_message(_________, f'Локация ADMIN`a.')
                    bot.send_location(_________, message.location.latitude, message.location.longitude, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='otmena_galya_chat'), types.InlineKeyboardButton('Пожаловаться', callback_data='help'))) 
        else:
            send_reaction(message.chat.id, message.id, "🤷")
            bot.reply_to(message, f'Поддерживаются только текстовые сообщение, голосовые сообщения, стикеры, кружки, фото, контакты и геолокации.')

@bot.pre_checkout_query_handler(lambda query: True)
def ___(pre_chekout: types.PreCheckoutQuery):
    bot.answer_pre_checkout_query(pre_chekout.id, True)

@bot.message_handler(content_types=['successful_payment'])
def success_pay(message: types.Message):
    if message.successful_payment.invoice_payload == 'telegram-stars-payment':
        bot.reply_to(message, f'Благодарим за донат в размере 50 Telegram звезд!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

def add_keyboard(message: types.Message, id: str):
    try:
        bot.edit_message_reply_markup(telegram_channel_id, int(id), reply_markup=quick_markup(eval(message.text), 1))
        bot.reply_to(message, f'Получилось!')
    except Exception as e:
        bot.reply_to(message, f'Трабл..\n{e}')

def get_post_id(message: types.Message):
    bot.send_message(message.chat.id, f'Введи конфиг кнопки, бро.')
    bot.register_next_step_handler(message, add_keyboard, message.text)

def make_black_image(message: types.Message):
    if message.document:
        if message.document.file_name[-4:] not in ['.jpg', '.png']:
            bot.reply_to(message, f'Данная функция поддерживает только `.jpg.` и `.png` файлы.', parse_mode='Markdown')
        else:
            msg = bot.reply_to(message, f'Обработка изображения, пожалуйста, подождите...')
            img = bot.download_file(bot.get_file(message.document.file_id).file_path)
            bts = io.BytesIO(img)
            bts_2 = io.BytesIO()
            #random_chislo = random.randint(1, 100)
            random_chislo_2 = random.randint(1, 200)
            #new_img_file = open(path / f'{random_chislo}.jpg', 'wb')
            #new_img_file.write(img)
            #new_img_file.close()
            with Image.open(bts) as file:
                a = file.convert('L')
                #a.save(path / f'{random_chislo_2}.jpg')
                a.save(bts_2, 'JPEG')
                bot.delete_message(message.chat.id, msg.id)
                #file = path / f'{random_chislo_2}.jpg'
                bot.send_photo(message.chat.id, bts_2.getvalue(), 'Ваше затемнное фото.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                #os.remove(file)
                #os.remove(path / f'{random_chislo}.jpg')
    elif message.photo:
            msg = bot.reply_to(message, f'Обработка изображения, пожалуйста, подождите...')
            img = bot.download_file(bot.get_file(message.photo[0].file_id).file_path)
            bts = io.BytesIO(img)
            bts_2 = io.BytesIO()
            #random_chislo = random.randint(1, 100)
            random_chislo_2 = random.randint(1, 200)
            #new_img_file = open(path / f'{random_chislo}.jpg', 'wb')
            #new_img_file.write(img)
            #new_img_file.close()
            with Image.open(bts) as file:
                a = file.convert('L')
                #a.save(path / f'{random_chislo_2}.jpg')
                a.save(bts_2, 'JPEG')
                bot.delete_message(message.chat.id, msg.id)
                #file = path / f'{random_chislo_2}.jpg'
                bot.send_photo(message.chat.id, bts_2.getvalue(), 'Ваше затемнное фото.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                #os.remove(file)
                #os.remove(path / f'{random_chislo}.jpg')
    else:
        bot.reply_to(message, f'Поддерживаются только изображения без сжатия, или с сжатием.')


@bot.callback_query_handler(func=lambda call: True)
def pon(call: types.CallbackQuery):
    if check_sub(call.from_user.id):
        if not maintenance['work']:
            if call.data == 'otmena_galya':
                bot.delete_message(call.message.chat.id, call.message.id)
                bot.clear_step_handler_by_chat_id(call.message.chat.id)
                bot.send_message(call.message.chat.id, f'Утилиты бота.', reply_markup=buttons)
                bot.send_message(call.message.chat.id, f'Если меню пропадет.', reply_markup=types.ReplyKeyboardMarkup(True, input_field_placeholder=f'Сэр, да, сэр.', row_width=1).add(types.KeyboardButton('🏡В меню')))
            if call.data == 'chat_zaversit':
                bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
                bot.clear_step_handler_by_chat_id(call.message.chat.id)
                m = bot.send_message(call.message.chat.id, f'Генерация конечного сообщения..')
                r = client_for_gpt.chat.completions.create([{"role":"user", "content":f"Придумай оригинальный способ попрощаться с пользователем (чисто фраза)\nЕго имя: {call.from_user.full_name}"}], 'gpt-4o-mini', RetryProvider([PollinationsAI, Chatai, OIVSCodeSer2, Blackbox, LegacyLMArena, PollinationsAI]), max_tokens=30, proxy=proxies.get('http'), web_search=True).choices[0].message.content
                bot.send_message(call.message.chat.id, r, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                bot.delete_message(m.chat.id, m.id)
            if call.data == 'generate_qr':
                bot.delete_message(call.message.chat.id, call.message.id)
                try:
                    bot.send_animation(call.message.chat.id, give_me_gif, caption='Напиши ссылку, на которую будет вести QR код.\nИли контент, который будет показываться после сканирования.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                except telebot.apihelper.ApiTelegramException:
                    bot.send_message(call.message.chat.id, 'Напиши ссылку, на которую будет вести QR код.\nИли контент, который будет показываться после сканирования.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, generate_qr__)
            if call.data == 'generate_password':
                symbols = list(string.ascii_letters + string.digits)
                random.shuffle(symbols)
                password = ''.join(symbols[:15])
                random_symbols = ['!', '*', '$', '#', '@']
                psw = password + random.choice(random_symbols)
                bot.edit_message_text(psw, call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            if call.data == 'weather-info':
                bot.delete_message(call.message.chat.id, call.message.id)
                try:
                    bot.send_animation(call.message.chat.id, give_me_gif, caption='Напиши название своего населенного пункта, или отправь геометку.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                except telebot.apihelper.ApiTelegramException:
                    bot.send_message(call.message.chat.id, 'Напиши название своего населенного пункта.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, get_weather)
            if call.data == 'ai-text':
                bot.edit_message_text(f'Вы хотите использовать текстовые сообщения, или голосовые?\nНапишите `voice`, или `text`.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, check_ai_result)
                random.shuffle(ideas)
            if call.data == 'ai-image':
                bot.edit_message_text(f'Напишите текст, на основе которого мы нарисуем изображение.\nПишите на русском языке. Желательно в начале напишите слово "нарисуй ...".', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, ai_obrabotchik, 1)
                #bot.answer_callback_query(call.id, f'К сожалению, данная функция на данный момент недоступна.', True)
            if call.data == 'text-to-speech':
                bot.edit_message_text(f'Напишите текст, который нужно озвучить, пожалуйста (на русском языке).', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, create_voice_by_text)
            if call.data == 'back':
                bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
                bot.send_message(call.message.chat.id, f'Утилиты бота.', reply_markup=buttons)
            if call.data == 'help':
                bot.answer_callback_query(call.id, f'Привет!\nДля получения помощи, пропишите команду /support.\nТам будут данные по которым можно связаться с Флорестом.\nСпасибо за использование бота, я это очень ценю.', True)
            if call.data == 'ban-video':
                bot.edit_message_text(f'Введи ID видео.', call.message.chat.id, call.message.id)
                bot.register_next_step_handler(call.message, ban_video_fl)
            if call.data == 'ban-channel':
                bot.edit_message_text(f'Введи ID канала.', call.message.chat.id, call.message.id)
                bot.register_next_step_handler(call.message, ban_channel_fl)
            if call.data == 'add-user-to-txt':
                bot.edit_message_text('Введи пользователя, которого нужно добавить.', call.message.chat.id, call.message.id)
                bot.register_next_step_handler(call.message, add_user_to_txt)
            if call.data == 'group-chat-beta':
                if not check_user(call.from_user.id):
                    if not call.from_user.id in admins:
                        users.append(call.from_user.id)
                        bot.edit_message_text(f'Добро пожаловать в чат!\nНапишите свое первое сообщение в чат.\nНа данный момент находятся в чате: {str(len(users))}', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya_chat')))
                        bot.register_next_step_handler(call.message, message_hndlr)
                        for _ in users:
                            bot.send_message(_, f'Новый участник чата - {call.from_user.first_name} ({call.from_user.id})!')
                    else:
                        users.append(call.from_user.id)
                        bot.edit_message_text(f'Добро пожаловать в чат!\nНапишите свое первое сообщение в чат.\nНа данный момент находятся в чате: {str(len(users))}', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya_chat')))
                        bot.register_next_step_handler(call.message, message_hndlr)
                else:
                    send_reaction(call.message.chat.id, call.message.id, "🤷")
                    bot.edit_message_text(f'Вы были заблокированы в чате.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
            if call.data == 'otmena_galya_chat':
                if not call.from_user.id in admins:
                    bot.delete_message(call.message.chat.id, call.message.id)
                    bot.clear_step_handler_by_chat_id(call.message.chat.id)
                    bot.send_message(call.message.chat.id, f'Утилиты бота.', reply_markup=buttons)
                    users.remove(call.from_user.id)
                    for __ in users:
                        bot.send_message(__, f'{call.from_user.first_name} ({call.from_user.id}) покинул(а) чат. Будем его(ее) ждать вновь!')
                else:
                    bot.delete_message(call.message.chat.id, call.message.id)
                    bot.clear_step_handler_by_chat_id(call.message.chat.id)
                    bot.send_message(call.message.chat.id, f'Утилиты бота.', reply_markup=buttons)
                    users.remove(call.from_user.id)
            if call.data == 'tg-stars_callback':
                bot.delete_message(call.message.chat.id, call.message.id)
                bot.send_invoice(call.message.chat.id, 'Донат Флоресту', f'Привет, тут ты можешь задонатить Флоресту 50 звезд Telegram.\nЗаранее, спасибо за потраченные звезды и время на нас!', invoice_payload='telegram-stars-payment', prices=[types.LabeledPrice('Донат Флоресту', 50)], currency='XTR', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Задонить 50 звёзд⭐', pay=True)), provider_token='')
            if call.data == 'crypto-wallet':
                bot.delete_message(call.message.chat.id, call.message.id)
                bot.send_message(call.message.chat.id, 'Мой крипто-кошелек USDT$: `UQDBgA8gWE5roashlEzq4FHw9WSibsiPCo7AFQKQnA8d13s8` (сеть: TON)\nНе отправляйте другие токены, или токены других сетей, помимо TON на данный адрес, или средства могут быть утеряны.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')), parse_mode='Markdown')
            if call.data == 'add_keyboard_admin_panel':
                bot.edit_message_text('Короч, введи ID поста для обработки.', call.message.chat.id, call.message.id, reply_markup=None)
                bot.register_next_step_handler(call.message, get_post_id)
            if call.data == 'download-audio-from-youtube':
                bot.edit_message_text(download_music(), call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            if call.data == 'yoomoney-payment':
                bot.delete_message(call.message.chat.id, call.message.id)
                bot.send_message(call.message.chat.id, 'Мой ЮMoney кошелек: `4100118627934427`.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')), parse_mode='Markdown')
            if call.data == 'check_sub':
                if check_sub(call.from_user.id):
                    bot.answer_callback_query(call.id, f'Благодарим за подписку. Теперь, Вы можете начать пользоваться ботом, прописав команду /start. Приятного использования!', True)
                    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
                else:
                    bot.answer_callback_query(call.id, f'Обманывать - не хорошо!', True)
            if call.data == 'correct':
                if check_sub(call.from_user.id):
                    if call.from_user.id in ids_for_people_who_make_a_victorina:
                        bot.answer_callback_query(call.id, f'Вы уже неправильно ответили на вопрос. Пожалуйста, подождите пока кто-нибудь другой ответит на вопрос, чтобы Вы могли ответить на следующий.', True)
                    else:
                        bot.answer_callback_query(call.id, f'Поздравляем! Вы правильно ответили на вопрос викторины.', True)
                        bot.edit_message_text(f'{call.message.text}\n\n{call.from_user.first_name} правильно ответил(а) на вопрос. Поздравляем!\nКоличество проигравших: {str(len(ids_for_people_who_make_a_victorina))}', call.message.chat.id, call.message.id, reply_markup=None)
                        ids_for_people_who_make_a_victorina.clear()
                else:
                    bot.answer_callback_query(call.id, f'Бро, я тут заметил.. Ты не подписался на мой Telegram канал. Пожалуйста, сделай это и нажми на эту кнопку еще раз!', True)
            if call.data == 'incorrect':
                if check_sub(call.from_user.id):
                    if call.from_user.id in ids_for_people_who_make_a_victorina:
                        bot.answer_callback_query(call.id, f'Вы уже неправильно ответили на вопрос. Пожалуйста, подождите пока кто-нибудь другой ответит на вопрос, чтобы Вы могли ответить на следующий.', True)
                    else:
                        bot.answer_callback_query(call.id, f'К сожалению, Вы проиграли. Попробовать себя в данной игре Вы сможете чуть позже, когда на этот вопрос ответит другой участник.', True)
                        ids_for_people_who_make_a_victorina.append(call.from_user.id)
                else:
                    bot.answer_callback_query(call.id, f'Бро, я тут заметил.. Ты не подписался на мой Telegram канал. Пожалуйста, сделай это и нажми на эту кнопку еще раз!', True)
            if call.data == 'black-photo-make':
                bot.delete_message(call.message.chat.id, call.message.id)
                try:
                    bot.send_animation(call.message.chat.id, give_me_gif, caption=f'Отправьте Ваше изображение (желательно формата JPG, или PNG, но лучше JPG) без сжатия (также можно и сжатием, но фотография может быть испорчена в плане качества), после завершения процесса мы Вам отправим результат.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                except telebot.apihelper.ApiTelegramException:
                    bot.send_message(call.message.chat.id, f'Отправьте Ваше изображение (желательно формата JPG, или PNG, но лучше JPG) без сжатия (также можно и сжатием, но фотография может быть испорчена в плане качества), после завершения процесса мы Вам отправим результат.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, make_black_image)
            if call.data == 'full_info_yt':
                bot.delete_message(call.message.chat.id, call.message.id)
                try:
                    bot.send_animation(call.message.chat.id, give_me_gif, caption=f'Введите ссылку на канал, пожалуйста.', parse_mode='Markdown', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                except telebot.apihelper.ApiTelegramException:
                    bot.send_message(call.message.chat.id, f'Введите ссылку на канал, пожалуйста.', parse_mode='Markdown', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, get_channel_details)
            if call.data == 'dialog-by-bot':
                bot.edit_message_text(f'Начните диалог с Флорестом прямо сейчас.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='leave_chat')))
                bot.register_next_step_handler(call.message, dialog_in_bot)
                bot.send_message(7455363246, f'Пользователь {call.from_user.first_name} присоединился(лась) к чату.\n{call.from_user.id}')
            if call.data == 'leave_chat':
                bot.send_message(7455363246, f'Пользователь {call.from_user.first_name} ({call.from_user.id}) покинул(а) чат.')
                bot.delete_message(call.message.chat.id, call.message.id)
                bot.clear_step_handler_by_chat_id(call.message.chat.id)
                bot.send_message(call.message.chat.id, f'Утилиты бота.', reply_markup=buttons)
            if call.data == 'download-video-from-yt':
                bot.delete_message(call.message.chat.id, call.message.id)
                try:
                    bot.send_animation(call.message.chat.id, give_me_gif, caption=f'Пришли мне ссылку на видео с YouTube.\nОно не должно длиться более 1 часа.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                except telebot.apihelper.ApiTelegramException:
                    bot.send_message(call.message.chat.id, f'Пришли мне ссылку на видео с YouTube.\nОно не должно длиться более 1 часа.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, download_youtube_video_func)
            if call.data == 'demotivator-create':
                bot.delete_message(call.message.chat.id, call.message.id)
                try:
                    bot.send_animation(call.message.chat.id, give_me_gif, caption='Пришлите фотографию, на основе которой мы сделаем демотиватор.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                except telebot.apihelper.ApiTelegramException:
                    bot.send_message(call.message.chat.id, 'Пришлите фотографию, на основе которой мы сделаем демотиватор.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, image_priem_to_demotivator)
            if call.data == 'predloshka':
                bot.edit_message_text(f'Привет! Здесь, ты можешь предложить пост Флоресту в @florestchannel.\nДля начала, надо согласиться с правилами ниже.\n\n> Запрещен шок-контент.\n> Запрещено обсуждать какие-либо социальные/религиозные/этнические группы в негативном ключе.\n> Запрещена реклама каких-либо левых ресурсов.\n> Запрещена пропаганда каких-либо идеологий.\n> Запрещены бессмысленные сообщения.\n\nПравила могут обновляться с течением времени.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Согласен', callback_data='sogl'), types.InlineKeyboardButton('Назад', callback_data='back')))
            if call.data == 'sogl':
                bot.edit_message_text(f'Отлично! Ты согласился с правилами.\nТеперь, начни писать пост.\nВот, что ты можешь использовать в посте: текстовые сообщения, аудиосообщения, музыка, видеосообщения, видео, фото (без сжатия).', call.message.chat.id, call.message.id)
                bot.register_next_step_handler(call.message, post_create)
            if call.data == 'search_youtube_video':
                bot.delete_message(call.message.chat.id, call.message.id)
                try:
                    bot.send_animation(call.message.chat.id, give_me_gif, caption='Введи поисковый запрос, который нужно сделать боту.\nМы пришлем Вам первое найденное видео, если на нем нет возрастных ограничений, или оно не длиться более 1 часа.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                except telebot.apihelper.ApiTelegramException:
                    bot.send_message(call.message.chat.id, 'Введи поисковый запрос, который нужно сделать боту.\nМы пришлем Вам первое найденное видео, если на нем нет возрастных ограничений, или оно не длиться более 1 часа.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, search_by_query)
            if call.data == 'information_about_ip':
                bot.delete_message(call.message.chat.id, call.message.id)
                try:
                    bot.send_animation(call.message.chat.id, give_me_gif, caption='Пришли мне IP адрес человека.\nПрошу обратить внимание, что информация является базовой, а также она была взята из открытых источников, т.е. не нарушает закон, или правила Telegram.\nВы сами берете ответственность за использование данной функции.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                except telebot.apihelper.ApiTelegramException:
                    bot.send_message(call.message.chat.id, 'Пришли мне IP адрес человека.\nПрошу обратить внимание, что информация является базовой, а также она была взята из открытых источников, т.е. не нарушает закон, или правила Telegram.\nВы сами берете ответственность за использование данной функции.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, deanon_by_ip_tg)
            if call.data == 'crypto-price':
                bot.delete_message(call.message.chat.id, call.message.id)
                bot.send_message(call.message.chat.id, f'Выберите крипту.', reply_markup=types.ReplyKeyboardMarkup(row_width=1).add(types.KeyboardButton('USDT'), types.KeyboardButton('BTC'), types.KeyboardButton('DOGE'), types.KeyboardButton('HMSTR')))
                try:
                    bot.send_animation(call.message.chat.id, give_me_gif, caption='Здесь, ты сможешь узнать цену криптовалют в RUB за одну единицу.\nДоступные крипты ниже.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                except:
                    bot.send_message(call.message.chat.id, 'Здесь, ты сможешь узнать цену криптовалют в RUB за одну единицу.\nДоступные крипты ниже.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, crypto_info)
            if call.data == 'sogl_group_rules':
                if bot.get_chat_member(group_id, call.from_user.id).status == 'left':
                    if not check_sub(call.from_user.id):
                        bot.answer_callback_query(call.id, f'Вы не подписаны на Telegram канал!\nИсправьте это и повторите попытку.\nТГК: @florestchannel', True)
                    else:
                        bot.answer_callback_query(call.id, f'Добро пожаловать к нам! Приятного общения.', True)
                        bot.approve_chat_join_request(group_id, call.from_user.id)
                        bot.send_photo(group_id, requests.get('https://cdn.discordapp.com/attachments/1246363653385752576/1309476788715388988/sticker_021307.webp?ex=6741b8cb&is=6740674b&hm=2f6c6e3f5533ac8ecdeb805cd7b957c7121cb27dd4bcc9ee843b1bb4be73159b&', headers=headers_for_html_requests, proxies=proxies).content, caption=f'Привет\, [{call.from_user.full_name}](tg://openmessage?user_id={call.from_user.id})\.\nЗдесь\, ты можешь найти новых собеседников и многое другое\.\nСоблюдай правила, которые находятся в описании группы\.\nНас уже {str(bot.get_chat_member_count(group_id))} участников ❤\nПо вопросам обратитесь к [главному администратору](tg://openmessage?user_id=7389388731)\.', parse_mode='MarkdownV2')
                else:
                    bot.answer_callback_query(call.id, f'Браток, это тебе больше не надо!\nДанная кнопка уже использована.', True)
                    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
            if call.data == 'password_check':
                bot.edit_message_text(f'Введи ник, по которому надо искать утечки.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, password_check)
            if call.data == 'nitro-generator':
                bot.edit_message_text(f'Данная функция генерирует немного ключей от Discord Nitro - платной подписки.\nКлючи могут не подойти, это значит, что надо попробовать еще раз.', call.message.chat.id, call.message.id)
                generate_nitro(call.message.chat.id, call.message.id)
            if call.data == 'fake_human':
                bot.answer_callback_query(call.id, f'Генерируем личность..', False)
                bot.edit_message_text(generate_human(), call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            if call.data == 'gen_info-btns':
                bot.edit_message_text(f'Категория генерации информации. Пароли, прокси, фейковые личности, ИНН и многое другое.', call.message.chat.id, call.message.id, reply_markup=gen_info_btns)
            if call.data == 'deanon_btns':
                bot.edit_message_text(f'Пробивчик. Используем только легальные способы, не нарушаем закон и правила тг.', call.message.chat.id, call.message.id, reply_markup=deanon_btns)
            if call.data == 'utilits_btns':
                bot.edit_message_text(f'Утилиты бота. Погода, демотиваторы, затемнение фото и другие функции.', call.message.chat.id, call.message.id, reply_markup=utilits_btns)
            if call.data == 'ai_btns':
                bot.edit_message_text(f'Генерация фото, текста (не всегда работает) и текст в речь (TTS).', call.message.chat.id, call.message.id, reply_markup=ai_btns)
            if call.data == 'youtube_funcs_btns':
                bot.edit_message_text(f'Парсеры для всего!\nYouTube, VK, Yandex, TikTok, Kwork и другие!', call.message.chat.id, call.message.id, reply_markup=parsers)
            if call.data == 'back_to_menu':
                bot.edit_message_text(f'Утилиты бота.', call.message.chat.id, call.message.id, reply_markup=buttons)
            if call.data == 'deanon_by_photo':
                bot.delete_message(call.message.chat.id, call.message.id)
                try:
                    bot.send_animation(call.message.chat.id, give_me_gif, caption='Дай мне фотографию для деанона.\nОтправляйте фото без сжатия в формате JPEG.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                except:
                    bot.send_message(call.message.chat.id, 'Дай мне фотографию для деанона.\nОтправляйте фото без сжатия в формате JPEG.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, deanonchik_photo)
            if call.data == 'imt_check':
                bot.delete_message(call.message.chat.id, call.message.id)
                try:
                    bot.send_animation(call.message.chat.id, give_me_gif, caption='Введите свой вес в килограммах.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                except:
                    bot.send_message(call.message.chat.id, 'Введите свой вес в килограммах.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, imt_check_kg)
            if call.data == 'write_to_user_without_nickname':
                bot.edit_message_text(F"Введи ID юзера.\nГде его можно узнать?\nСкачайте Ayugram с официального сайта разработчика, а затем зайдите в профиль к человеку. Внизу будет его ID.\nЛибо зайдите в @username_to_id_bot и нажмите на кнопку \"User\". Если пользователь не отображается, добавьте его в контакты и повторите попытку.", call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardButton('Отмена', callback_data='otmena_galya'))
                bot.register_next_step_handler(call.message, write_to_user_without_nickname)
            if call.data == 'send-mail-by-bot':
                bot.edit_message_text('Данная функция позволяет отправить письмо, используя специальную почту.\nВведи тему письма (заголовок).', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, get_email_title)
            if call.data == 'virus-check':
                bot.edit_message_text('С помощью данной новинки можно проверить наличие вирусов в файле.\nОбращаю внимание, что архивы, защищенные паролем проверить нельзя.\nПринимаются файлы 20 МБ и меньше.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, virus_check)
            if call.data == 'parsing-site':
                bot.edit_message_text(f'С помощью данной функции можно спарсить сайт.\nМы отправим вам файл с исходным кодом на языке HTML5.\nОтправьте ссылку в личные сообщения с ботом.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, parsing_site_fl)
            if call.data == 'google-photo-parsing':
                bot.edit_message_text(f'С помощью данной функции можно спарсить фото с Google Photo.\nМожет быть низкое разрешение, вам придет рандомное фото из списка возможных по вашему запросу.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, google_photo_parsing)
            if call.data == 'speech-to-text':
                bot.edit_message_text(f'С помощью данной функции можно узнать, о чем говорит человек в своем голосовом сообщении/видеосообщении, или в видео в длительностью 10 минут максимум.\nФункция на этапе разработки и использует Google Speech API.\nПоддерживается русский язык.\nПринимаются только голосовые/видео сообщения, а также видео (максимум 10 минут).', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, speech_to_text)
            if call.data == 'make-email-rassylka':
                bot.edit_message_text(f'Данная функция нужна для отправки сообщений с одинаковым текстом на определенное количество электронных почт.\nМаксимум почт за раз: 50 почт.\nВ библиотеке `florestbotfunctions` ограничений нет.\nОтправьте список электронных почт либо сообщением (каждая почта на новой строке), либо .txt документом (также, каждая почта на новой строке).', call.message.chat.id, call.message.id, parse_mode='Markdown', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, priem_emails_LOL)
            if call.data == 'cpp_compiler':
                bot.edit_message_text(f'Эта функция - встроенный компилятор для C++!\nНе надо качать G++, или другие компиляторы на свой компьютер, теперь можно получить быстрый доступ к нему через этого бота.\nКомпиляция не использует никаких флагов. Стандартная компиляция.\nПоддерживаются файлы: `.cpp`, `.cxx`.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')), parse_mode='Markdown')
                bot.register_next_step_handler(call.message, cpp_compiler)
            if call.data == 'vk_music_download':
                bot.edit_message_text(f'Напиши название песни для поиска на просторах VK музыки!\nИли "автор - название песни" для лучшей результативности!', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, vk_music_download)
            if call.data == 'last_post_vk':
                bot.edit_message_text(f'Пришлите название паблика, с которого нужно выслать пост.\nПример: Флорест | ВКонтакте.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, last_post_vk)
            if call.data == 'yandex_beta_parse':
                bot.edit_message_text(f'Функция парсит Yandex картинки, в большом количестве, затем скидывает вам .zip архив с картинками.\n\nПо какому запросу искать картинки?', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, get_query_p)
            if call.data == 'make-face-pixel-censor':
                bot.edit_message_text(f'Пришлите фотографию в расширении .JPG файлом (без сжатия).\n\n*Функция формата APLHA, могут быть лаги. Блюр может покрыть 90% лица, или меньше.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, face_obrab_func)
            if call.data == 'create-sticker-pack-with-florestik':
                bot.edit_message_text(f'Данная функция предназначена для простого создания стикер-паков в Telegram.\nПонадобиться `.zip` архив с фотографиями в расширении `.png` и `webm`.\n\nКак будет называться стикер-пак?', call.message.chat.id, call.message.id, parse_mode='Markdown', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, get_title_stickerpack)
            if call.data == 'games':
                bot.edit_message_text('Мини-игры в моем боте, созданные мной.', call.message.chat.id, call.message.id, reply_markup=games)
            if call.data == 'get-api-token':
                bot.answer_callback_query(call.id, f'API закрыт.')
            if call.data == 'info-about-minecraft-server':
                bot.edit_message_text(f'С помощью данной функции Вы можете узнать информацию о Java-сервере в Minecraft.\nВведите хост сервера, или IP+port (пример: 111.111.111.111:25565), или домен.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, info_about_minecraft_server)
            if call.data == 'add_watermark_on_photo':
                bot.edit_message_text(f'С помощью этой функции Вы можете добавить водяной знак на свою фотографию.\n\nОтправьте фото без сжатия, в формате JPG/PNG.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, add_watermark_on_photo_)
            if call.data == 'deepseek-ai-usage':
                bot.edit_message_text(f'Эта функция нужна для работы с DeepSeek-v3.\nЗа обработку фотографий отвечает GPT-4o-vision.\n\nНапишите тон общения: toxic, или auto?\ntoxic - токсичное общение, не зависимо от промпта.\nauto - интонация, в зависимости от запроса.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, toxic_or_auto_deepseek)
            if call.data == 'download-playlist-elements':
                bot.edit_message_text(f'Кратко, данная функция нужна для скачивания, в основном, музыкальных плейлистов.\nПлейлист должен быть с публичным доступом. Если в плейлисте больше 150 элементов, бот проигнорирует все, кроме первых 150. Если какое-то видео длиться больше 20 минут, - будет ошибка, а также игнорирование этого видео при скачивании контента.\n\nПришлите ссылку на открытый плейлист.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, download_playlist_elements)
            if call.data == 'parser-kwork':
                bot.edit_message_text(f'Эта функция нужна для парсинга биржи Kwork!\n\nВведи номер категории. К примеру, 11 - это программирование.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, parser_kwork)
            if call.data == 'cut-link-clck-yandex':
                bot.edit_message_text(f'Пожалуйста, пришлите ссылку для сокращения.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, cut_link_clck)
            if call.data == 'tiktok-video-downloader':
                bot.edit_message_text(f'Данная функция парсит тикток-видео за пару секунд.\n\nВведите ролик на видео формата https://www.tiktok.com/@<username>/video/<video_id> или https://vt.tiktok.com/...', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, tiktok_video_downloader)
            if call.data == 'create-request-to-florest-server':
                bot.edit_message_text(f'Привет! Ты готов приступить к отправке анкеты для того, чтобы попасть в белый список FlorestStreamsServer?\nПеред этим, пожалуйста, прочти правила по ссылке: https://telegra.ph/PRAVILA-FSS-08-02', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Да, подать заявку', callback_data='create-request-to-fss'), types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
            if call.data == 'create-request-to-fss':
                bot.edit_message_text(f'Благодарим! Напишите свое игровое имя.', call.message.chat.id, call.message.id)
                bot.register_next_step_handler(call.message, create_request_to_fss)
            if call.data == 'twitch-clips-downloader':
                bot.edit_message_text(f'С помощью данной функции можно спарсить клипы стримов с Twitch.\n\nВведи ссылку на клип.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, twitch_downloader)
            if call.data == 'russian-trio-parsing':
                bot.edit_message_text(f'Функция для парсинга видео RuTube, Яндекс Дзена и ВК.\n\nПришли ссылку на видео, пожалуйста.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, yandex_rutube_vk_parser_video)
            if call.data == 'unzip_apk_or_jar':
                bot.edit_message_text(f'Данная функция помогает расшифровать исходный код, к примеру плагина в майнкрафте (jar), или приложения от вашего друга-кодера (apk).\n\nПришлите файл jar/apk до 20 МБ.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, upzip_apk_or_jar)
            if call.data == 'from-zip-to-apk':
                bot.edit_message_text("Для быстрой компиляции исходного кода в архиве .zip в .apk.\n\nПришлите ваш .zip архив.", call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, unzip_zip_to_apk)
            if call.data == 'ai-upscale-x4':
                bot.edit_message_text('Функция для увеличения исходного разрешения фотографии в 4 раза.\n\nСкиньте фото (.JPG/.PNG), без сжатия.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, ai_upscale_x4)
            if call.data == 'ai-subtitles-video':
                bot.edit_message_text(f'Для использования этой функции, пожалуйста, дайте свой API ключ от этого сервиса: https://whisper-api.com/dashboard\n\nМожно при регистрации сразу получить 5 бесплатных токенов. API ключ будет использоваться только для проведения запросов в рамках бота.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, get_token_whisper)
            if call.data == 'img-format-convertation':
                bot.edit_message_text(f'Скиньте изображение без сжатия (файлом) в следующих допустимых форматах: .jpg, .png, .gif, .webp, .bmp.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, get_img_for_conv)
            if call.data == 'vk-profile-info':
                bot.edit_message_text(f'Пришли ник (без @) пользователя в VK.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, get_vk_profile_info)
            if call.data == 'steam-profile-parsing':
                bot.edit_message_text(f'Напиши свой ник в Steam для получения статистики.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, steam_profile_parsing)
            if call.data == 'last_news_meduza':
                parsed = feedparser.parse('https://meduza.io/rss/all').entries[:10]
                list_ = [f'{i.title} - {i.published}\n{i.link}' for i in parsed]
                string_ = "📰 Последние новости Meduza:\n\n" + "\n\n".join(list_)
                bot.edit_message_text(string_, call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            if call.data == 'parse_statii':
                bot.edit_message_text(f'Пожалуйста, пришлите ссылку на статью (Вики, любая статья) для парсинга.', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, parse_statii)
        else:
            bot.answer_callback_query(call.id, f'Привет, братец!\nСейчас идут технические работы по причине: {maintenance["reason"]}\nПриходите через {maintenance["time"]}.', True)
    else:
        bot.answer_callback_query(call.id, f'Эээ. А на ТГК подписончик оформить?(\nКанал: @florestchannel', True)

bot.infinity_polling(timeout=7200)

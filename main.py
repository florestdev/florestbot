# -*- coding: utf-8 -*-
import os
try:
    import telebot
    import g4f.Provider
    import g4f.client
    from telebot import TeleBot, types
    import time, pathlib, sys, logging
    import g4f, random, os
    from config import *
    from qrcode import make as create_qr
    import string, requests, threading
    from gtts import gTTS
    import io
    from telebot.util import quick_markup
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    from bs4 import BeautifulSoup
    from googleapiclient.discovery import build
    from pytubefix import Channel, YouTube, Search
    import faker as faker_
    from datetime import date
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    import smtplib
    import hashlib
    from virus_total_apis import PublicApi as VirusTotalPublicApi
    import speech_recognition as sr
    import subprocess
    from vkpymusic import Service
    import vk_api
    from googletrans import Translator
except ImportError:
    os.system('pip install -r requirements.txt')

url = 'https://florestdev.github.io/clicker-html/'
bot = TeleBot(token=token)
path = pathlib.Path(sys.argv[0]).parent.resolve()
users = []
admins = ['']
buttons = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Генерация информации, паролей и т.д.', callback_data='gen_info-btns'), types.InlineKeyboardButton('Деанончик', callback_data='deanon_btns'), types.InlineKeyboardButton('Утилиты', callback_data='utilits_btns'), types.InlineKeyboardButton('ИИ, текст в речь, картинки', callback_data='ai_btns'), types.InlineKeyboardButton('Функции YouTube', callback_data='youtube_funcs_btns'))
gen_info_btns = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Сгенерировать QR код', callback_data='generate_qr'), types.InlineKeyboardButton('Сгенирировать пароль', callback_data='generate_password'), types.InlineKeyboardButton('Топ песни с чартов', callback_data='download-audio-from-youtube'),  types.InlineKeyboardButton('Цена крипты', callback_data='crypto-price'), types.InlineKeyboardButton('Проверить пароль на утечки', callback_data='password_check'), types.InlineKeyboardButton('Подобрать нитро', callback_data='nitro-generator'), types.InlineKeyboardButton('Фейковая личность', callback_data='fake_human'), types.InlineKeyboardButton('Назад', callback_data='back_to_menu'))
deanon_btns = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Информация по IP', callback_data='information_about_ip'), types.InlineKeyboardButton('Деанон по фото', callback_data='deanon_by_photo'), types.InlineKeyboardButton('Назад', callback_data='back_to_menu'))
utilits_btns = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Погода', callback_data='weather-info'), types.InlineKeyboardButton('Сыграть в кликер [NEW]', web_app=types.WebAppInfo(url)), types.InlineKeyboardButton('Затемнить фотографию', callback_data='black-photo-make'), types.InlineKeyboardButton('Создать демотиватор', callback_data='demotivator-create'), types.InlineKeyboardButton('Предложить новость', callback_data='predloshka'), types.InlineKeyboardButton('Узнать ИМТ', callback_data='imt_check'), types.InlineKeyboardButton('Написать пользователю без ника', callback_data='write_to_user_without_nickname'), types.InlineKeyboardButton('Отправить письмо через бота', callback_data='send-mail-by-bot'), types.InlineKeyboardButton('Рассылка по E-Mail', callback_data='make-email-rassylka'), types.InlineKeyboardButton('Проверка на вирусы', callback_data='virus-check'), types.InlineKeyboardButton('Парсинг сайта', callback_data='parsing-site'), types.InlineKeyboardButton('Парсинг Google фото', callback_data='google-photo-parsing'), types.InlineKeyboardButton('C++ компилятор', callback_data='cpp_compiler'), types.InlineKeyboardButton('Скачать музыку с VK', callback_data='vk_music_download'), types.InlineKeyboardButton('Последний пост в VK', callback_data='last_post_vk'), types.InlineKeyboardButton('Назад', callback_data='back_to_menu'))
ai_btns = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Разговор с GigaChat', callback_data='ai-text'), types.InlineKeyboardButton('Нарисовать изображение', callback_data='ai-image'), types.InlineKeyboardButton('Из текста в речь', callback_data='text-to-speech'), types.InlineKeyboardButton('Из речи в текст', callback_data='speech-to-text'), types.InlineKeyboardButton('Перевод YouTube видео [BETA]', callback_data="translate-youtube-video"), types.InlineKeyboardButton('Назад', callback_data='back_to_menu'))
youtube_btns = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Подробная информация о YouTube канале', callback_data='full_info_yt'), types.InlineKeyboardButton('Скачать видео с YouTube', callback_data='download-video-from-yt'), types.InlineKeyboardButton('Найти видео по названию', callback_data='search_youtube_video'), types.InlineKeyboardButton('Назад', callback_data='back_to_menu'))

def start_translate_video(message: types.Message, url: str):
    bot.reply_to(message, f'Качаем видео...')
    video = YouTube(url, proxies=proxies)
    if video.length > 1200:
        bot.reply_to(message, f'Видео не может длиться свыше 20 минут.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        _ = random.random()
        video.streams.get_lowest_resolution().download(path, f'{_}.mp4')
        video.streams.filter(only_audio=True).first().download(path, f'{_}.mp3')
        bot.reply_to(message, f'Окэй. Скачали.\nОбработка..')
        subprocess.run(['ffmpeg', '-i', f'{_}.mp3', f'{_}.wav'], check=True)
        os.remove(path / f'{_}.mp3')
        bot.reply_to(message, f'Обработали аудио-файл..\nНачинаем транскрибацию.')
        lang = 'en-US'
        if message.text == 'Английский (US)':
            lang = 'en-US'
        elif message.text == 'Французский (FR)':
            lang = 'fr-FR'
        elif message.text == 'Немецкий (DE)':
            lang = 'de-DE'
        else:
            lang = 'pt-PT'
        r = sr.Recognizer()
        file = open(path / f'{_}.wav', 'rb')
        with sr.AudioFile(file) as source:
            audio = r.record(source)
        text = r.recognize_google(audio, language=lang)
        bot.reply_to(message, f'Расшифровали видео..\nПеревод.')
        translator = Translator()
        translated_text = translator.translate(text, dest='ru').text
        bot.reply_to(message, f'Видео переведено.')
        tts = gTTS(translated_text, lang='ru')
        tts.save(path / f'{_}.mp3')
        bot.reply_to(message, f'Новая аудио-дорожка с переводом готова!')
        os.remove(path / f'{_}.wav')
        __ = random.random()
        command = [
            'ffmpeg',
            '-i', path / f'{_}.mp4',
            '-i', path / f'{_}.mp3',
            '-map', '0:v',
            '-map', '1:a',
            '-c:v', 'copy',
            '-shortest',
            '-y',
            path / f'{__}.mp4'
        ]
        subprocess.run(command, check=True)
        bot.reply_to(message, f'Дорожка заменена. Начинаем отправку видео.')
        os.remove(path / f'{_}.mp4')
        os.remove(path / f'{_}.mp3')
        bot.send_chat_action(message.chat.id, 'upload_video', 300)
        likes = requests.get('https://www.googleapis.com/youtube/v3/videos', params={"part":"statistics", "id":video.video_id, "key":google_api_key}, proxies=proxies, headers=headers_for_html_requests).json()
        bot.send_video(message.chat.id, open(path / f'{__}.mp4', 'rb'), duration=video.length, caption=f'{video.author} - {video.title}\nКоличество просмотров: {video.views}\nКоличество отметок "нравится": {likes["items"][0]["statistics"]["likeCount"]}\nКоличество комментариев: {likes["items"][0]["statistics"]["commentCount"]}', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        os.remove(path / f'{__}.mp4')
        del _, __


def get_youtube_video_for_translate(message: types.Message):
    if not 'http' in message.text:
        bot.reply_to(message, f'Данная функция поддерживает только ссылки.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        bot.reply_to(message, f'Хорошо. Укажите язык.', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('Английский (US)'), types.KeyboardButton('Французский (FR)'), types.KeyboardButton('Немецкий (DE)'), types.KeyboardButton('Португальский (PT)')))
        bot.register_next_step_handler(message, start_translate_video, message.text)

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

def vk_music_download(message: types.Message):
    if not message.text:
        bot.reply_to(message, f'Напишите название песни текстовым сообщением.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        service = Service('KateMobileAndroid/56 lite-460 (Android 4.4.2; SDK 19; x86; unknown Android SDK built for x86; en)', token_for_vk)
        songs = service.search_songs_by_text(message.text)
        if len(songs) == 0:
            bot.reply_to(message, f'Песни по запросу не найдены на просторах VK музыки!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        else:
            bot.reply_to(message, f'Нашли! Скачиваем..')
            req = requests.get(songs[0].url)
            bot.send_audio(message.chat.id, req.content, caption=f'{songs[0].artist} - {songs[0].title}\nСсылка: {songs[0].url}\nДлительность (в секундах): {songs[0].duration}', duration=songs[0].duration, performer=songs[0].artist, title=songs[0].title, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))

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
        if message.video.duration > 600:
            bot.reply_to(message, f'Видео длиться более 10 минут, невозможно его перевести в текст.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
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


def search_by_query(message: types.Message):
    search = Search(message.text, proxies=proxies)
    search_process = bot.reply_to(message, f'Ищем...')
    if len(search.videos) == 0:
        bot.delete_message(search_process.chat.id, search_process.id)
        bot.reply_to(message, f'Ничего по Вашему запросу не было найдено на YouTube.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        video = search.videos[0]
        if video.age_restricted:
            bot.delete_message(search_process.chat.id, search_process.id)
            bot.reply_to(message, f'Видео имеет возрастные ограничения. Возможно, Вы запросили показать порнографический, или насильственный контент.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        else:
            if video.length > 3600:
                bot.delete_message(search_process.chat.id, search_process.id)
                bot.reply_to(message, f'Видео имеет длительность свыше одного часа. Возможно, Вы сделали запрос, согласно которому выдалось подобное видео.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            else:
                try:
                    buffer = io.BytesIO()
                    video.streams.get_lowest_resolution().stream_to_buffer(buffer)
                    bot.send_chat_action(message.chat.id, 'upload_video')
                    likes = requests.get('https://www.googleapis.com/youtube/v3/videos', params={"part":"statistics", "id":video.video_id, "key":google_api_key}, proxies=proxies, headers=headers_for_html_requests).json()
                    try:
                        bot.send_video(message.chat.id, buffer.getvalue(), caption=f'{video.author} - {video.title}\nКоличество просмотров: {video.views}\nКоличество отметок "нравится": {likes["items"][0]["statistics"]["likeCount"]}\nКоличество комментариев: {likes["items"][0]["statistics"]["commentCount"]}', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')), supports_streaming=True)
                    except:
                        bot.send_video(message.chat.id, buffer.getvalue(), caption=f'{video.author} - {video.title}\nКоличество просмотров: {video.views}', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')), supports_streaming=True)
                    bot.delete_message(search_process.chat.id, search_process.id)
                except:
                    bot.delete_message(message.chat.id, message.id)
                    try:
                        bot.send_animation(message.chat.id, error_gif, caption='Произошла ошибка.\n(Внимание! Есть проблемы со скачиванием контента для детей. Причина еще не выявлена.)', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
                    except:
                        bot.send_message(message.chat.id, 'Произошла ошибка.\n(Внимание! Есть проблемы со скачиванием контента для детей. Причина еще не выявлена.)', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))

def post_create(message: types.Message):
    if message.content_type not in ['document', 'video', 'video_note', 'audio', 'text', 'voice']:
        bot.reply_to(message, f'{message.from_user.first_name}, данная функция поддерживает только фото, видео, кружки, музыку, текстовые сообщения и голосовые сообщения.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    else:
        if message.text:
            bot.reply_to(message, f'{message.from_user.first_name}, отправили пост на модерацию. Если все нормально, он будет опубликован в @florestchannel.')
            bot.send_message('', f'{message.text}\n\n🤵 {message.from_user.first_name}')
        if message.video:
            bot.reply_to(message, f'{message.from_user.first_name}, отправили пост на модерацию. Если все нормально, он будет опубликован в @florestchannel.')
            bot.send_video('', bot.download_file(bot.get_file(message.video.file_id).file_path), caption=f'🤵 {message.from_user.first_name}')
        if message.video_note:
            bot.reply_to(message, f'{message.from_user.first_name}, отправили пост на модерацию. Если все нормально, он будет опубликован в @florestchannel.')
            bot.send_message('', f'🤵 {message.from_user.first_name}')
            bot.send_video_note('', bot.download_file(bot.get_file(message.video_note.file_id).file_path))
        if message.audio:
            bot.reply_to(message, f'{message.from_user.first_name}, отправили пост на модерацию. Если все нормально, он будет опубликован в @florestchannel.')
            bot.send_audio('', bot.download_file(bot.get_file(message.audio.file_id).file_path), f'🤵 {message.from_user.first_name}', message.audio.duration, message.audio.performer, message.audio.title)
        if message.voice:
            bot.reply_to(message, f'{message.from_user.first_name}, отправили пост на модерацию. Если все нормально, он будет опубликован в @florestchannel.')
            bot.send_voice('', bot.download_file(bot.get_file(message.voice.file_id).file_path), f'🤵 {message.from_user.first_name}', message.audio.duration)
        if message.document:
            if message.document.file_name[-4:] not in ['.jpg', '.png']:
                bot.reply_to(message, f'{message.from_user.first_name}, мы поддерживаем только фото формата `.jpg` и `.png`.', parse_mode='Markdown', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
            else:
                bot.reply_to(message, f'{message.from_user.first_name}, отправили пост на модерацию. Если все нормально, он будет опубликован в @florestchannel.')
                bot.send_photo('', bot.download_file(bot.get_file(message.document.file_id).file_path), f'🤵 {message.from_user.first_name}')

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
        try:
            yt_obj = YouTube(url, proxies=proxies)
            if yt_obj.age_restricted:
                bot.delete_message(message.chat.id, msg.id)
                bot.reply_to(message, f'Нельзя скачать видео с возрастными ограничениями.', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))
            else:
                if yt_obj.length > 3600:
                    bot.delete_message(message.chat.id, msg.id)
                    bot.reply_to(message, 'Нельзя скачивать видео с длительностью больше одного часа.', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))
                else:
                    buffer = io.BytesIO()
                    yt_obj.streams.get_lowest_resolution().stream_to_buffer(buffer)
                    bot.delete_message(message.chat.id, msg.id)
                    bot.send_chat_action(message.chat.id, f'upload_video')
                    likes = requests.get('https://www.googleapis.com/youtube/v3/videos', params={"part":"statistics", "id":yt_obj.video_id, "key":google_api_key}, proxies=proxies, headers=headers_for_html_requests).json()
                    try:
                        bot.send_video(message.chat.id, buffer.getvalue(), yt_obj.length, caption=f'{yt_obj.author} - {yt_obj.title}\nКоличество просмотров: {yt_obj.views}\nКоличество отметок "нравится": {likes["items"][0]["statistics"]["likeCount"]}\nКоличество комментариев: {likes["items"][0]["statistics"]["commentCount"]}', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')), supports_streaming=True)
                    except:
                        bot.send_video(message.chat.id, buffer.getvalue(), yt_obj.length, caption=f'{yt_obj.author} - {yt_obj.title}\nКоличество просмотров: {yt_obj.views}', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')), supports_streaming=True)
                    del buffer
        except Exception as e:
            print(e)
            bot.delete_message(message.chat.id, msg.id)
            try:
                bot.send_animation(message.chat.id, error_gif, caption=f'Произошла ошибка.\nВозможно, мы не смогли найти нужные стримы для данного видео.\nИли оно не существует.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
            except telebot.apihelper.ApiTelegramException:
                bot.send_message(message.chat.id, f'Произошла ошибка.\nВозможно, мы не смогли найти нужные стримы для данного видео.\nИли оно не существует.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
    elif message.text == 'Аудио':
        msg = bot.reply_to(message, f'Качаем аудио...', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))
        try:
            yt_obj = YouTube(url, proxies=proxies)
            if yt_obj.age_restricted:
                bot.delete_message(message.chat.id, msg.id)
                bot.reply_to(message, f'Нельзя скачать аудио с видео с возрастными ограничениями.', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))
            else:
                if yt_obj.length > 3600:
                    bot.delete_message(message.chat.id, msg.id)
                    bot.reply_to(message, 'Нельзя скачивать аудио с видео с длительностью больше одного часа.', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')))
                else:
                    buffer = io.BytesIO()
                    yt_obj.streams.get_audio_only().stream_to_buffer(buffer)
                    bot.delete_message(message.chat.id, msg.id)
                    bot.send_chat_action(message.chat.id, f'upload_voice')
                    likes = requests.get('https://www.googleapis.com/youtube/v3/videos', params={"part":"statistics", "id":yt_obj.video_id, "key":google_api_key}, proxies=proxies, headers=headers_for_html_requests).json()
                    try:
                        bot.send_audio(message.chat.id, buffer.getvalue(), duration=yt_obj.length, caption=f'{yt_obj.author} - {yt_obj.title}\nКоличество просмотров: {yt_obj.views}\nКоличество отметок "нравится": {likes["items"][0]["statistics"]["likeCount"]}\nКоличество комментариев: {likes["items"][0]["statistics"]["commentCount"]}', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')), performer=yt_obj.author, title=yt_obj.title)
                    except:
                        bot.send_audio(message.chat.id, buffer.getvalue(), duration=yt_obj.length, caption=f'{yt_obj.author} - {yt_obj.title}\nКоличество просмотров: {yt_obj.views}', reply_markup=types.ReplyKeyboardMarkup().add(types.KeyboardButton('🏡В меню')), performer=yt_obj.author, title=yt_obj.title)
                    del buffer
        except Exception as e:
            print(e)
            bot.delete_message(message.chat.id, msg.id)
            try:
                bot.send_animation(message.chat.id, error_gif, caption=f'Произошла ошибка.\nВозможно, мы не смогли найти нужные стримы для данного видео.\nИли оно не существует.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
            except telebot.apihelper.ApiTelegramException:
                bot.send_message(message.chat.id, f'Произошла ошибка.\nВозможно, мы не смогли найти нужные стримы для данного видео.\nИли оно не существует.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))

def download_youtube_video_func(message: types.Message):
    bot.reply_to(message, f'Отлично!\nВидео, или только аудио?', reply_markup=types.ReplyKeyboardMarkup(row_width=1).add(types.KeyboardButton('Видео'), types.KeyboardButton('Аудио')))
    bot.register_next_step_handler(message, download_video_func___, message.text)

def dialog_in_bot(message: types.Message) -> None:
    if message.text:
        bot.reply_to(message, f'Сообщение было отправлено. Ожидайте ответ.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='leave_chat')))
        msg=bot.send_message('', f'Сообщение от пользователя ({message.from_user.first_name}): {message.text}\n{message.from_user.id}')
        bot.register_next_step_handler(message, dialog_in_bot)
    else:
        bot.reply_to(message, f'Поддерживаются только текстовые сообщения. Напишите свое сообщение еще раз, пожалуйста.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Выйти из чата', callback_data='leave_chat')))
        bot.register_next_step_handler(message, dialog_in_bot)

def get_channel_details(message: types.Message):
    msg=bot.reply_to(message, f'Обработка запроса, пожалуйста, подождите...')
    try:
        channel = Channel(message.text, proxies=proxies)
        youtube = build('youtube', 'v3', developerKey=google_api_key)
        request = youtube.channels().list(part='snippet,statistics', id=channel.channel_id)
        response = request.execute()
        response_photo = requests.get(f'{response["items"][0]["snippet"]["thumbnails"]["high"]["url"]}', headers=headers_for_html_requests, proxies=proxies)
        bot.send_photo(message.chat.id, response_photo.content, caption=f'⚠️Информация и статистика о канале "`{response["items"][0]["snippet"]["title"]}`":\n\n**ИНФОРМАЦИЯ**\n🌐 Псевдоним: `{response["items"][0]["snippet"]["customUrl"]}`\n⛳ Страна: `{response["items"][0]["snippet"]["country"]}`\n\n**СТАТИСТИКА**\n👁️ Всего просмотров: `{response["items"][0]["statistics"]["viewCount"]}`\n♥️ Количество подписчиков: `{response["items"][0]["statistics"]["subscriberCount"]}`\n🎥 Количество видео на канале: `{response["items"][0]["statistics"]["videoCount"]}`\n🎥 Сколько плейлистов: `{str(len(channel.playlists))}`', parse_mode='MarkdownV2', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
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
                        bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, {message.from_user.first_name}\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})', reply_markup=markup1, parse_mode='MarkdownV2')
                    except:
                        bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, пользователь\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})', reply_markup=markup1, parse_mode='MarkdownV2')
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
                                bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, {message.from_user.first_name}\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})', reply_markup=markup1, parse_mode='MarkdownV2')
                            except:
                                bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, пользователь\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})', reply_markup=markup1, parse_mode='MarkdownV2')
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
                                bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, {message.from_user.first_name}\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})', reply_markup=markup1, parse_mode='MarkdownV2')
                            except:
                                bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, пользователь\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})', reply_markup=markup1, parse_mode='MarkdownV2')
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
                                    bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, {message.from_user.first_name}\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})', reply_markup=markup1, parse_mode='MarkdownV2')
                                except:
                                    bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, пользователь\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})', reply_markup=markup1, parse_mode='MarkdownV2')
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
                                    bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, {message.from_user.first_name}\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})', reply_markup=markup1, parse_mode='MarkdownV2')
                                except:
                                    bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, пользователь\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})', reply_markup=markup1, parse_mode='MarkdownV2')
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
                            bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, {message.from_user.first_name}\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})', reply_markup=markup1, parse_mode='MarkdownV2')
                        except:
                            bot.send_photo(message.chat.id, open(path / 'obloshka_bota.jpg', 'rb'), caption=f'Привет, пользователь\.\nВ данном боте Вы можете увидеть много различных функций для разных целей\.\n\nТолько в данном боте Вы можете скачать видео с YouTube длительностью до 1 часа бесплатно\.\nТакже Вы можете сделать черно\-белую фотографию из цветной\.\nГенерация QR, паролей, погода, ИИ \(ChatGPT, а также для картинок\) и много других функций абсолютно бесплатно\.\n\nЗадонатить можете здесь: /donate\nОбратиться за помощью: /support\n\nМой Telegram канал: [тык](https://t.me/florestchannel)\nВсе мои социальные сети: [тык](https://taplink.cc/florestone4185)\nРепозиторий бота: [тык](https://github.com/florestdev/florestbot)\nВаша реферальная ссылка: [тык](https://t.me/postbotflorestbot?start={message.from_user.id})', reply_markup=markup1, parse_mode='MarkdownV2')
                        msg=bot.send_message(message.chat.id, f'Утилиты бота', reply_markup=buttons)
                        bot.reply_to(msg, f'На будущее, вдруг меню пропадет.', reply_markup=types.ReplyKeyboardMarkup(True, input_field_placeholder=f'Сэр, да, сэр.', row_width=1).add(types.KeyboardButton('🏡В меню')))
                    else:
                        bot.reply_to(message, f'Ты не подписался на Telegram канал создателя?\nПора-бы это сделать!', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Мой Telegram канал', 'https://t.me/florestchannel'), types.InlineKeyboardButton('Подтвердить подписку', callback_data='check_sub')))

@bot.message_handler(commands=['support'])
def support(message: types.Message):
    if message.chat.type == 'private':
        bot.reply_to(message, f'Связаться со мной по поводу ошибок бота, либо сотрудничества или по другим причинам.\nМоя почта: florestone4185@internet.ru\nМой Discord аккаунт: florestdev\nЛибо нажмите кнопки ниже.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Написать на почту', 'https://inlnk.ru/oeaxRw'), types.InlineKeyboardButton('Поговорить внутри бота', callback_data='dialog-by-bot')))

def ai_obrabotchik(message: types.Message, type: int):
    if type == 1:
        if message.text:
            import requests, re, pathlib, sys
            url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

            payload={
                'scope': 'GIGACHAT_API_PERS'
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'RqUID': f'd17b9acc-2add-400e-8a3e-ff5a632ce31f',
                'Authorization': f'Basic ZDE3YjlhY2MtMmFkZC00MDBlLThhM2UtZmY1YTYzMmNlMzFmOjQ3YTliYjg2LTZkMDEtNGQ2NC05YmYzLWFlMGI0MGYxMDE3YQ=='
            }

            response = requests.request("POST", url, headers=headers, data=payload, verify=False)

            access_token = response.json()['access_token']

            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }

            data = {
                "model": "GigaChat",
                "messages": [
                    {
                        "role": "system",
                        "content": "Glory to Florest."
                    },
                    {
                        "role": "user",
                        "content": message.text
                    }
                ],
                "function_call": "auto"
            }

            patterns = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"

            response = requests.post(
                'https://gigachat.devices.sberbank.ru/api/v1/chat/completions',
                headers=headers,
                json=data,
                verify=False
            )
            json = response.json()
            matches = re.search(patterns, json['choices'][0]['message']['content'])
            if not matches:
                bot.reply_to(message, f"Нельзя создать изображение по данному запросу. Причина: {json['choices'][0]['message']['content'].lower()}", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад',callback_data='back')))
            else:
                match_ = matches.group(0)
                req_img = requests.get(f"https://gigachat.devices.sberbank.ru/api/v1/files/{match_}/content", headers={'Accept': 'application/jpg', "Authorization":f"Bearer {access_token}"}, verify=False, stream=True)
                bot.send_chat_action(message.chat.id, 'upload_photo')
                bot.send_photo(message.chat.id, req_img.content, 'Изображение по Вашему запросу.\nМогут быть неточности. Если они присутствуют, попробуйте изменить язык на котором вы пишите запрос, или его формуляровку.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                bot.clear_step_handler_by_chat_id(message.chat.id)
        else:
            bot.reply_to(message, f'Поддерживаются только текстовые сообщения.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
    if type == 2:
        if message.text:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Завершить диалог', callback_data='chat_zaversit'))
            bot.send_chat_action(message.chat.id, 'typing')
            import requests, json

            url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

            payload={
                'scope': 'GIGACHAT_API_PERS'
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'RqUID': 'd17b9acc-2add-400e-8a3e-ff5a632ce31f',
                'Authorization': 'Basic ZDE3YjlhY2MtMmFkZC00MDBlLThhM2UtZmY1YTYzMmNlMzFmOjQ3YTliYjg2LTZkMDEtNGQ2NC05YmYzLWFlMGI0MGYxMDE3YQ=='
            }

            response = requests.request("POST", url, headers=headers, data=payload, verify=False)

            access_token = response.json()['access_token']

            url1 = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

            payload1 = json.dumps({
                "model": "GigaChat",
                "messages": [
                    {
                        "role": "user",
                        "content": message.text
                    }
                ],
                "stream": False,
                "repetition_penalty": 1
            })
            headers1 = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}'
            }

            response1 = requests.request("POST", url1, headers=headers1, data=payload1, verify=False)

            result = response1.json()['choices'][0]['message']['content']

            bot.reply_to(message, result, reply_markup=markup, parse_mode='Markdown')
            bot.register_next_step_handler(message, ai_obrabotchik, 2)
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
                import requests, json

                url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

                payload={
                    'scope': 'GIGACHAT_API_PERS'
                }
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json',
                    'RqUID': 'd17b9acc-2add-400e-8a3e-ff5a632ce31f',
                    'Authorization': 'Basic ZDE3YjlhY2MtMmFkZC00MDBlLThhM2UtZmY1YTYzMmNlMzFmOjQ3YTliYjg2LTZkMDEtNGQ2NC05YmYzLWFlMGI0MGYxMDE3YQ=='
                }

                response = requests.request("POST", url, headers=headers, data=payload, verify=False)

                access_token = response.json()['access_token']

                url1 = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

                payload1 = json.dumps({
                    "model": "GigaChat",
                    "messages": [
                        {
                            "role": "user",
                            "content":text
                        }
                    ],
                    "stream": False,
                    "repetition_penalty": 1
                })
                headers1 = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                'Authorization': f'Bearer {access_token}'
                }

                response1 = requests.request("POST", url1, headers=headers1, data=payload1, verify=False)

                result = response1.json()['choices'][0]['message']['content']

                bot.reply_to(message, result, reply_markup=markup, parse_mode='Markdown')
                bot.register_next_step_handler(message, ai_obrabotchik, 2)
            except sr.UnknownValueError:
                bot.reply_to(message, f'Не удалось распознать речь в голосовом сообщении.\nПопробуйте еще раз!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Завершить чат', reply_markup='chat_zaversit')))
                bot.register_next_step_handler(message, ai_obrabotchik, 2)
            except:
                bot.reply_to(message, f'Неизвестная ошибка.\nВоспользуйтесь текстовым вводом.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Завершить чат', reply_markup='chat_zaversit')))
                bot.register_next_step_handler(message, ai_obrabotchik, 2)
            os.remove(path / f'audio_{chislo}.ogg')
            os.remove(path / f'audio_{chislo}.wav')


@bot.message_handler(commands=['admin_panel'])
def admin_panel(message: types.Message):
    if message.chat.type == 'private':
        if message.from_user.id != '':
            bot.reply_to(message, f'Ошибка! Доступ к данной панели есть только у создателя бота.')
        else:
            bot.reply_to(message, f'Здаров, {message.from_user.first_name}.\nНиже кнопки действий.', protect_content=True, reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Заблокировать видео', callback_data='ban-video'), types.InlineKeyboardButton('Заблокировать канал', callback_data='ban-channel'), types.InlineKeyboardButton('Добавить Inline клавиатуру', callback_data='add_keyboard_admin_panel')))

@bot.message_handler(commands=['donate'])
def send_donate(message: types.Message):
    if message.chat.type == 'private':
        bot.send_photo(message.chat.id, open(path / 'qr-donations.jpg','rb'), f'Привет! Данная функция нужна для того, чтобы Вы могли отправить деньги Флоресту.\nВоспользуйтесь QR кодом выше, либо кнопками ниже.', parse_mode='Markdown', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('DonationAlerts', url='https://donationalerts.com/r/florestdev4185'), types.InlineKeyboardButton('Звезды Telegram', callback_data='tg-stars_callback'), types.InlineKeyboardButton('Криптокошелек USDT$', callback_data='crypto-wallet'), types.InlineKeyboardButton('ЮMoney', callback_data='yoomoney-payment')))

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
            pass
        else:
            if message.voice:
                bot.send_chat_action(message.chat.id, 'typing')
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
                    bot.reply_to(message, f'В голосовом сообщении сказано следующее: `{text}`.', parse_mode='Markdown')
                except sr.UnknownValueError:
                    bot.reply_to(message, f'Не удалось распознать речь в данном голосовом сообщении.')
                except Exception as e:
                    bot.reply_to(message, f'Произошла неизвестная ошибка на нашей стороне. Обратитесь в поддержку и скиньте нам код ошибки.\nКод ошибки: `{e}`', parse_mode='Markdown')
                os.remove(path / f'audio_{chislo}.ogg')
                os.remove(path / f'audio_{chislo}.wav')
            elif message.video_note:
                bot.send_chat_action(message.chat.id, 'typing')
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
                    bot.reply_to(message, f'В видеосообщении сказано следующее: `{text}`.', parse_mode='Markdown', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                except sr.UnknownValueError:
                    bot.reply_to(message, f'Не удалось распознать речь в данном видеосообщении.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                except Exception as e:
                    bot.reply_to(message, f'Произошла неизвестная ошибка на нашей стороне. Обратитесь в поддержку и скиньте нам код ошибки.\nКод ошибки: `{e}`', parse_mode='Markdown', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                os.remove(path / f'video_{chislo}.mp4')
                os.remove(path / f'video_{chislo}.wav')
            elif message.video:
                bot.send_chat_action(message.chat.id, 'typing')
                if message.video.duration > 600:
                    bot.reply_to(message, f'Видео длиться более 10 минут, невозможно его перевести в текст.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                else:
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
                        bot.reply_to(message, f'В видео сказано следующее: `{text}`.', parse_mode='Markdown', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                    except sr.UnknownValueError:
                        bot.reply_to(message, f'Не удалось распознать речь в данном видео.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                    except Exception as e:
                        bot.reply_to(message, f'Произошла неизвестная ошибка на нашей стороне. Обратитесь в поддержку и скиньте нам код ошибки.\nКод ошибки: `{e}`', parse_mode='Markdown', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
                    os.remove(path / f'video_{chislo}.mp4')
                    os.remove(path / f'video_{chislo}.wav')
            else:
                pass
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
                        elif entities.type in ['mention', 'text_mention']:
                            bot.delete_message(message.chat.id, message.id)
                            bot.send_message(message.chat.id, f'{message.from_user.first_name} был(а) ограничен(а) за отправку упоминаний одного из участников группы на 5 минут.')
                            bot.restrict_chat_member(message.chat.id, message.from_user.id, time.time()+500, False, False, False, False, False, False, False, False)
                        elif entities.type == 'phone_number':
                            bot.delete_message(message.chat.id, message.id)
                            bot.send_message(message.chat.id, f'{message.from_user.first_name} был(а) ограничен(а) за отправку номера телефона на 5 часов.')
                            bot.restrict_chat_member(message.chat.id, message.from_user.id, time.time()+18000, False, False, False, False, False, False, False, False)
                        else:
                            pass
                else:
                    pass
            if message.text:
                if bot.get_chat_member(message.chat.id, message.from_user.id).status == 'member':
                    if check_text(message.text):
                        bot.delete_message(message.chat.id, message.id)
                        bot.send_message(message.chat.id, f'{message.from_user.first_name}, ваше сообщение нарушает правила.\nОно было удалено, а также Вы были ограничены на 15 минут, если Вы не нарушали правила, то обратитесь к администраторам из списка участников.')
                        bot.restrict_chat_member(message.chat.id, message.from_user.id, time.time()+900, False, False, False, False, False, False, False, False)
                    else:
                        pass
                else:
                    if check_text(message.text):
                        bot.reply_to(message, f'[!] Данное сообщение может нарушать правила, пожалуйста, обратитесь к создателю данной группы.')
                    else:
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
        bot.send_message(request.from_user.id, f'Привет, {request.from_user.first_name}!\nДля входа, вы должны принять эти правила:\n1. Оскорбления - мьют.\n2. Пиар - бан.\n3. Полит. срач, или любой другой срач - бан.\n4. Пропаганда запрещенных идеологий/движений - бан.\n5. Призывы к самоубийству/членовредительству - бан.\n\nВы согласны с ними?', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Согласен', callback_data='sogl_group_rules')))

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
            req = requests.get(f'https://www.google.ru/search?q=погода+в+{message.text}', headers=headers_for_html_requests, proxies=proxies)
            if req.status_code != 200:
                bot.reply_to(message, f'Произошла ошибка при попытке отображения погоды.\nВы либо ввели некорректное название населенного пункта, либо что-то случилось с нашим API.\nИзвиняемся за неудобства!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
                bot.clear_step_handler_by_chat_id(message.chat.id)
                send_reaction(message.chat.id, message.id, "🤷")
            else:
                soup = BeautifulSoup(req.text, "html.parser")
                temperature = soup.select("#wob_tm")[0].getText()
                title = soup.select("#wob_dc")[0].getText()
                humidity = soup.select("#wob_hm")[0].getText()
                time = soup.select("#wob_dts")[0].getText()
                wind = soup.select("#wob_ws")[0].getText()
                veroyatnost = soup.select("#wob_pp")[0].getText()
                bot.reply_to(message, f'Результаты по Вашему населенному пункту.\nТемпература: `{temperature} °C`\nОписание погоды: `{title.lower()}`\nВлажность: `{humidity}`\nВремя прогноза: `{time.lower()}`\nВетер: `{wind.lower()}`\nВероятность осадков: `{veroyatnost}`', parse_mode='Markdown', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        except:
            bot.reply_to(message, f'Произошла ошибка при попытке отображения погоды.\nВы либо ввели некорректное название населенного пункта, либо что-то случилось с нашим API.\nИзвиняемся за неудобства!', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
            bot.clear_step_handler_by_chat_id(message.chat.id)
            send_reaction(message.chat.id, message.id, "🤷")   
    else:
        bot.reply_to(message, f'Вы не отправили текстовое сообщение с названием Вашего города.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        send_reaction(message.chat.id, message.id, "🤷")      

def create_voice_by_text(message: types.Message):
    if not message.text:
        bot.reply_to(message, f'Не смогли найти в Вашем сообщении текст.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')))
        send_reaction(message.chat.id, message.id, "🤷")   
    else:
        try:
            bot.send_chat_action(message.chat.id, 'record_voice')
            engine = gTTS(message.text, lang='ru')
            bytes_ = io.BytesIO()
            engine.write_to_fp(bytes_)
            bot.send_voice(message.chat.id, bytes_.getvalue(), caption=f'Из текста в речь.\nПо запросу: {message.text}', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back')), reply_to_message_id=message.id)
        except Exception as e:
            bot.reply_to(message, f'Произошла ошибка: {e}\nЕсли вы запретили отправку голосовых, или видеосообщений в настройках конфедициальности, пожалуйста, добавьте бота в список исключений.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='back'), types.InlineKeyboardButton('Помощь', callback_data='help')))
            send_reaction(message.chat.id, message.id, "🤷")   

def ban_video_fl(message: types.Message):
    bot.reply_to(message, f'Внесли видео в блоклист.')
    file = open('prohibitions/banned_videos.txt', 'a')
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
                bot.send_message(call.message.chat.id, f'Было приятно с Вами пообщаться! Чтобы вернуться в меню, нажмите на кнопку ниже.', reply_markup=types.ReplyKeyboardMarkup(True, input_field_placeholder=f'Сэр, да, сэр.', row_width=1).add(types.KeyboardButton('🏡В меню')))
                bot.clear_step_handler_by_chat_id(call.message.chat.id)
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
                    bot.send_animation(call.message.chat.id, give_me_gif, caption='Напиши название своего населенного пункта.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                except telebot.apihelper.ApiTelegramException:
                    bot.send_message(call.message.chat.id, 'Напиши название своего населенного пункта.', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, get_weather)
            if call.data == 'ai-text':
                bot.edit_message_text(f'Напишите запрос для GigaChat, пожалуйста.\nИли используйте голосовые сообщения!', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, ai_obrabotchik, 2)
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
                bot.edit_message_text(f'Скачивание видео, информация о YouTube канале, поиск видео и т.д.', call.message.chat.id, call.message.id, reply_markup=youtube_btns)
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
            if call.data == 'translate-youtube-video':
                bot.edit_message_text(f'Данная функция переводит Ваше видео с английского, французского, немецкого, португальского языков.\nПоддерживаются видео с видеохостинга YouTube.\nДлительность: не более 20 минут.\nВремя обработки может разниться, просто ждите!', call.message.chat.id, call.message.id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Отмена', callback_data='otmena_galya')))
                bot.register_next_step_handler(call.message, get_youtube_video_for_translate)
        else:
            bot.answer_callback_query(call.id, f'Привет, братец!\nСейчас идут технические работы по причине: {maintenance["reason"]}\nПриходите через {maintenance["time"]}.', True)
    else:
        bot.answer_callback_query(call.id, f'Эээ. А на ТГК подписончик оформить?(\nКанал: @florestchannel', True)

bot.infinity_polling(timeout=7200)
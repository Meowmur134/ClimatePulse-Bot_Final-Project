from bs4 import BeautifulSoup
import requests
import telebot
from datetime import datetime


# Токен бота
token = "YOUR_TOKEN"
# Список городов для мониторинга аномалий
cities = ["kazan", "moscow", "london", "minsk", "dubai"]
months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
current_month_name = months[datetime.now().month - 1]


def get_climate_norm_temp(city):
    # Это URL-адрес веб-страницы, с которой мы хотим получить данные.
    climate_norm_url = f"https://pogoda.mail.ru/prognoz/{city}/by-month/"
    # Здесь мы используем библиотеку requests для отправки GET-запроса
    # к указанному URL-адресу и получения ответа.
    response = requests.get(climate_norm_url)
    # Мы передаем текст ответа от сайта (response.text)
    climate_norm_text = response.text
    # и указываем парсер, который будет использоваться ("html"),
    # чтобы создать объект BeautifulSoup для дальнейшего анализа HTML-кода.
    bs = BeautifulSoup(climate_norm_text, "html")


def get_current_temp(city):
    global current_temp_raw
    global current_temp
    # Это URL-адрес веб-страницы, с которой мы хотим получить данные.
    current_temp_url = f"http://wttr.in/{city}?format=3&m"
    # Здесь мы используем библиотеку requests для отправки GET-запроса
    # к указанному URL-адресу и получения ответа.
    response = requests.get(current_temp_url)
    # Мы передаем текст ответа от сайта (response.text)
    text = response.text
    current_temp_raw = text.replace("🌤️", "").replace(" ", "").strip()
    current_temp = current_temp_raw.replace("Kazan:+", "").replace("°C", "").strip()


bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def send_notification(message):
    bot.send_message(message.chat.id, "Привет! Я бот для мониторинга климатических аномалий")
    bot.send_message(message.chat.id, "Я проверяю, насколько погода сегодня отличается от климатической нормы")


@bot.message_handler(commands=['weather'])
def send_weather(message):
    text = message.text.split()
    if len(text) == 1:
        bot.send_message(message.chat.id, "Напиши /weather и название города на английском с большой буквы  через пробел")

    elif len(text) == 2:
        if text[1] in cities:
            get_climate_norm_temp(text[1])
            get_current_temp(text[1])
            bot.send_message(message.chat.id, current_temp_raw)
            bot.send_message(message.chat.id, current_temp)


bot.polling()

# Здесь мы ищем все нужные элементы на странице
# и сохраняем их в переменные.

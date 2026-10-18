from bs4 import BeautifulSoup
import pandas as pd
import requests
import telebot
from datetime import datetime


# Токен бота
token = "Your_token"
# Список городов для мониторинга аномалий
cities = ["kazan", "moscow", "london", "minsk", "dubai"]


def get_current_temp(city: str) -> str:
    global raw_temp
    global current_temp
    # Это URL-адрес веб-страницы, с которой мы хотим получить данные.
    raw_temp_url = f"http://wttr.in/{city}?format=3&m"
    current_temp_url = f"http://wttr.in/{city}?format=%t"
    # Здесь мы используем библиотеку requests для отправки GET-запроса
    # к указанному URL-адресу и получения ответа.
    try:
        # timeout=5 означает: если сайт не ответит за 5 секунд, мы прекращаем ждать
        response1 = requests.get(raw_temp_url, timeout=10)
        raw_temp = response1.text.strip()
        response2 = requests.get(current_temp_url, timeout=10)
        current_temp = response2.text.strip()
    except Exception as e:
        # Если сайт завис, бот не упадет, а запишет понятный текст
        print(f"Ошибка сети при запросе к wttr.in: {e}")
        raw_temp = f"{city.capitalize()}: Сервер погоды wttr.in временно перегружен"
        current_temp = f"{city.capitalize()}: Сервер погоды wttr.in временно перегружен"
    return raw_temp


def get_nasa_temp():
    global nasa_temp
    # Читаем файл от NASA (skiprows=1 пропускает техническую строку заголовка)
    df = pd.read_csv("GLB.Ts+dSST.csv", skiprows=1)
    current_year = datetime.now().year
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    current_month = months[datetime.now().month - 1]
    # Ищем через Pandas строку с текущим годом
    nasa_year = df[df["Year"] == current_year]
    # 2. ПРОВЕРКА: Если строки 2026 года вообще нет в базе, то есть на месте месяца стоит ***
    if nasa_year.empty or str(nasa_year[current_month].values[0]).strip() == "***":
        # Откатываемся на прошлый год, где октябрь гарантированно заполнен цифрами!
        nasa_year = df[df["Year"] == (current_year - 1)]
    # Метод .item() чисто и без ошибок достает значение из ячейки
    nasa_temp = nasa_year[current_month].item()


bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def send_notification(message):
    bot.send_message(message.chat.id, "Привет! Я бот для мониторинга климатических аномалий")
    bot.send_message(message.chat.id, "Я проверяю, насколько погода сегодня отличается от климатической нормы")


@bot.message_handler(commands=['weather'])
def send_weather_report(message):
    text = message.text.split()
    if len(text) == 1:
        bot.send_message(message.chat.id, "Напиши /weather и название города на английском с маленькой буквы  через пробел")

    elif len(text) == 2:
        if text[1] in cities:
            get_current_temp(text[1])
            get_nasa_temp()
            clean_temp_str = current_temp.replace("°C", "").replace("+", "").strip()
            temp = float(clean_temp_str)
            historic_temp = round(temp - float(nasa_temp), 2)
            bot.send_message(message.chat.id, raw_temp)
            bot.send_message(message.chat.id, f"Глобальное отклонение климата (NASA): +{nasa_temp}°C")
            bot.send_message(message.chat.id, f"Историческая норма температуры (NASA): +{historic_temp}°C")


bot.polling()

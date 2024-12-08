import logging
import requests
import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

API_TOKEN = '7746517875:AAH6fo3wE8IMNcT5NW1BceDdFIi85TsB-c4'
ESP_URL = 'http://192.168.1.100'  # Замените на IP ESP8266

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

# Инициализация планировщика
scheduler = BackgroundScheduler()
scheduler.start()

# Клавиатура команд
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
buttons = [
    KeyboardButton("💡 Регулировать освещение"),
    KeyboardButton("🖥️ Запустить программу"),
]
keyboard.add(*buttons)

# Команда /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Выберите действие:", reply_markup=keyboard)

# Регулировка освещения по времени суток
@dp.message_handler(lambda message: message.text == "💡 Регулировать освещение")
async def schedule_lighting(message: types.Message):
    scheduler.add_job(turn_on_light, 'cron', hour=18, minute=0)
    scheduler.add_job(turn_off_light, 'cron', hour=6, minute=0)
    await message.reply("Освещение будет включаться в 18:00 и выключаться в 6:00.")

def turn_on_light():
    requests.get(f"{ESP_URL}/lamp_on")
    print("Лампа включена (по расписанию).")

def turn_off_light():
    requests.get(f"{ESP_URL}/lamp_off")
    print("Лампа выключена (по расписанию).")

# Запуск программы по расписанию
@dp.message_handler(lambda message: message.text == "🖥️ Запустить программу")
async def schedule_program(message: types.Message):
    await message.reply("Введите имя программы и время запуска в формате:\n`notepad 15:30`")

@dp.message_handler(lambda message: ' ' in message.text)
async def handle_program_task(message: types.Message):
    try:
        program, time_str = message.text.split()
        run_time = datetime.strptime(time_str, "%H:%M")
        scheduler.add_job(run_program, 'date', run_date=run_time, args=[program])
        await message.reply(f"Задача для запуска программы '{program}' в {time_str} добавлена.")
    except Exception as e:
        await message.reply("Ошибка формата. Используйте формат: `notepad 15:30`")

def run_program(program):
    subprocess.Popen(program, shell=True)
    print(f"Программа '{program}' запущена.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

import logging
import requests
import subprocess
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

API_TOKEN = '7746517875:AAH6fo3wE8IMNcT5NW1BceDdFIi85TsB-c4'
ESP_URL = 'http://192.168.1.100'  # Замените на IP ESP8266

# Создание бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

logging.basicConfig(level=logging.INFO)

# Инициализация планировщика
scheduler = BackgroundScheduler()
scheduler.start()

# Клавиатура команд
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💡 Регулировать освещение")],
        [KeyboardButton(text="🖥️ Запустить программу")]
    ],
    resize_keyboard=True
)

# Команда /start
@router.message(Command(commands=['start']))
async def start(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=keyboard)

# Регулировка освещения по времени суток
@router.message(F.text == "💡 Регулировать освещение")
async def schedule_lighting(message: types.Message):
    scheduler.add_job(turn_on_light, 'cron', hour=18, minute=0)
    scheduler.add_job(turn_off_light, 'cron', hour=6, minute=0)
    await message.answer("Освещение будет включаться в 18:00 и выключаться в 6:00.")

def turn_on_light():
    requests.get(f"{ESP_URL}/lamp_on")
    print("Лампа включена (по расписанию).")

def turn_off_light():
    requests.get(f"{ESP_URL}/lamp_off")
    print("Лампа выключена (по расписанию).")

# Запуск программы по расписанию
@router.message(F.text == "🖥️ Запустить программу")
async def schedule_program(message: types.Message):
    await message.answer("Введите имя программы и время запуска в формате:\n`notepad 15:30`")

@router.message(F.text.contains(' '))
async def handle_program_task(message: types.Message):
    try:
        program, time_str = message.text.split()
        run_time = datetime.strptime(time_str, "%H:%M")
        scheduler.add_job(run_program, 'date', run_date=run_time, args=[program])
        await message.answer(f"Задача для запуска программы '{program}' в {time_str} добавлена.")
    except Exception as e:
        await message.answer("Ошибка формата. Используйте формат: `notepad 15:30`")

def run_program(program):
    subprocess.Popen(program, shell=True)
    print(f"Программа '{program}' запущена.")

if __name__ == '__main__':
    dp.run_polling(bot)

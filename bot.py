# bot.py
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import DEEPSEEK_API_KEY, TELEGRAM_BOT_TOKEN
from database import init_db, save_chat, get_chat
import requests
import json

# Инициализация базы данных
init_db()

# Отправка запроса в DeepSeek с отладкой
def send_to_deepseek(question):
    url = "https://api.deepseek.com/v1/chat/completions"  # Уточните URL в документации DeepSeek
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",  # Убедитесь, что модель указана правильно
        "messages": [{"role": "user", "content": question}]
    }

    print("Отправка запроса к DeepSeek API...")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(data, indent=2)}")

    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Ответ API (статус код): {response.status_code}")
        print(f"Ответ API (текст): {response.text}")

        # Проверяем, есть ли ошибки в ответе
        response.raise_for_status()

        # Парсим JSON-ответ
        response_json = response.json()
        print(f"Ответ API (JSON): {json.dumps(response_json, indent=2)}")

        # Возвращаем ответ нейросети
        return response_json["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as e:
        if response.status_code == 402:
            return "Ошибка: Недостаточно средств на балансе. Пожалуйста, пополните счёт."
        else:
            return f"Ошибка при запросе к нейросети: {e}"
    except requests.exceptions.RequestException as e:
        return f"Ошибка при запросе к нейросети: {e}"

# Обработка команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await update.message.reply_text("Привет! Я бот с нейросетью DeepSeek. Задайте ваш вопрос:")

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_message = update.message.text

    # Получаем текущий чат пользователя
    chat_data = get_chat(user_id)

    # Добавляем новое сообщение пользователя в чат
    chat_data += f"\nПользователь: {user_message}"

    # Отправляем запрос в DeepSeek
    bot_response = send_to_deepseek(user_message)

    # Добавляем ответ бота в чат
    chat_data += f"\nБот: {bot_response}"

    # Сохраняем обновлённый чат
    save_chat(user_id, chat_data)

    # Отправляем ответ пользователю
    await update.message.reply_text(bot_response)

# Запуск бота
if __name__ == '__main__':
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

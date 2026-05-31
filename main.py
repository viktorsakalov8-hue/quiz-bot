# import operator
# import random as rdm
# import time
# import operator as op
# import database
# from pyrogram import Client, filters
# from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
# import  quiz_logic
# import config
# import buttons
# import keyboards
# from custom_filters import button_filter
#
#
# bot = Client(
#     api_id=config.API_ID,
#     api_hash=config.API_HASH,
#     bot_token=config.BOT_TOKEN,
#     name="Bot_bez_zabot",
# )
#
#
#
#
#
# # Словарь для хранения текущего вопроса пользователя
# user_state = {}  # {user_id: current_question_index}
#
# @bot.on_message(filters=filters.command("start") | button_filter(buttons.start_button))
# async def start_command(client, message: Message):
#     user_id = message.from_user.id
#     username = message.from_user.username or "unknown"
#     # Убедимся, что пользователь есть в БД
#     if database.get_score(user_id) == 0 and not database.get_score(user_id) == 0:
#         database.update_score(user_id, username, 0)
#     await message.reply_text(
#         "🎉 Привет! Я квиз-бот.\n"
#         "Используй команды:\n"
#         "/quiz — начать викторину\n"
#         "/score — показать баллы\n"
#         "/help — помощь",
#                         reply_markup=keyboards.main_keyboard)
#
# @bot.on_message(filters=filters.command("help") | button_filter(buttons.help_button))
# async def help_command(client, message: Message):
#     await message.reply_text(
#         "📖 *Правила:*\n"
#         "• /quiz — запускает викторину (3 вопроса)\n"
#         "• На каждый вопрос — 4 варианта с кнопками\n"
#         "• За правильный ответ — +1 балл\n"
#         "• /score — показать текущий счёт\n"
#         "• Баллы сохраняются в базе данных",
#                         reply_markup=keyboards.main_keyboard)
#
# @bot.on_message(filters=filters.command("score") | button_filter(buttons.score_button))
# async def score_command(client, message: Message):
#     user_id = message.from_user.id
#     score = database.get_score(user_id)
#     await message.reply_text(f"🏆 Ваш текущий счёт: *{score}* баллов",
#                              reply_markup=keyboards.main_keyboard)
#
# @bot.on_message(filters=filters.command("quiz") | button_filter(buttons.quiz_button))
# async def quiz_start(client, message: Message):
#     user_id = message.from_user.id
#     user_state[user_id] = 0  # начинаем с первого вопроса
#     await send_question(client, message.chat.id, user_id, 0,
#                         reply_markup=keyboards.main_keyboard)
#
# async def send_question(client, chat_id, user_id, q_index):
#     if q_index >= len(quiz_logic.QUESTIONS):
#         # Викторина окончена
#         final_score = database.get_score(user_id)
#         await client.send_message(
#             chat_id,
#             f"✅ Викторина завершена!\nВаш результат: {final_score} / {len(quiz_logic.QUESTIONS)}\n"
#             "Спасибо за игру! 🎉"
#         )
#         if user_id in user_state:
#             del user_state[user_id]
#         return
#
#     q = quiz_logic.QUESTIONS[q_index]
#     text = f"📌 *Вопрос {q_index+1}/{len(quiz_logic.QUESTIONS)}:*\n{q['question']}"
#     markup = quiz_logic.get_question_markup(q_index)
#     await client.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
#
# @bot.on_callback_query()
# async def handle_callback(client, callback: CallbackQuery):
#     data = callback.data
#     user_id = callback.from_user.id
#     username = callback.from_user.username or "unknown"
#
#     if data.startswith("ans_"):
#         parts = data.split("_")
#         q_index = int(parts[1])
#         selected_idx = int(parts[2])
#
#         # Проверяем, что пользователь на правильном вопросе
#         if user_id not in user_state or user_state[user_id] != q_index:
#             await callback.answer("⚠️ Викторина не активна или вопрос устарел. Начни /quiz заново.", show_alert=True)
#             return
#
#         is_correct, explanation = quiz_logic.check_answer(q_index, selected_idx, user_id)
#
#         current_score = database.get_score(user_id)
#         if is_correct:
#             current_score += 1
#             database.update_score(user_id, username, current_score)
#             result_text = f"✅ Правильно! +1 балл\n{explanation}\nТвой счёт: {current_score}"
#         else:
#             database.update_score(user_id, username, current_score)
#             result_text = f"❌ Неправильно.\n{explanation}\nТвой счёт: {current_score}"
#
#         await callback.answer()  # убираем "часики"
#         await callback.message.delete()  # удаляем кнопки
#         await callback.message.reply_text(result_text)
#
#         # Переходим к следующему вопросу
#         next_q = q_index + 1
#         user_state[user_id] = next_q
#         await send_question(client, callback.message.chat.id, user_id, next_q)
#
#     else:
#         await callback.answer("Неизвестная команда", show_alert=True)
#
# bot.run()


from pyrogram import Client, filters, enums
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
import json
import config
import database as db
import buttons
import keyboards
import operator
import random as rdm
import time
import operator as op
import  quiz_logic
from custom_filters import button_filter

bot = Client("quiz_bot", bot_token=config.BOT_TOKEN,
             api_id=config.API_ID, api_hash=config.API_HASH)

db.init_db()

# Загрузка вопросов из JSON
with open("questions.json", "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

# Хранилище текущего вопроса для каждого пользователя
user_state = {}  # {user_id: current_question_index}


def get_question_markup(question_index):
    """Создаёт inline-кнопки для вариантов ответа"""
    q = QUESTIONS[question_index]
    buttons = []
    for i, opt in enumerate(q["options"]):
        buttons.append([InlineKeyboardButton(opt, callback_data=f"ans_{question_index}_{i}")])
    return InlineKeyboardMarkup(buttons)


async def send_question(client, chat_id, user_id, q_index):
    """Отправляет вопрос пользователю"""
    if q_index >= len(QUESTIONS):
        # Викторина окончена
        final_score = db.get_score(user_id)
        await client.send_message(
            chat_id,
            f"✅ Викторина завершена!\nВаш результат: {final_score} / {len(QUESTIONS)}\n"
            "Спасибо за игру! 🎉\n\n"
            "Хотите сыграть ещё? Используйте /quiz"
        )
        if user_id in user_state:
            del user_state[user_id]
        return

    q = QUESTIONS[q_index]
    text = f"📌 *Вопрос {q_index + 1}/{len(QUESTIONS)}:*\n\n{q['question']}"
    markup = get_question_markup(q_index)

    await client.send_message(
        chat_id,
        text,
        reply_markup=markup,
        parse_mode=enums.ParseMode.MARKDOWN
    )


@bot.on_message(filters=filters.command("start") | button_filter(buttons.start_button))
async def start_command(client, message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "unknown"

    # Проверяем, есть ли пользователь в БД
    if db.get_score(user_id) == 0:
        db.update_score(user_id, username, 0)

    await message.reply_text(
        "🎉 *Привет! Я квиз-бот.*\n\n"
        "📋 *Доступные команды:*\n"
        "/quiz — начать викторину\n"
        "/score — показать мои баллы\n"
        "/help — получить помощь\n\n"
        "Готов проверить свои знания? Нажми /quiz!",
        parse_mode=enums.ParseMode.MARKDOWN
    )


@bot.on_message(filters.command("help") | button_filter(buttons.help_button))
async def help_command(client, message: Message):
    await message.reply_text(
        "📖 *Правила викторины:*\n\n"
        "• /quiz — запускает викторину\n"
        "• На каждый вопрос есть 4 варианта ответа\n"
        "• Нажимай на кнопки с вариантами\n"
        f"• За правильный ответ — +1 балл\n"
        "• /score — показывает текущий счёт\n"
        f"• Всего вопросов: {len(QUESTIONS)}\n"
        "• Баллы сохраняются в базе данных\n\n"
        "*Удачи!* 🍀",
        parse_mode=enums.ParseMode.MARKDOWN
    )


@bot.on_message(filters.command("score") | button_filter(buttons.score_button))
async def score_command(client, message: Message):
    user_id = message.from_user.id
    score = db.get_score(user_id)

    await message.reply_text(
        f"🏆 *Ваш текущий счёт:* {score} баллов\n"
        f"📊 Всего вопросов: {len(QUESTIONS)}",
        parse_mode=enums.ParseMode.MARKDOWN
    )


@bot.on_message(filters.command("quiz") | button_filter(buttons.quiz_button))
async def quiz_start(client, message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "unknown"

    # Сбрасываем счёт пользователя перед новой викториной
    db.update_score(user_id, username, 0)
    user_state[user_id] = 0  # начинаем с первого вопроса

    await message.reply_text(
        "🎯 *Начинаем викторину!*\n\n"
        f"Всего вопросов: {len(QUESTIONS)}\n"
        "За каждый правильный ответ вы получаете 1 балл.\n\n"
        "*Поехали!* 🚀",
        parse_mode=enums.ParseMode.MARKDOWN
    )

    # Отправляем первый вопрос
    await send_question(client, message.chat.id, user_id, 0)

@bot.on_callback_query()
async def handle_callback(client, callback: CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id
    username = callback.from_user.username or "unknown"

    # Проверяем, что это ответ на вопрос
    if data.startswith("ans_"):
        parts = data.split("_")
        q_index = int(parts[1])
        selected_idx = int(parts[2])

        # Проверяем, активна ли викторина для этого пользователя
        if user_id not in user_state or user_state.get(user_id) != q_index:
            await callback.answer(
                "⚠️ Викторина не активна или вопрос устарел.\n"
                "Начните новую викторину командой /quiz",
                show_alert=True
            )
            try:
                await callback.message.delete()
            except:
                pass
            return

        # Проверяем правильность ответа
        correct_idx = QUESTIONS[q_index]["correct"]
        explanation = QUESTIONS[q_index]["explanation"]

        current_score = db.get_score(user_id)

        if selected_idx == correct_idx:
            current_score += 1
            db.update_score(user_id, username, current_score)
            result_text = f"✅ *Правильно!* +1 балл\n\n{explanation}\n\n📊 Твой счёт: {current_score}/{len(QUESTIONS)}"
        else:
            correct_answer = QUESTIONS[q_index]["options"][correct_idx]
            db.update_score(user_id, username, current_score)
            result_text = f"❌ *Неправильно*\n\nПравильный ответ: *{correct_answer}*\n\n{explanation}\n\n📊 Твой счёт: {current_score}/{len(QUESTIONS)}"

        # Отвечаем на callback
        await callback.answer()

        # Удаляем сообщение с кнопками
        try:
            await callback.message.delete()
        except:
            pass

        # Отправляем результат
        await callback.message.reply_text(result_text, parse_mode=enums.ParseMode.MARKDOWN)

        # Переходим к следующему вопросу
        next_q = q_index + 1
        user_state[user_id] = next_q
        await send_question(client, callback.message.chat.id, user_id, next_q)

    else:
        await callback.answer("❓ Неизвестная команда", show_alert=True)


bot.run()



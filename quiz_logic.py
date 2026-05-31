import json
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

with open("questions.json", "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

user_question_index = {}

def get_question_markup(question_index):
    q = QUESTIONS[question_index]
    buttons = []
    for i, opt in enumerate(q["options"]):
        buttons.append([InlineKeyboardButton(opt, callback_data=f"ans_{question_index}_{i}")])
    return InlineKeyboardMarkup(buttons)

def check_answer(question_index, selected_idx, user_id):
    correct = QUESTIONS[question_index]["correct"]
    if selected_idx == correct:
        return True, QUESTIONS[question_index]["explanation"]
    else:
        return False, f"❌ Неверно. {QUESTIONS[question_index]['explanation']}"
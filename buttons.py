from pyrogram.types import KeyboardButton
from pyrogram import emoji
start_button = KeyboardButton(f"{emoji.LAST_TRACK_BUTTON} Старт")
quiz_button = KeyboardButton('🎮Викторина')
score_button = KeyboardButton('📊Счет')
help_button = KeyboardButton('Руководство')
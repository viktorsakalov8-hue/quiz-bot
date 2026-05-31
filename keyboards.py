from pyrogram.types import ReplyKeyboardMarkup
import buttons

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [buttons.quiz_button,
         buttons.score_button],
        [buttons.start_button],
        [buttons.help_button]
            ],
    resize_keyboard=True
)
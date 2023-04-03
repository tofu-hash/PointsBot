from aiogram.types import (InlineKeyboardButton,
                           InlineKeyboardMarkup)

cancel_reply_markup = InlineKeyboardMarkup()
cancel_reply_markup.add(InlineKeyboardButton(text='⏪ Отмена',
                                             callback_data='cancel'))

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder, KeyboardBuilder, KeyboardButton
from aiogram import types
from aiogram.filters.callback_data import CallbackData

builder1 = ReplyKeyboardBuilder()
builder1.row(
    types.KeyboardButton(text='Меню')
)
builder1.row(

    types.KeyboardButton(text='Пары сегодня'),
    types.KeyboardButton(text='Пары завтра'),
    types.KeyboardButton(text='Пара неделя'),
    types.KeyboardButton(text='Пары след неделя')
)
builder1.row(
    types.KeyboardButton(text='погода'),
    types.KeyboardButton(text='Старт'),
    types.KeyboardButton(text='ресет')
)


def get_numbers(count_people):
    builder = InlineKeyboardBuilder()
    pair_smiles = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    for i in range(count_people):
        builder.button(text=pair_smiles[i], callback_data=f'many_{i}')
    builder.adjust(5, 5)
    return builder.as_markup()


def get_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="💡Доп. Функции", callback_data="menu_additional"),
            types.InlineKeyboardButton(text="👤Профиль", callback_data="menu_profile")
        ],
        [
            types.InlineKeyboardButton(text="👨‍👩‍👧‍👦Друзья", callback_data="menu_friends"),
            types.InlineKeyboardButton(text="📚Расписание", callback_data="menu_schedule")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def confirm_delete_friends():
    buttons = [
        [
            types.InlineKeyboardButton(text="✅Да, удалить", callback_data="confirmation_yes"),
            types.InlineKeyboardButton(text="❌Нет", callback_data="confirmation_no")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def friend_menu(count_people):
    builder = InlineKeyboardBuilder()
    pair_smiles = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    for i in range(count_people):
        builder.button(text=pair_smiles[i], callback_data=f'friend_{i}')
    builder.button(text="🗑Очистить", callback_data="friend_deleteAll")
    builder.button(text="➕Добавить", callback_data="friend_add")
    builder.button(text='🔙Назад', callback_data='schedule_prev')
    if count_people == 1:
        builder.adjust(1, 3)
    elif count_people == 2:
        builder.adjust(2, 3)
    elif count_people == 3:
        builder.adjust(1, 2, 3)
    elif count_people == 4:
        builder.adjust(2, 2, 3)
    elif count_people == 5:
        builder.adjust(1, 2, 2, 3)
    elif count_people == 6:
        builder.adjust(2, 2, 2, 3)
    elif count_people == 7:
        builder.adjust(1, 2, 2, 2, 3)
    elif count_people == 8:
        builder.adjust(2, 2, 2, 2, 3)
    elif count_people == 9:
        builder.adjust(1, 2, 2, 2, 2, 3)
    elif count_people == 10:
        builder.adjust(2, 2, 2, 2, 2, 3)
    return builder.as_markup()


def friend_add():
    buttons = [
        [
            types.InlineKeyboardButton(text="➕Добавить друга", callback_data="friend_add"),
        ],
        [
            types.InlineKeyboardButton(text='🔙Назад', callback_data='schedule_prev')
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_schedule():
    buttons = [
        [
            types.InlineKeyboardButton(text='На сегодня', callback_data='schedule_today')
        ],
        [
            types.InlineKeyboardButton(text='На завтра', callback_data='schedule_tomorrow')
        ],
        [
            types.InlineKeyboardButton(text='На эту неделю', callback_data='schedule_this_week')
        ],
        [
            types.InlineKeyboardButton(text='На следующую неделю', callback_data='schedule_next_week')
        ],
        [
            types.InlineKeyboardButton(text='🔙Назад', callback_data='schedule_prev')
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_schedule_from_friends():
    buttons = [
        [
            types.InlineKeyboardButton(text='На сегодня', callback_data='scheduleFriends_today')
        ],
        [
            types.InlineKeyboardButton(text='На завтра', callback_data='scheduleFriends_tomorrow')
        ],
        [
            types.InlineKeyboardButton(text='На эту неделю', callback_data='scheduleFriends_this_week')
        ],
        [
            types.InlineKeyboardButton(text='На следующую неделю', callback_data='scheduleFriends_next_week')
        ],
        [
            types.InlineKeyboardButton(text='🔙Назад', callback_data='menu_friends')
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def return_from_schedule_friends():
    buttons = [
        [
            types.InlineKeyboardButton(text='🔙Назад', callback_data='menu_friends')
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def return_from_schedule():
    buttons = [
        [
            types.InlineKeyboardButton(text='🔙Назад', callback_data='menu_schedule')
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_profile():
    buttons = [
        [
            types.InlineKeyboardButton(text='♻️Изменить ФИО♻️', callback_data='profile_changeName'),
            types.InlineKeyboardButton(text='Изменить список друзей', callback_data='profile_changeFriends')
        ],
        [
            types.InlineKeyboardButton(text='🔄Обновить расписание🔄', callback_data='profile_reload'),
            types.InlineKeyboardButton(text='🔔Уведомления🔔', callback_data='profile_notifications')
        ],
        [
            types.InlineKeyboardButton(text='🔙Назад', callback_data='schedule_prev')
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

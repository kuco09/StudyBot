from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

mainMenu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📚 Study new words")],
    [KeyboardButton(text="✍️ Write new words"), KeyboardButton(text="📂 Study exact group")],
    [KeyboardButton(text="⚙️ Settings")]],
    resize_keyboard=True)

createNewWords = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🆕 Create new words"), KeyboardButton(text="🔙 Back")]],
    resize_keyboard=True
)

groupOperation = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🗂️ Make new group"),
            KeyboardButton(text="✏️ Change exist group")],
            [KeyboardButton(text="🔙 Back to menu")]], 
    resize_keyboard=True, 
    one_time_keyboard=True
)

backButton = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔙 Back to menu")]], 
    resize_keyboard=True
)

changeGroup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🗑️ Delete words", callback_data="delete_word")],
    [InlineKeyboardButton(text="📝 Change name", callback_data="change_name_group")],
    [InlineKeyboardButton(text="🗑️ Delete group", callback_data="delete_group")]
])

changeSettings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="num of repeat old words", callback_data="num_of_repeat_old_words")]
])

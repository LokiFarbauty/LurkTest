from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand
from aiogram.utils.keyboard import ReplyKeyboardBuilder
#


async def create_keyboard(*buttons: str, buttons_dict: dict[str], adjust: int = 1) -> ReplyKeyboardMarkup:
    '''Создание клавиатуры KB-кнопок'''
    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    gen=[KeyboardButton(text=buttons_dict[button] if button in buttons_dict else button)
          for button in buttons]
    for btn in gen:
        kb_builder.add(btn)
    kb_builder.adjust(adjust)
    return kb_builder.as_markup(resize_keyboard=True)

async def create_keyboard_ex(buttons_dict: dict[str], adjust: int = 1) -> ReplyKeyboardMarkup:
    '''Создание клавиатуры KB-кнопок'''
    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    for btn_name in buttons_dict:
        btn = KeyboardButton(text=buttons_dict[btn_name])
        kb_builder.add(btn)
    kb_builder.adjust(adjust)
    return kb_builder.as_markup(resize_keyboard=True)

async def set_command_menu(bot: Bot, commands: dict[str, str]):
    '''
    Функция устанавливает меню команд бота
    :param bot:
    :return:
    '''
    main_menu = [
        BotCommand(command=command, description=description)
        for command, description in commands.items()
    ]
    await bot.set_my_commands(main_menu)

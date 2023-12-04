from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import BufferedInputFile, Message, ReplyKeyboardRemove
from aiogram import Bot
# from key_boards.start_keyboard import create_start_keyboard
# from key_boards.buttons import KB_BUTTONS
from aiogram_dialog import DialogManager, StartMode
#
from lexicon.buttons import START_BUTTONS, COMMON_DLG_BUTTONS
from lexicon.greetings import GREETINGS
import dialogs.states as states
from elements.keyboards import create_keyboard_ex
from tools.logers import setup_logger
from config import ProjectConfig
from elements.keyboards import create_keyboard
#

logger = setup_logger(logger_name='LurkoBotLogerBTN_HND', log_file=ProjectConfig.PATH_LOGS+'btn_handlers.log')

router: Router = Router()

# @router.message(F.text==COMMON_DLG_BUTTONS['старт'])
# #@router.message(Text)
# async def find_btn_push(message: Message, bot: Bot, dialog_manager: DialogManager):
#     # Выводим стартовое меню
#     kb = await create_keyboard_ex(START_BUTTONS, adjust=2)
#     grt_name = 'старт'
#     grt_desc = GREETINGS[grt_name] if grt_name in GREETINGS else grt_name
#     await message.answer(grt_desc, reply_markup=kb)
#     # Закрываем все ранее открытые диалоги
#     # try:
#     #     await dialog_manager.done()
#     #     await dialog_manager.reset_stack()
#     # except:
#     #     pass

# @router.message(F.text==START_BUTTONS['найти'])
# #@router.message(Text)
# async def find_btn_push(message: Message, bot: Bot, dialog_manager: DialogManager):
#     # удаление клавиатуры
#     try:
#         await message.answer(GREETINGS['поискать'], reply_markup=ReplyKeyboardRemove())
#         await dialog_manager.start(states.SG_find_post.input_words, mode=StartMode.RESET_STACK)
#     except Exception as ex:
#         logger.error(f"START_BUTTONS['найти']: {ex}")
#
# @router.message(F.text==START_BUTTONS['избранное'])
# #@router.message(Text)
# async def fav_btn_push(message: Message, bot: Bot, dialog_manager: DialogManager):
#     # удаление клавиатуры
#     try:
#         await message.answer(GREETINGS['избранное'], reply_markup=ReplyKeyboardRemove())
#         await dialog_manager.start(states.SG_favourites.start, mode=StartMode.RESET_STACK)
#     except Exception as ex:
#         logger.error(f"START_BUTTONS['избранное']: {ex}")
#
#
# @router.message(F.text==START_BUTTONS['топ'])
# #@router.message(Text)
# async def top_btn_push(message: Message, bot: Bot, dialog_manager: DialogManager):
#     # удаление клавиатуры
#     try:
#         kb= await create_keyboard('старт',buttons_dict=COMMON_DLG_BUTTONS)
#         await message.answer(GREETINGS['топ'], reply_markup=kb)
#         await dialog_manager.start(states.SG_tops.start, mode=StartMode.RESET_STACK)
#     except Exception as ex:
#         logger.error(f"START_BUTTONS['топ']: {ex}")
#
# @router.message(F.text==START_BUTTONS['случайно'])
# #@router.message(Text)
# async def random_btn_push(message: Message, bot: Bot, dialog_manager: DialogManager):
#     # удаление клавиатуры
#     try:
#         await message.answer(GREETINGS['случайно'], reply_markup=ReplyKeyboardRemove())
#         await dialog_manager.start(states.SG_random.start, mode=StartMode.RESET_STACK)
#     except Exception as ex:
#         logger.error(f"START_BUTTONS['случайно']: {ex}")

# @router.message(Text(text=lexicon.BUTTONS['судьи'], ignore_case=True))
# async def get_button_judges(message: Message, bot: Bot, dialog_manager: DialogManager):
#     # удаление клавиатуры
#     await message.answer('Я могу поискать судью.', reply_markup=ReplyKeyboardRemove())
#     await dialog_manager.start(states.SG_find_judge.main, mode=StartMode.RESET_STACK)
#
# @router.message(Text(text=lexicon.BUTTONS['суды'], ignore_case=True))
# async def get_button_courts(message: Message, bot: Bot, dialog_manager: DialogManager):
#     # удаление клавиатуры
#     await message.answer('Я могу поискать суд.', reply_markup=ReplyKeyboardRemove())
#     await dialog_manager.start(states.SG_find_court.main, mode=StartMode.RESET_STACK)
#
# @router.message(Text(text=lexicon.BUTTONS['лица'], ignore_case=True))
# async def get_button_persons(message: Message, bot: Bot, dialog_manager: DialogManager):
#     # удаление клавиатуры
#     await message.answer('Я могу поискать лиц, являющихся фигурантами дел.', reply_markup=ReplyKeyboardRemove())
#     await dialog_manager.start(states.SG_find_persons.main, mode=StartMode.RESET_STACK)
#
# @router.message(Text(text=lexicon.BUTTONS['мои'], ignore_case=True))
# async def get_button_persons(message: Message, bot: Bot, dialog_manager: DialogManager):
#     # удаление клавиатуры
#     await message.answer('Посмотрите список избранных дел:', reply_markup=ReplyKeyboardRemove())
#     await dialog_manager.start(states.SG_user_cases.main, mode=StartMode.RESET_STACK)


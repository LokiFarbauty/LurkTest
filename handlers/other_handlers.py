from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram_dialog import DialogManager, StartMode
from aiogram import Bot
# from lexicon.lexicon import GREETINGS
# from key_boards.start_keyboard import create_start_keyboard
from dbs import data_model
from tools.tg_bot_utils import get_tg_user_names
from lexicon.greetings import GREETINGS
from lexicon.buttons import START_BUTTONS
from elements.keyboards import create_keyboard_ex
#
from tools.logers import setup_logger
from config import ProjectConfig
from dialogs import states

logger = setup_logger(logger_name='LurkoBotLogerOTH_HND', log_file=ProjectConfig.PATH_LOGS+'other_handlers.log')

router: Router = Router()
#
@router.message(F.text)
async def proc_other_mess(message: Message, bot: Bot, dialog_manager: DialogManager):
    try:
        # Проверяем зарегистрирован ли пользователь
        user_id = message.from_user.id
        username, firstname, lastname = get_tg_user_names(message.from_user)
        user = data_model.check_user(user_id, username, firstname, lastname)
        # Выводим диалог
        #await dialog_manager.start(states.SG_find_post.input_words, mode=StartMode.RESET_STACK, data={'src_words': message.text})
        await dialog_manager.start(states.SG_start_menu.start, mode=StartMode.RESET_STACK, data={'user': user})
        # kb= await create_keyboard_ex(START_BUTTONS, adjust=2)
        # grt_name='старт'
        # grt_desc = GREETINGS[grt_name] if grt_name in GREETINGS else grt_name
        # await message.answer(grt_desc, reply_markup=ReplyKeyboardRemove())
    except Exception as ex:
        logger.error(f"F.text: {ex}")
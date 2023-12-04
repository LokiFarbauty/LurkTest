from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import Bot
from elements.keyboards import create_keyboard_ex
from aiogram_dialog import DialogManager, StartMode

from dbs import data_model
from tools.tg_bot_utils import get_tg_user_names
from lexicon.greetings import GREETINGS
from lexicon.buttons import START_BUTTONS
from tools.logers import setup_logger
from config import ProjectConfig
from dialogs import states
from objects.parser import ParseParams, ParserApp
import config

logger = setup_logger(logger_name='LurkoBotLogerBASE_HND', log_file=ProjectConfig.PATH_LOGS+'base_handlers.log')

router: Router = Router()

@router.message(CommandStart())
async def proc_start_command(message: Message, bot: Bot, dialog_manager: DialogManager):
    # Проверяем зарегистрирован ли пользователь
    try:
        #await message.answer(GREETINGS['поискать'], reply_markup=ReplyKeyboardRemove())
        user_id = message.from_user.id
        username, firstname, lastname = get_tg_user_names(message.from_user)
        user = data_model.check_user(user_id, username, firstname, lastname)
        # Закрываем все ранее открытые диалоги
        try:
            #await dialog_manager.done()
            await dialog_manager.reset_stack()
        except:
            pass
        # Выводим стартовое меню
        #kb= await create_keyboard_ex(START_BUTTONS, adjust=2)
        #grt_name='старт'
        #grt_desc = GREETINGS[grt_name] if grt_name in GREETINGS else grt_name
        #await message.answer(grt_desc, reply_markup=kb)
        await dialog_manager.start(states.SG_start_menu.start, mode=StartMode.RESET_STACK, data={'user': user})
        #await bot.send_message(message.chat.id, 'Главное меню')
    except Exception as ex:
        logger.error(f"CommandStart(): {ex}")

@router.message(Command('back'))
async def proc_back_command(message: Message, bot: Bot, dialog_manager: DialogManager):
    # Проверяем зарегистрирован ли пользователь
    try:
        # Проверяем зарегистрирован ли пользователь
        user_id = message.from_user.id
        username, firstname, lastname = get_tg_user_names(message.from_user)
        user = data_model.check_user(user_id, username, firstname, lastname)
        await dialog_manager.done()
        # user_id = message.from_user.id
        # username, firstname, lastname = get_tg_user_names(message.from_user)
        # user = data_model.check_user(user_id, username, firstname, lastname)
        # stack = dialog_manager.current_stack()
        # stack_len = len(stack.intents)
        # await dialog_manager.done()
        # if stack_len <= 1:
        #     kb = await create_keyboard_ex(START_BUTTONS, adjust=2)
        #     grt_name = 'старт'
        #     grt_desc = GREETINGS[grt_name] if grt_name in GREETINGS else grt_name
        #     await message.answer(grt_desc, reply_markup=kb)
    except Exception as ex:
        logger.error(f"Command('back'): {ex}")

@router.message(Command('post'))
async def proc_back_command(message: Message, bot: Bot, dialog_manager: DialogManager):
    # Проверяем зарегистрирован ли пользователь
    try:
        # Проверяем зарегистрирован ли пользователь
        user_id = message.from_user.id
        username, firstname, lastname = get_tg_user_names(message.from_user)
        user = data_model.check_user(user_id, username, firstname, lastname)
        msg_text = message.text
        pos = msg_text.find('post')
        msg_text = msg_text[pos+5:]
        msg_text = msg_text.strip()
        # Публикуем
        project_config = config.ProjectConfig()
        # Создаем парсер
        # target_ids=[-100157872], target_names=['lurkopub_alive']
        parser_params = ParseParams(target_ids=[-100157872, -26406986, -206243391],
                                    target_names=['lurkopub_alive', 'lurkopub', 'lurkupub'],
                                    token=project_config.VK_API_TOKEN, reserve_token=project_config.VK_API_TOKEN,
                                    min_text_len=project_config.PARSER_MIN_TEXT_LEN,
                                    telegraph_token=project_config.TELEGRAPH_TOKEN,
                                    telegraph_author=project_config.TELEGRAPH_AUTHOR,
                                    telegraph_author_url=project_config.TELEGRAPH_AUTHOR_URL,
                                    channel_id=project_config.CHANNEL_ID,
                                    errors_channel_id=project_config.CHANNEL_ID_ERROR_REPORT,
                                    proxy_http=project_config.PROXY_HTTP, proxy_https=project_config.PROXY_HTTPS,
                                    bot_url=project_config.BOT_URL)
        parser_obj = ParserApp(project_config, parser_params)
        err = await parser_obj.public_post_to_channel(bot=bot, post_id=int(msg_text), random=False, check_text=False)
    except Exception as ex:
        logger.error(f"Command('post'): {ex}")
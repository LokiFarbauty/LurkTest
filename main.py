import asyncio
import logging
import concurrent.futures as pool
from time import sleep
from aiogram import Bot, Dispatcher, F, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, ExceptionTypeFilter
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState, OutdatedIntent
from aiogram_dialog import setup_dialogs
from aiogram_dialog import DialogManager, StartMode
from datetime import datetime
#
import config
from tools.logers import setup_logger
from objects.parser import ParserApp, ParseParams
from config import ProjectConfig
from handlers import base_handlers, other_handlers, btn_handlers
from elements.keyboards import set_command_menu
import lexicon.menues as menues
from tools.terminal import console
from errors import Errors
from tools.tg_bot_utils import split_post_text, check_mat_in_text
# Диалоги
import dialogs.states as states
import dialogs.start_menu as start_menu
import dialogs.find_post as find_post
import dialogs.favourites as favourites
import dialogs.new as news
import dialogs.random_post as random_post
import dialogs.nothing as nothing
import dialogs.tops as tops
import dialogs.offer_post as offer_post

logger = setup_logger(logger_name='LurkoBotLoger', log_file=ProjectConfig.PATH_LOGS+'app.log')

async def on_unknown_intent(event, dialog_manager: DialogManager):
    """Example of handling UnknownIntent Error and starting new dialog."""
    logger.error(f'Сработало исключение: неизвестный замысел: {event.exception}!')
    #await dialog_manager.start(DialogSG.greeting, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND,)


async def on_unknown_state(event, dialog_manager: DialogManager):
    """Example of handling UnknownState Error and starting new dialog."""
    #logging.error("Restarting dialog: %s", event.exception)
    logger.error(f'Сработало исключение: неизвестное состояние: {event.exception}!')
    #print('Error: on_unknown_state')
    #await dialog_manager.start(DialogSG.greeting, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND,)

async def on_outdated_intent(event, dialog_manager: DialogManager):
    """Example of handling UnknownState Error and starting new dialog."""
    try:
        #await dialog_manager.done()
        await dialog_manager.reset_stack()
        logger.error(f'Сработало исключение: on_outdated_intent: {event.exception}!')
    except:
        pass
    await dialog_manager.start(states.SG_start_menu.start, mode=StartMode.RESET_STACK)

async def content_update(parser_obj: ParserApp, bot: Bot):
    print("Автообновление запущено.")
    timeout = 3600 * 24
    start_hour = 9
    end_hour = 22
    while True:
        cur_time = datetime.now().time().hour
        await asyncio.sleep(timeout)
        if cur_time <= start_hour or cur_time >= end_hour:
            await asyncio.sleep(1000)
        err = await parser_obj.update(show_progress=False)
        if err != Errors.NoError:
            logger.error(f'Ошибка в content_update(): {err}')
            # отправляем сведения об ошибке в канал
            if parser_obj.params.errors_channel_id != '':
                try:
                    await bot.send_message(chat_id=parser_obj.params.errors_channel_id,
                                           text=f'Ошибка в content_update(): {err}')
                except:
                    pass
        #await asyncio.sleep(timeout)


async def publicator(parser_obj: ParserApp, bot: Bot):
    print("Автопубликации в канал запущены.")
    start_hour = 9
    end_hour = 21
    timeout = round(3600 * 2.5)
    while True:
        err_str = ''
        cur_time = datetime.now().time().hour
        if cur_time >= start_hour and cur_time <= end_hour:
            try:
                err = await parser_obj.public_post_to_channel(bot, random=True)
            except Exception as ex:
                err = Errors.PyError
                err_str = ex
            if err != Errors.NoError:
                logger.error(f'Ошибка в publicator(): {err}: {err_str}')
                # отправляем сведения об ошибке в канал
                if parser_obj.params.errors_channel_id != '':
                    try:
                        await bot.send_message(chat_id=parser_obj.params.errors_channel_id, text=f'Ошибка в publicator(): {err}: {err_str}')
                    except:
                        pass
            await asyncio.sleep(timeout)
        else:
            await asyncio.sleep(timeout)

async def main():
    # loop = asyncio.get_running_loop()
    # result = await loop.run_in_executor(None, blocking_function)
    #
    logger.info('Starting bot')
    storage: MemoryStorage = MemoryStorage()
    try:
        bot: Bot = Bot(token=ProjectConfig.BOT_TOKEN, parse_mode='HTML')
    except Exception as ex:
        print(f'Создать объект бота нее удалось: {ex}')
        return
    try:
        # Получаем конфигурацияю проекта
        project_config = config.ProjectConfig()
        # Создаем парсер
        # target_ids=[-100157872], target_names=['lurkopub_alive']
        parser_params = ParseParams(target_ids=[-100157872, -26406986, -206243391], target_names=['lurkopub_alive', 'lurkopub', 'lurkupub'],
                                    token=project_config.VK_API_TOKEN, reserve_token=project_config.VK_API_TOKEN,
                                    min_text_len=project_config.PARSER_MIN_TEXT_LEN,
                                    telegraph_token=project_config.TELEGRAPH_TOKEN,
                                    telegraph_author=project_config.TELEGRAPH_AUTHOR,
                                    telegraph_author_url=project_config.TELEGRAPH_AUTHOR_URL,
                                    channel_id=project_config.CHANNEL_ID, errors_channel_id=project_config.CHANNEL_ID_ERROR_REPORT,
                                    proxy_http=project_config.PROXY_HTTP, proxy_https=project_config.PROXY_HTTPS,
                                    bot_url=project_config.BOT_URL)
        parser_obj = ParserApp(project_config, parser_params)
        # Запусп процесса автопубликации
        publicate_task = asyncio.create_task(publicator(parser_obj, bot))
        # Запусп процесса обновления
        updater_task = asyncio.create_task(content_update(parser_obj, bot))
        # Запуск консоли управления
        console_task = asyncio.create_task(console({'parser_obj': parser_obj, 'bot': bot}))
        #
        dp: Dispatcher = Dispatcher(storage=storage)
        # Срздаем роутер для диалогов
        dialog_router = Router()
        # Регистрируем все диалоги
        dialog_router.include_routers(
            start_menu.dialog_start_menu,
            find_post.dialog_get_post,
            favourites.dialog_favourites,
            news.dialog_news,
            random_post.dialog_random_post,
            nothing.dialog_nothing,
            tops.dialog_tops,
            offer_post.dialog_offer_post,
        #     find_judge.dialog_find_judge,
        #     find_court.dialog_court_found_result,
        #     find_court.dialog_find_court,
        #     find_person.dialog_person_found_result,
        #     find_person.dialog_find_person,
        #     user_case.dialog_user_cases,
        )
        # Регистрируем обработчики ошибок
        dp.errors.register(on_unknown_intent, ExceptionTypeFilter(UnknownIntent), )
        dp.errors.register(on_unknown_state, ExceptionTypeFilter(UnknownState), )
        dp.errors.register(on_outdated_intent, ExceptionTypeFilter(OutdatedIntent), )
        # Регистрируем основные роутеры
        dp.include_router(base_handlers.router)
        dp.include_router(btn_handlers.router)
        # Регистрируем диалоги в диспетчере
        dp.include_router(dialog_router)
        # Регистрируем прочие роутеры
        dp.include_router(other_handlers.router)
        # Просто нужно делать, чтобы все работало
        setup_dialogs(dp)
        # Формируем меню команд бота
        await set_command_menu(bot, menues.COMMAND_MENU)
        #
        # Просто нужно делать, чтобы все работало
        # await bot.delete_webhook(drop_pending_updates=True)  # убрать в продакшене
    except Exception as ex:
        print(f'Ошибка запуска бота: {ex}')
        return
    try:
        await dp.start_polling(bot)
    except Exception as ex:
        print(f'Ошибка в работе бота смотрите логи!')
        logger.error(ex)
    pass


# global


if __name__ == '__main__':
    try:
        asyncio.run(main())
        pass
    except (KeyboardInterrupt, SystemExit):
        logger.info('Bot stopped!')
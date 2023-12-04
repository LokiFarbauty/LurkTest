
import os
from dataclasses import dataclass


'''Конфигурация проекта'''
@dataclass
class ProjectConfig:
    PATH_PROJECT: str = os.path.dirname(os.path.abspath(__file__))+'\\' # путь к файлу проекта
    PATH_PARSER: str = PATH_PROJECT + 'parser\\' # путь к папке парсера
    PATH_DBS: str = PATH_PROJECT + 'dbs\\'  # путь к файлу базы данных
    PATH_ERRORS: str = PATH_PROJECT + 'errors\\' # путь к папке c ошибками
    PATH_LOGS: str = PATH_PROJECT + 'logs\\' # путь к папке c логами
    DB_NAME: str = 'db.db' # имя файла базы данных
    # Настройки парсера
    PROXY_HTTP: str = '' # не используется, параметры прокси беруться из системы через proxies=urllib.request.getproxies()
    PROXY_HTTPS: str = '' # не используется, параметры прокси беруться из системы через proxies=urllib.request.getproxies()
    PARSER_MIN_TEXT_LEN = 800
    VK_API_TOKEN: str = ''
    VK_API_TOKEN_RESERV: str = VK_API_TOKEN
    TELEGRAPH_TOKEN = ''
    TELEGRAPH_AUTHOR = 'MyLurkoBot'
    #TELEGRAPH_AUTHOR_URL = 'https://t.me/my_lurk_alive'
    TELEGRAPH_AUTHOR_URL = 'https://t.me/+TdMuwTUF-8ZhMDky'
    # Настройки бота
    BOT_URL = '' # Ссылка на бот
    BOT_TOKEN = ''  # Тестовый бот
    CHANNEL_ID = -000 # Канал куда публиковать рандомные пасты - VIDEO DUMP -1001891628599 -chat
    CHANNEL_ID_ERROR_REPORT = -000  # Канал для отправки отчета об ошибках



'''Исполняемая часть'''
# Создаем нужные папки
try:
    if not os.path.isdir(ProjectConfig.PATH_ERRORS):
        os.mkdir(ProjectConfig.PATH_ERRORS)
    if not os.path.isdir(ProjectConfig.PATH_LOGS):
        os.mkdir(ProjectConfig.PATH_LOGS)
    if not os.path.isdir(ProjectConfig.PATH_PROJECT):
        os.mkdir(ProjectConfig.PATH_PROJECT)
    if not os.path.isdir(ProjectConfig.PATH_DBS):
        os.mkdir(ProjectConfig.PATH_DBS)
except:
    pass
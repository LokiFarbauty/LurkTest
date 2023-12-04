import logging
from tools.logers import setup_logger
from config import ProjectConfig

dialogs_logger = setup_logger(logger_name='LurkoBotLogerDialogs', log_file=ProjectConfig.PATH_LOGS+'dialogs.log')
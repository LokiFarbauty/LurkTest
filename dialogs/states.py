from aiogram.fsm.state import State, StatesGroup
from aiogram_dialog import DialogManager


def get_offset(dialog_manager: DialogManager, data_key: str):
    data = dialog_manager.dialog_data
    try:
        offset = data['offset']
    except:
        offset = 0
        data['offset'] = 0
    # Защищаем выход индекса за границу
    if offset >= len(data[f'{data_key}']): offset = 0
    if offset < 0: offset = len(data[f'{data_key}']) - 1
    data['offset'] = offset
    return offset

def get_offset_ex(dialog_manager: DialogManager, data_key: str):
    data = dialog_manager.dialog_data
    try:
        offset = data[f'{data_key}_offset']
    except:
        offset = 0
        data[f'{data_key}_offset'] = 0
    # Защищаем выход индекса за границу
    if offset >= len(data[f'{data_key}']): offset = 0
    if offset < 0: offset = len(data[f'{data_key}']) - 1
    data[f'{data_key}_offset']=offset
    return offset

def get_current_dialog_data(dialog_manager: DialogManager, data_key: str):
    #data = dialog_manager.start_data
    data = dialog_manager.dialog_data
    try:
        offset = data['offset']
    except:
        offset = 0
        data['offset'] = 0
    # Защищаем выход индекса за границу
    if offset >= len(data[f'{data_key}']): offset = 0
    if offset < 0: offset = len(data[f'{data_key}']) - 1
    dialog_manager.dialog_data['offset'] = offset
    # Выбираем элемент
    try:
        res=data[f'{data_key}'][offset]
    except:
        res=[]
    return res

class SG_start_menu(StatesGroup):
    start = State()

class SG_nothing(StatesGroup):
    start = State()

class SG_find_post(StatesGroup):
    input_words = State()
    show_result = State()

class SG_favourites(StatesGroup):
    start = State()

class SG_tops(StatesGroup):
    start = State()

class SG_news(StatesGroup):
    start = State()

class SG_random(StatesGroup):
    start = State()

class SG_topic(StatesGroup):
    choose_topics = State()
    view_post = State()

class SG_offer_post(StatesGroup):
    add_text = State()
    add_img = State()
    finish = State()
# class SG_start_menu(StatesGroup):
#     main = State()
#
# class SG_find_case_for_number(StatesGroup):
#     input_number = State()
#
# class SG_find_case_for_court_and_person(StatesGroup):
#     input_court = State()
#     input_person = State()
#
# class SG_case_found_result(StatesGroup):
#     show_result = State()
#     show_persons = State()
#     show_case_movents = State()
#     add_to_my = State()
#
# class SG_find_judge(StatesGroup):
#     main = State()
#
# class SG_judge_found(StatesGroup):
#     main = State()
#     biography = State()
#     schedule = State()
#
# class SG_find_court(StatesGroup):
#     main = State()
#
# class SG_court_found(StatesGroup):
#     main = State()
#     calendar = State()
#     schedule = State()
#
# class SG_find_persons(StatesGroup):
#     main = State()
#
# class SG_persons_found(StatesGroup):
#     main = State()
#     cases = State()
#
# class SG_user_cases(StatesGroup):
#     main = State()
#     empty = State()


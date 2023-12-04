
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Cancel, Button, Back, Select, SwitchTo, Start
from aiogram_dialog.widgets.text import Const, Format, Multi
from dialogs import states
#
#import key_boards.start_keyboard as start_keyboard
#from lexicon.lexicon import GREETINGS
from elements.keyboards import create_keyboard_ex
from lexicon.greetings import GREETINGS
from lexicon.buttons import START_BUTTONS

async def event_next_case(callback: CallbackQuery, button: Button,
                    dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    try:
        offset = data['offset']
    except:
        offset = 0
    offset+=1
    dialog_manager.dialog_data['offset']=offset
    #
    try:
        aiogd_context = data['aiogd_context']
        aiogd_context.widget_data['text_scroll_post'] = 0
    except:
        pass

async def event_prev_case(callback: CallbackQuery, button: Button,
                    dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    try:
        offset = data['offset']
    except:
        offset = 0
    offset-=1
    if offset<0:
        offset=0
    dialog_manager.dialog_data['offset']=offset
    try:
        aiogd_context = data['aiogd_context']
        aiogd_context.widget_data['text_scroll_post'] = 0
    except:
        pass

PREV_CASE_BUTTON = Button(
    Const('⬅️'),
    on_click=event_prev_case,
    id="btn_prev_case"
)

NEXT_CASE_BUTTON = Button(
    Const('➡️'),
    on_click=event_next_case,
    id="btn_next_case"
)


async def show_main_menu(callback: CallbackQuery = None, dialog_manager: DialogManager = None):
    # kb = await create_keyboard_ex(START_BUTTONS, adjust=2)
    # grt_name = 'старт'
    # grt_desc = GREETINGS[grt_name] if grt_name in GREETINGS else grt_name
    # if callback!=None:
    #     await callback.message.answer(grt_desc, reply_markup=kb)
    # if dialog_manager!=None:
    #     await dialog_manager.event.answer(grt_desc, reply_markup=kb)
    await dialog_manager.start(states.SG_start_menu.start, mode=StartMode.RESET_STACK)


async def event_to_menu(callback: CallbackQuery, button: Button,
                    dialog_manager: DialogManager):
    '''Событие нажатия на кнопку - Назад в главное меню'''
    #await dialog_manager.done()
    try:
        await dialog_manager.done()
        await dialog_manager.reset_stack()
    except:
        pass
    await show_main_menu(callback)
    #await dialog_manager.start(states.SG_find_case_for_court_and_person.input_court, mode=StartMode.RESET_STACK)

MAIN_MENU_BUTTON=Button(
    Const("🔝 Главное меню"),
    on_click=event_to_menu,
    id="btn_to_menu")

async def event_back(callback: CallbackQuery, button: Button,
                    dialog_manager: DialogManager):
    '''Событие нажатия на кнопку - Назад'''
    try:
        stack = dialog_manager.current_stack()
        stack_len=len(stack.intents)
        await dialog_manager.done()
        if stack_len<=1:
            await show_main_menu(callback)
    except Exception as ex:
        #print(ex)
        pass

# Возвращает в предидущий диалог
BTN_BACK=Button(
    text=Const('⏏️'),
    id='btn_back',
    on_click=event_back)

async def event_back_window(callback: CallbackQuery, button: Button,
                    dialog_manager: DialogManager):
    '''Событие нажатия на кнопку - Назад (возврат в предидущее окно)'''
    await dialog_manager.back()

# Возвращает в предидущий диалог
BTN_BACK_WINDOW=Button(
    text=Const('🔙 Назад'),
    id='btn_back_window',
    on_click=event_back_window)
from aiogram.types import CallbackQuery, ContentType, Message, FSInputFile, ReplyKeyboardRemove
from aiogram import Bot, Dispatcher, F, Router
from aiogram_dialog import (
    ChatEvent, Dialog, DialogManager, setup_dialogs,
    ShowMode, StartMode, Window,
)
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Button, Row, Select, SwitchTo, Start, Next
from aiogram_dialog.widgets.kbd import (
    CurrentPage, FirstPage, LastPage, Multiselect, NextPage, NumberedPager,
    PrevPage, ScrollingGroup, StubScroll
)
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format, Multi, ScrollingText
from operator import itemgetter
from datetime import datetime
#
import dialogs.states as states
import dialogs.common_elements as common_elements
import dialogs.share_elements as share_elements
import config
import os
from tools.tg_bot_utils import del_forbiden_tg_char
import dbs.data_model as data_model
from lexicon.greetings import GREETINGS
from lexicon.buttons import START_BUTTONS
from elements.keyboards import create_keyboard
from dialogs import states
from lexicon.buttons import START_BUTTONS

async def start_main_menu(**_kwargs):
    #dm = _kwargs['dialog_manager']
    #args[1].dialog_data = data
    pass

async def getter_start_menu(**_kwargs):
    dm = _kwargs['dialog_manager']
    try:
        user = dm.start_data['user']
        user_name = f'{user.firstname} {user.lastname}'
    except:
        user_name = ''
    return {
        "greeting": GREETINGS['старт'].format(user_name),
        }

dialog_start_menu = Dialog(
    Window(
        Format('{greeting}'),
        Row(
            Start(Const(START_BUTTONS['новое']), id="dlg_news", state=states.SG_news.start),
            Start(Const(START_BUTTONS['найти']), id="dlg_find", state=states.SG_find_post.input_words),
        ),
        Row(
            Start(Const(START_BUTTONS['топ']), id="dlg_top", state=states.SG_tops.start),
            Start(Const(START_BUTTONS['случайно']), id="dlg_random", state=states.SG_random.start),
        ),
        Row(
            Start(Const(START_BUTTONS['избранное']), id="dlg_favour", state=states.SG_favourites.start),
            Start(Const(START_BUTTONS['предложить']), id="dlg_offer", state=states.SG_offer_post.add_text),
        ),
        state=states.SG_start_menu.start,
    ),
    getter=getter_start_menu,
)



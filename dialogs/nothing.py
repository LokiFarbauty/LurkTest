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


dialog_nothing = Dialog(
    Window(
        Const(GREETINGS['избранного нет']),
        common_elements.BTN_BACK,
        state=states.SG_nothing.start,
    ),
)

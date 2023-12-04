
from aiogram.types import CallbackQuery, ContentType, Message, FSInputFile, ReplyKeyboardRemove
from aiogram import Bot, Dispatcher, F, Router
from aiogram_dialog import (
    ChatEvent, Dialog, DialogManager, setup_dialogs,
    ShowMode, StartMode, Window,
)
from aiogram_dialog.widgets.common.scroll import ManagedScroll
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
from lexicon.buttons import COMMON_DLG_BUTTONS
from elements.keyboards import create_keyboard
from dialogs.dialogs_loger import dialogs_logger

async def finish(a,b, dialog_manager: DialogManager):
    await dialog_manager.done()



async def text_handler(message: Message, message_input: MessageInput,
                       dialog_manager: DialogManager):
    words = del_forbiden_tg_char(message.text)
    # Проверяем что сообщение не очень короткое и не очень длинное
    try:
        old_text = dialog_manager.dialog_data['text']
        first = False
    except:
        old_text = ''
        first = True
    if old_text == '':
        first = True
    if (len(words)<300) and first==True:
        await message.answer(GREETINGS['слишком короткий'])
    else:
        # Проверяем что оно уникальное
        post_offer = data_model.Offer_Post.select().where(data_model.Offer_Post.text == (old_text+words))
        if len(post_offer) > 0:
            await message.answer(GREETINGS['повтор'])
        else:
            dialog_manager.dialog_data['text'] = f'{old_text}{words}'
            try:
                await dialog_manager.next()
            except Exception as ex:
                dialogs_logger.error(f'dialog: offer_post, func: text_handler(), operation: dialog_manager.next(), '
                                     f'user_id: {message.from_user.id}, message_text:{message.text}, error: {ex}')


async def img_handler(message: Message, message_input: MessageInput,
                       dialog_manager: DialogManager):
    words = message.text
    try:
        # Проверяем что сообщение не очень короткое и не очень длинное
        if (words.find('https://')==-1):
            await message.answer(GREETINGS['не правильная ссылка'])
        else:
            dialog_manager.dialog_data['img_url'] = words
            await dialog_manager.next()
    except Exception as ex:
        dialogs_logger.error(f'dialog: offer_post, func: img_handler(), operation: all, '
                             f'user_id: {message.from_user.id}, message_text:{message.text}, error: {ex}')


async def getter_case_find(**_kwargs):
    user_id = 0
    try:
        user_id = _kwargs['event_from_user'].id
        user = data_model.get_user(user_tg_id=user_id)
        #context = _kwargs['aiogd_context']
        dialog_manager = _kwargs['dialog_manager']
        #dialog_manager.dialog_data['aiogd_context'] = context
        data = dialog_manager.dialog_data
        post_text = data['text']
        try:
            img_url = data['img_url']
        except:
            img_url = ''
        dt = datetime.now()
        dt = dt.replace(microsecond=0).timestamp()
        try:
            data_model.Offer_Post.create(user=user, text=post_text, img_url=img_url, dt=dt)
        except Exception as ex:
            await dialog_manager.done()
        try:
            dialog_manager.dialog_data['text'] = ''
        except:
            pass
        return _kwargs
    except Exception as ex:
        dialogs_logger.error(f'dialog: offer_post, func: getter_case_find(), operation: all, '
                             f'user_id: {user_id}, error: {ex}')




dialog_offer_post = Dialog(
    Window(
        Const(GREETINGS['новый пост']),
        MessageInput(text_handler, content_types=[ContentType.TEXT]),
        state=states.SG_offer_post.add_text,
    ),
    Window(
        Const(GREETINGS['новая картинка']),
        MessageInput(img_handler, content_types=[ContentType.TEXT]),
        SwitchTo(Const('Без картинки'),id='btn_no_img',state=states.SG_offer_post.finish),
        state=states.SG_offer_post.add_img,
    ),
    Window(
        Const(GREETINGS['новый пост получен']),
        common_elements.BTN_BACK,
        getter=getter_case_find,
        state=states.SG_offer_post.finish,
    ),
    on_process_result=finish,
)
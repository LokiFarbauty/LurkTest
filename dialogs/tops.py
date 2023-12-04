
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
from aiogram_dialog.widgets.media import StaticMedia, DynamicMedia
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


MAX_TEXT_SIZE = 700
async def finish(a,b, dialog_manager: DialogManager):
    await dialog_manager.done()

async def getter_tops(A, dialog_manager: DialogManager):
    posts = data_model.Post.select().order_by(data_model.Post.likes.desc())
    posts_count = data_model.Post.select().order_by(data_model.Post.likes.desc()).count()
    dialog_manager.dialog_data['posts_count'] = posts_count
    dialog_manager.dialog_data['posts'] = posts

async def getter_tops_start(**_kwargs):
    #user_id = _kwargs['event_from_user'].id
    context = _kwargs['aiogd_context']
    dialog_manager = _kwargs['dialog_manager']
    dialog_manager.dialog_data['aiogd_context'] = context
    data = dialog_manager.dialog_data
    img_url = ''
    img_exist = False
    try:
        offset = data['offset']
    except:
        offset = 0
        data['offset'] = 0
    # Получаем текст пост
    try:
        posts_count = data['posts_count']
        # Проверяем ограничение диапазона
        if offset >= posts_count:
            offset -= 1
            data['offset'] = offset
        posts = data['posts']
        post_id = posts[offset].get_id()
        data_model.increase_post_views(posts[offset])
        data['post_id'] = post_id
        try:
            img = data_model.get_post_photo(post=posts[offset])
            img_url = img.url
            img_exist = True
        except:
            pass
        post_desc = await share_elements.get_user_post_desc(posts[offset], offset, posts_count, show_count=False, debug=True)
    except Exception as ex:
        # if offset > 0:
        #     offset = 0
        #     data['offset'] = offset
        #     try:
        #         post_desc = await share_elements.get_user_post_desc(posts[offset])
        #     except:
        #         post_desc = share_elements.PostDesc(POST_TEXT='_', POST_DESC=GREETINGS['не найдено'], POST_EXIST=False)
        # else:
        post_desc = share_elements.PostDesc(POST_TEXT='_', POST_DESC=GREETINGS['не найдено'], POST_EXIST=False)
        dialog_manager.done()
    # Возвращаем значения
    return {
        "offset": offset,
        "post_desc": post_desc.POST_DESC,
        "post_text": post_desc.POST_TEXT,
        "post_exist": post_desc.POST_EXIST,
        'img_url': img_url,
        "img_exist": img_exist,
        }


dialog_tops = Dialog(
    Window(
        StaticMedia(
            url=Format('{img_url}'),
            type=ContentType.PHOTO,
            when=F["img_exist"]
            ),
            Format('{post_desc}'),
            ScrollingText(
                text=Format('{post_text}'),
                id='text_scroll_post',
                page_size=MAX_TEXT_SIZE,
                when=F["post_exist"]
                ),
            ScrollingGroup(
                NumberedPager(
                    scroll='text_scroll_post',
                    ),
                id='sgrp_scroll_post',
                width=8,
                height=1,
                hide_on_single_page=True,
                when=F["post_exist"],
            ),
            Row(
                common_elements.PREV_CASE_BUTTON,
                common_elements.BTN_BACK,
                share_elements.LIKE_BUTTON,
                share_elements.DISLIKE_BUTTON,
                share_elements.ADD_FAVOURITES_BUTTON,
                share_elements.REPOST_POST_URL_BUTTON,
                common_elements.NEXT_CASE_BUTTON,
                when=F["post_exist"]
            ),
            #common_elements.MAIN_MENU_BUTTON,
            getter=getter_tops_start,
            state=states.SG_tops.start,
        ),
    on_process_result=finish,
    on_start=getter_tops,
)

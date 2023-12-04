from operator import itemgetter
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
from peewee import fn
import random
#
import dialogs.states as states
import dialogs.common_elements as common_elements
import dialogs.share_elements as share_elements
import config
import os
from tools.tg_bot_utils import del_forbiden_tg_char
import dbs.data_model as data_model
from lexicon.greetings import GREETINGS
from lexicon.buttons import OTHER_BUTTONS
from elements.keyboards import create_keyboard

MAX_TEXT_SIZE = 700

async def topics_getter(**_kwargs):
    try:
        topics_num = data_model.Hashtag.select().where(fn.LENGTH(data_model.Hashtag.value)>3).count()
        topics_querry = data_model.Hashtag.select().where(fn.LENGTH(data_model.Hashtag.value)>3).order_by(data_model.Hashtag.value.asc())
        topics = [(topics_querry[i].value, i) for i in range(0, topics_num-1)]
        dialog_manager = _kwargs['dialog_manager']
        dialog_manager.dialog_data['topics'] = topics
    except Exception as ex:
        topics = []
    return {
        "topics": topics,
    }

async def getter_post_start(**_kwargs):
    #user_id = _kwargs['event_from_user'].id
    dialog_manager = _kwargs['dialog_manager']
    context = _kwargs['aiogd_context']
    dialog_manager.dialog_data['aiogd_context'] = context
    data = dialog_manager.dialog_data
    img_url = ''
    img_exist = False
    # try:
    #     offset = data['offset']
    # except:
    #     offset = 0
    #     data['offset'] = 0
    try:
        posts_count = data['posts_count']
        try:
            offset = random.randrange(posts_count-1)
        except:
            offset = 0
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
        post_desc = await share_elements.get_user_post_desc(posts[offset], offset, posts_count, show_count=False)
    except Exception as ex:
        post_desc = share_elements.PostDesc(POST_TEXT='_', POST_DESC=GREETINGS['не найдено'], POST_EXIST=False)
        await dialog_manager.done()
    # Возвращаем значения
    return {
        "post_desc": post_desc.POST_DESC,
        "post_text": post_desc.POST_TEXT,
        "post_exist": post_desc.POST_EXIST,
        'img_url': img_url,
        "img_exist": img_exist,
        }

async def event_page_click(*args):
    el_data = args[0].data
    pos = el_data.find('ms:')
    try:
        el_index = int(el_data[pos + 3:])
        el_str = args[2].dialog_data['topics'][el_index][0]
        selected_topics = args[2].dialog_data['selected topics']
    except Exception as ex:
        selected_topics = []
    if el_str in selected_topics:
        selected_topics.remove(el_str)
    else:
        if len(selected_topics)>3:
            await args[0].message.anwser(GREETINGS['много тем'])
        else:
            selected_topics.append(el_str)
    args[2].dialog_data['selected topics'] = selected_topics
    pass

# async def show_post_start(*args):
#     pass


async def event_show_post(callback: CallbackQuery, button: Button,
                    dialog_manager: DialogManager):
    try:
        selected_topics = dialog_manager.dialog_data['selected topics']
        # Получаем посты по выбранным темам
        posts = data_model.Post.select().join(data_model.Post_Hashtag).join(data_model.Hashtag).where(data_model.Hashtag.value.in_(selected_topics))
        posts_count = data_model.Post.select().join(data_model.Post_Hashtag).join(data_model.Hashtag).where(
            data_model.Hashtag.value.in_(selected_topics)).count()
        dialog_manager.dialog_data['posts'] = posts
        dialog_manager.dialog_data['posts_count'] = posts_count
        await dialog_manager.next()
    except Exception as ex:
        await callback.answer(GREETINGS['тема не выбрана'])

dialog_topics = Dialog(
    Window(
            Const(GREETINGS['темы']),
            ScrollingGroup(
                Multiselect(
                    Format("✓ {item[0]}"),
                    Format("{item[0]}"),
                    id="ms",
                    items="topics",
                    item_id_getter=itemgetter(1),
                    on_click=event_page_click,
                ),
                width=2,
                height=10,
                id="scroll_with_pager",
            ),
            Button(
                Const(OTHER_BUTTONS['показать']),
                on_click=event_show_post,
                id="btn_show_post"
            ),
            state=states.SG_topic.choose_topics,
    ),
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
                #common_elements.PREV_CASE_BUTTON,
                common_elements.BTN_BACK,
                share_elements.ADD_FAVOURITES_BUTTON,
                share_elements.RANDOM_BUTTON,
                #common_elements.NEXT_CASE_BUTTON,
                when=F["post_exist"]
            ),
            #common_elements.MAIN_MENU_BUTTON,
            getter=getter_post_start,
            state=states.SG_topic.view_post,
        ),
    getter = topics_getter,
)
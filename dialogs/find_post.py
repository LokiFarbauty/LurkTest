
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
import time
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

# async def start_dialog_getter(**_kwargs):
#     pass
#     dialog_manager = _kwargs['dialog_manager']
#     try:
#         words = dialog_manager.start_data['src_words']
#         docs = data_model.PostIndex.search(term=words, with_score=True, explicit_ordering=True)
#         try:
#             a = docs[0]
#             posts_count = data_model.PostIndex.search(term=words, with_score=True, explicit_ordering=True).count()
#             dialog_manager.dialog_data['posts_index'] = docs
#             dialog_manager.dialog_data['posts_count'] = posts_count
#             await dialog_manager.switch_to(states.SG_find_post.show_result, show_mode=StartMode.NORMAL)
#         except:
#             pass
#     except:
#         pass
#     return _kwargs

async def finish(a,b, dialog_manager: DialogManager):
    await dialog_manager.done()



async def words_handler(message: Message, message_input: MessageInput,
                       dialog_manager: DialogManager):
    '''
    Обработчик ввода слов для поиска
    :param message:
    :param message_input:
    :param dialog_manager:
    :return:
    '''
    #start = time.time()
    words = del_forbiden_tg_char(message.text)
    docs = data_model.PostIndex.search(term=words, with_score=True, explicit_ordering=True)
    #
    #print(docs[0].get_id())
    #
    #dialog_manager.dialog_data['offset'] = 0
    try:
        a=docs[0]
        posts_count = data_model.PostIndex.search(term=words, with_score=True, explicit_ordering=True).count()
        dialog_manager.dialog_data['posts_index'] = docs
        dialog_manager.dialog_data['posts_count'] = posts_count
        #end = time.time()
        #print(f'\nВремя операции - {end - start} сек.')
        await dialog_manager.next()
    except:
        # kb = await create_keyboard('старт', buttons_dict=COMMON_DLG_BUTTONS)
        # await message.answer(GREETINGS['ищу'], reply_markup=kb)
        await message.answer(GREETINGS['не найдено'])
        pass

    #await dialog_manager.start(states.SG_find_post.show_result, mode=StartMode.RESET_STACK, data={'cases': cases})
    # Завершаем диалог
    #await dialog_manager.done()


async def getter_case_find(**_kwargs):
    '''
    Готовим данные к выводу
    :param _kwargs:
    :return:
    '''
    # Получаем модель
    user_id = _kwargs['event_from_user'].id
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
    posts_index = data['posts_index']
    posts_count = data['posts_count']
    # Проверяем ограничение диапазона
    if offset>=posts_count:
        offset-=1
        data['offset'] = offset
    # Получаем текст поста
    try:
        # Уведличиваем счетчик просмотра постов
        #start = time.time()
        post_id = posts_index[offset].get_id()
        post = data_model.Post.get_by_id(post_id)
        data_model.increase_post_views(post)
        # Получаем описание
        post = data_model.get_post_for_text_id(post_id)
        data['post_id'] = post_id
        try:
            img = data_model.get_post_photo(post=post)
            img_url = img.url
            img_exist = True
        except:
            img_exist = False
        data['post'] = post
        post_desc = await share_elements.get_post_desc(post, posts_index, offset, user_id, posts_count, debug=True)
        # end = time.time()
        # print(f'\nВремя операции - {end - start} сек.')
    except Exception as ex:
        if offset>0:
            offset = 0
            data['offset'] = offset
            try:
                post_desc = await share_elements.get_post_desc(post, posts_index, offset, user_id, posts_count)
            except:
                post_desc = share_elements.PostDesc(POST_TEXT='_', POST_DESC=GREETINGS['не найдено'], POST_EXIST=False)
        else:
            post_desc = share_elements.PostDesc(POST_TEXT='_', POST_DESC=GREETINGS['не найдено'], POST_EXIST=False)
    text_len = len(post_desc.POST_TEXT)
    if text_len >= MAX_TEXT_SIZE*8:
        post_big = True
    else:
        post_big = False
    # Возвращаем значения
    return {
        "offset": offset,
        "post_desc": post_desc.POST_DESC,
        "post_text": post_desc.POST_TEXT,
        "post_exist": post_desc.POST_EXIST,
        "post_big": post_big,
        'img_url': img_url,
        "img_exist": img_exist,
    }



# async def event_number_unknown(callback: CallbackQuery, button: Button,
#                     dialog_manager: DialogManager):
#     '''Событие нажатия на кнопку - Номер дела не известен'''
#     await dialog_manager.start(states.SG_find_case_for_court_and_person.input_court, mode=StartMode.RESET_STACK)

async def event_page_changed(callback: CallbackQuery, Widget: ManagedScroll, dialog_manager: DialogManager):
    pass

dialog_get_post = Dialog(
    Window(
        Const(GREETINGS['найти']),
        MessageInput(words_handler, content_types=[ContentType.TEXT]),
        #common_elements.BTN_BACK,
        #common_elements.MAIN_MENU_BUTTON,
        state=states.SG_find_post.input_words,
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
                when=F["post_exist"],
                on_page_changed=event_page_changed,
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
                Button(Const(COMMON_DLG_BUTTONS['предыдущий элемент']), on_click=common_elements.event_prev_case, id="btn_prev_case"),
                common_elements.BTN_BACK,
                share_elements.LIKE_BUTTON,
                share_elements.DISLIKE_BUTTON,
                share_elements.ADD_FAVOURITES_BUTTON,
                share_elements.REPOST_POST_URL_BUTTON,
                share_elements.RANDOM_BUTTON,
                Button(Const(COMMON_DLG_BUTTONS['следующий элемент']), on_click=common_elements.event_next_case, id="btn_next_case"),
                when=F["post_exist"]
            ),
            #common_elements.MAIN_MENU_BUTTON,
            getter=getter_case_find,
            state=states.SG_find_post.show_result,
        ),
    on_process_result=finish,
)


async def start(message: Message, dialog_manager: DialogManager):
    # it is important to reset stack because user wants to restart everything
    await dialog_manager.start(states.SG_find_post.input_words, mode=StartMode.RESET_STACK)
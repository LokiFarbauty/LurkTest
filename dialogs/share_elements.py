
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Cancel, Button, Back, Select, SwitchTo, Start
from aiogram_dialog.widgets.text import Const, Format, Multi
from datetime import datetime
#
import dbs.data_model as data_model
from dataclasses import dataclass
import random
import config
from objects.parser import ParserApp, ParseParams



'''Элементы поста для вывода'''
@dataclass
class PostDesc:
    POST_TEXT: str = ''
    POST_DESC: str = ''
    POST_EXIST: bool = False


async def get_post_desc(post: data_model.Post, posts_index: data_model.PostIndex, offset: int, user_id: int, posts_count = 0, debug=False) -> PostDesc:
    post_text = posts_index[offset].text
    user = data_model.get_user(user_tg_id=user_id)
    if user != None:
        user.last_post_read = post.get_id()
        user.save()
    dt = post.dt
    dt = datetime.fromtimestamp(dt).strftime('%d.%m.%Y')
    if debug:
        post_id = post.get_id()
        post_desc = f'id: <b>{post_id}</b>, {offset+1} из <b>{posts_count}</b>. Опубликовано: <b>{dt}</b>. Оценка: <b>{post.likes}</b>.\n'
    else:
        post_desc = f'{offset+1} из <b>{posts_count}</b>. Опубликовано: <b>{dt}</b>. Оценка: <b>{post.likes}</b>.\n'
    post_exist = True
    res = PostDesc(POST_TEXT=post_text, POST_DESC=post_desc, POST_EXIST=post_exist)
    return res

async def get_user_post_desc(post: data_model.Post, offset=0, posts_count=0, show_count = True, debug=False) -> PostDesc:
    post_key = post.get_id()
    post_index = data_model.PostIndex.get_by_id(post_key)
    post_text = post_index.text
    dt = post.dt
    dt = datetime.fromtimestamp(dt).strftime('%d.%m.%Y')
    if show_count:
        post_desc = f'{offset+1} из <b>{posts_count}</b>. Опубликовано: <b>{dt}</b>. Оценка: <b>{post.likes}</b>.\n'
    else:
        if debug:
            post_id = post.get_id()
            post_desc = f'Опубликовано: <b>{dt}</b>. Оценка: <b>{post.likes}</b>. Id: <b>{post_id}</b>,\n'
        else:
            post_desc = f'Опубликовано: <b>{dt}</b>. Оценка: <b>{post.likes}</b>.\n'
    post_exist = True
    res = PostDesc(POST_TEXT=post_text, POST_DESC=post_desc, POST_EXIST=post_exist)
    return res


async def event_random_post(callback: CallbackQuery, button: Button,
                    dialog_manager: DialogManager):
    # Получаем пользователя
    user = data_model.get_user(user_tg_id=callback.from_user.id)
    if user!=None:
        # Получаем текущий пост
        try:
            data = dialog_manager.dialog_data
            posts_count = data['posts_count']
            offset = random.randrange(posts_count)
            dialog_manager.dialog_data['offset'] = offset
            try:
                aiogd_context = data['aiogd_context']
                aiogd_context.widget_data['text_scroll_post'] = 0
            except:
                pass
        except Exception as ex:
            pass

RANDOM_BUTTON = Button(
    Const('🎲'),
    on_click=event_random_post,
    id="btn_random_post"
)



async def event_add_favourites(callback: CallbackQuery, button: Button,
                    dialog_manager: DialogManager):
    # Получаем пользователя
    user = data_model.get_user(user_tg_id=callback.from_user.id)
    if user!=None:
        # Получаем текущий пост
        try:
            data = dialog_manager.dialog_data
            post_id = data['post_id']
            post = data_model.get_post_for_text_id(post_id)
            user_post = data_model.check_user_post(user, post)
            if user_post == None:
                user_favorites = data_model.User_Post.create(user=user, post=post)
                user_favorites.save()
                await callback.answer('Добавлено в избранное')
            else:
                await callback.answer('Уже в избранном')
        except Exception as ex:
            pass

ADD_FAVOURITES_BUTTON = Button(
    Const('⭐️'),
    on_click=event_add_favourites,
    id="btn_add_favourites"
)

async def event_del_favourite(callback: CallbackQuery, button: Button,
                    dialog_manager: DialogManager):
    # Получаем пользователя
    user = data_model.get_user(user_tg_id=callback.from_user.id)
    if user!=None:
        # Получаем текущий пост
        try:
            data = dialog_manager.dialog_data
            post_obj = data['post']
            #post = data_model.get_post_for_text_id(post_text_id)
            data_model.del_user_posts(post_obj)
            await callback.answer('Удалено из избранного')
        except Exception as ex:
            pass

DEL_FAVOURITES_BUTTON = Button(
    Const('🗑'),
    on_click=event_del_favourite,
    id="btn_del_favourites"
)

async def event_repost_post_url(callback: CallbackQuery, button: Button,
                    dialog_manager: DialogManager):
    # Получаем пользователя
    try:
        data = dialog_manager.dialog_data
        try:
            posts = data['posts']
            offset = data['offset']
            post = posts[offset]
        except:
            try:
                post = data['post']
            except:
                pass
        try:
            tg_url = post.telegraph_url
            # Создаем парсер для использования его функций
            # Получаем конфигурацияю проекта
            project_config = config.ProjectConfig()
            parser_params = ParseParams(target_ids=[-100157872, -26406986, -206243391],
                                        target_names=['lurkopub_alive', 'lurkopub', 'lurkupub'],
                                        token=project_config.VK_API_TOKEN, reserve_token=project_config.VK_API_TOKEN,
                                        min_text_len=project_config.PARSER_MIN_TEXT_LEN,
                                        telegraph_token=project_config.TELEGRAPH_TOKEN,
                                        telegraph_author=project_config.TELEGRAPH_AUTHOR,
                                        telegraph_author_url=project_config.TELEGRAPH_AUTHOR_URL,
                                        channel_id=project_config.CHANNEL_ID,
                                        errors_channel_id=project_config.CHANNEL_ID_ERROR_REPORT,
                                        proxy_http=project_config.PROXY_HTTP, proxy_https=project_config.PROXY_HTTPS,
                                        bot_url=project_config.BOT_URL)
            parser_obj = ParserApp(project_config, parser_params, need_loger=False)
            #
            if tg_url != '':
                await dialog_manager.event.bot.send_message(dialog_manager.event.from_user.id,
                                                            f'{tg_url}\nПодписывайтесь на наш <a href="{parser_params.telegraph_author_url}">телеграм-канал</a>.',
                                                            parse_mode='HTML')
            else:
                author_caption = f'\nБлагодарим за внимание!\nПодписывайтесь на наш <a href="{parser_obj.params.telegraph_author_url}">телеграм-канал</a>.\nЗаходите к нам в <a href="{parser_obj.params.bot_url}">бот</a>.'
                tg_url = await parser_obj.put_post_to_telegraph(post, author_caption=author_caption)
                if tg_url != '':
                    await dialog_manager.event.bot.send_message(dialog_manager.event.from_user.id,
                                                                f'{tg_url}\nПодписывайтесь на наш <a href="{parser_params.telegraph_author_url}">телеграм-канал</a>.',
                                                                parse_mode='HTML')
                    post.telegraph_url = tg_url
                    post.save()
                else:
                    await dialog_manager.event.answer('К сожалению сейчас получить ссылку для репоста невозможно. Попробуйте позднее.')
        except Exception as ex:
            await dialog_manager.event.answer('К сожалению сейчас получить ссылку для репоста невозможно. Попробуйте позднее.')
    except Exception as ex:
        pass

REPOST_POST_URL_BUTTON = Button(
    Const('📣'),
    on_click=event_repost_post_url,
    id="btn_repost_post"
)

async def event_like(callback: CallbackQuery, button: Button,
                    dialog_manager: DialogManager):
    # Получаем пользователя
    user = data_model.get_user(user_tg_id=callback.from_user.id)
    if user!=None:
        # Получаем текущий пост
        try:
            data = dialog_manager.dialog_data
            try:
                posts = data['posts']
                offset = data['offset']
                post = posts[offset]
            except:
                try:
                    post = data['post']
                except:
                    pass
            try:
                liked = data['liked']
                await callback.answer('Вы уже поставили оценку')
            except:
                #post = data_model.get_post_for_text_id(post_text_id)
                post.likes += 1
                post.save()
                data['liked'] = 1
                await callback.answer('Лайк учтен')
        except Exception as ex:
            pass

LIKE_BUTTON = Button(
    Const('👍'),
    on_click=event_like,
    id="btn_like"
)

async def event_dislike(callback: CallbackQuery, button: Button,
                    dialog_manager: DialogManager):
    # Получаем пользователя
    user = data_model.get_user(user_tg_id=callback.from_user.id)
    if user!=None:
        # Получаем текущий пост
        try:
            data = dialog_manager.dialog_data
            try:
                posts = data['posts']
                offset = data['offset']
                post = posts[offset]
            except:
                try:
                    post = data['post']
                except:
                    pass
            try:
                liked = data['disliked']
                await callback.answer('Вы уже поставили оценку')
            except:
                # post = data_model.get_post_for_text_id(post_text_id)
                post.likes -= 1
                post.save()
                data['disliked'] = 1
                await callback.answer('Дизлайк учтен')
        except Exception as ex:
            pass

DISLIKE_BUTTON = Button(
    Const('👎'),
    on_click=event_dislike,
    id="btn_dislike"
)
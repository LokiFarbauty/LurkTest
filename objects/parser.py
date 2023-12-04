
import os
from fake_useragent import UserAgent
import requests
import enum
from typing import Union
import re
from tqdm import tqdm
import pymorphy3
import hashlib
from telegraph import Telegraph
from time import sleep
from dataclasses import dataclass
import urllib.request
from peewee import fn
from fp.fp import FreeProxy
import time
#
from errors import Errors
import config
from tools.logers import setup_logger
import dbs.data_model as data_model
import tools.my_telegraph as my_telegraph
from tools.tg_bot_utils import split_post_text, check_mat_in_text


VOID_CHAR = '⚡️'



class MainParserReturns(enum.Enum):
    Not_defined = -1
    GetVKWallError = -2
    NormalizeDataError = -3

class VkPost():
    # Класс для анализатора постов и обмена данными с парсерами
    def __init__(self, post_id, text, views=0, likes=0, dt=0, hashtags=[], photos=None, text_hash='', url='', url_name=''):
        self.post_id = post_id
        self.text: str = text
        self.views = views
        self.likes = likes
        self.dt = dt
        self.hashtags = hashtags
        if photos==None:
            self.photos = []
        else:
            self.photos = photos
        if (len(self.text) > 1000 and len(self.photos)>0) or (len(self.text) > 4000):
            self.in_telegraph = 1
        else:
            self.in_telegraph = 0
        self.text_hash = text_hash
        self.url = url
        self.url_name = url_name

@dataclass
class ParseParams:
    program_id: int = 0
    task_id: int = 0
    target_ids: int = 0
    target_names: str = ''
    target_url: str = ''
    filter: str = 'all'
    offset: int = 0
    post_count: int = 100
    token: str = ''
    bot_url: str = ''
    reserve_token: str = ''
    to_locate: int = 0
    user_key: int = 0
    min_text_len: int = 500
    telegraph_token: str = ''
    telegraph_author: str = ''
    telegraph_author_url: str = ''
    channel_id: str = ''
    errors_channel_id: str = '' # Канал для отправки отчет об ошибках
    proxy_http: str = ''
    proxy_https: str = ''

class ParserApp():
    def __init__(self, project_config: config.ProjectConfig, params: ParseParams, need_loger=True):
        '''
        Класс парсера
        '''
        # Создаем логер
        self.project_config = project_config
        if need_loger:
            self.log_file_name = project_config.PATH_LOGS + 'parser.log'
            self.loger = setup_logger("ParserLogger", self.log_file_name)
        self.params = params
        #
        self.db_file = project_config.PATH_DBS + project_config.DB_NAME  # Название базы данных
        # Проверяем созда ли база, если нет, то создаем
        if not os.path.isfile(self.db_file):
            try:
                data_model.create_data_model()
                if need_loger:
                    self.loger.info(f'База данных не найдена. Создана новая база: {self.db_file}')
            except Exception as ex:
                if need_loger:
                    self.loger.critical(f'Невозможно создать базу данных: {self.db_file}. Ошибка: {ex}')
        # Подключаемся к телеграф
        try:
            self.telegraph = Telegraph(access_token=params.telegraph_token)
        except Exception as ex:
            self.telegraph = None
            if need_loger:
                self.loger.critical(f'Ошибка подключения к Телеграф: {ex}')


    async def public_post_to_channel(self, bot, post_id=None, random=True, check_text=True):
        # Получаем случайный пост
        #posts_count = data_model.Post.select().count()
        #index = random.randrange(posts_count-1)
        try:
            check_mat = True
            check_mat_num = 0
            while check_mat:
                check_mat_num +=1
                if check_mat_num>200:
                    # if send_report:
                    #     try:
                    #         await bot.send_message(chat_id=self.params.errors_channel_id, text='', parse_mode='HTML')
                    #     except:
                    #         pass
                    return Errors.NoGoodPost
                if random:
                    post_arr = data_model.Post.select().order_by(fn.Random()).limit(1)
                    post = post_arr[0]
                else:
                    try:
                        post = data_model.Post.get_by_id(post_id)
                    except Exception as ex:
                        return Errors.PostNotFound
                post_key = post.get_id()
                post_index = data_model.PostIndex.get_by_id(post_key)
                post_text = post_index.text
                if check_text:
                    check_mat = check_mat_in_text(post_text)
                else:
                    check_mat = False
            img = data_model.get_post_photo(post=post)
            if img != None:
                img_url = img.url
            else:
                img_url = ''
            if len(post_text) >= 2500:
                # Публикуем ссылкой на телеграф
                post_text_lst = split_post_text(post_text, first=True)
                post_text = post_text_lst[0]
                tg_url=post.telegraph_url
                if tg_url != '':
                    post_text = f'{post_text}\n<b><a href="{tg_url}">Показать полностью</a></b>'
                else:
                    author_caption = f'\nБлагодарим за внимание!\nПодписывайтесь на наш <b><a href="{self.params.telegraph_author_url}">телеграм-канал</a></b>.\nЗаходите к нам в <b><a href="{self.params.bot_url}">бот</a></b>.'
                    tg_url= await self.put_post_to_telegraph(post, author_caption=author_caption)
                    if tg_url != '':
                        post_text = f'{post_text}\n<b><a href="{tg_url}">Показать полностью</a></b>'
                        post.telegraph_url=tg_url
                        post.save()
                    else:
                        return Errors.TelegraphError
            elif len(post_text) >= 1020:
                post_text = f'{post_text}\n\nСпасибо за внимание.\n<b>Подписывайтесь на наш канал</b>'
                if img_url != '':
                    post_text = f'{post_text}<a href="{img_url}">.</a>'
                await bot.send_message(chat_id=self.params.channel_id, text=post_text, parse_mode='HTML')
                return Errors.NoError
            if img_url != '':
                await bot.send_photo(chat_id=self.params.channel_id, photo=img_url, caption= post_text, parse_mode='HTML')
            else:
                await bot.send_message(chat_id=self.params.channel_id, text=post_text, parse_mode='HTML')
            return Errors.NoError
        except Exception as ex:
            return ex

    async def put_post_to_telegraph(self, post: Union[data_model.Post, VkPost], author_caption = ''):
        # Создаем страничку в Телеграфе
        tg_url = ''
        formated=False
        if self.telegraph != None:
            # Получаем ссылку на картинку
            if type(post) is data_model.Post:
                photo = data_model.get_post_photo(post)
                if photo == None:
                    photo_url = ''
                else:
                    photo_url = f'<img src="{photo.url}" alt="{photo.caption}">'
            elif type(post) is VkPost:
                try:
                    photo_url = post.photos[0]['url']
                    photo_cap = post.photos[0]['caption']
                    photo_url = f'<img src="{photo_url}" alt="{photo_cap}">'
                except:
                    photo_url = ''
            # Получаем текст
            if type(post) is data_model.Post:
                post_index = data_model.PostIndex.get_by_id(post.text)
                post_text = post_index.text
            elif type(post) is VkPost:
                post_text = post.text
            # Определяем заголовок
            if type(post) is data_model.Post:
                link = self.__get_url_name(post_text, prefix='Продолжение -> ')
                if link == '':
                    title = ''
                else:
                    title = link
            elif type(post) is VkPost:
                title = post.url_name
            if title == '':
                pos = post_text.find('\n')
                if pos == -1 or pos > 100:
                    pos = post_text.find('.')
                if pos != -1 and pos <= 100:
                    title = post_text[:pos]
                    post_text = f'{photo_url} {post_text[pos + 1:]}'
                    post_text = f'{post_text}\n{author_caption}'
                    post_text = my_telegraph.text_to_telegraph_format(post_text)
                    formated = True
                else:
                    # Берем название из хэштэгов
                    if type(post) is data_model.Post:
                        hashtags = data_model.get_post_hashtags_str(post)
                        if hashtags != '':
                            title = hashtags
                        else:
                            title = 'Паста'
                    elif type(post) is VkPost:
                        if len(post.hashtags) > 0:
                            title = post.hashtags[0]
                        else:
                            title = 'Паста'
            else:
                pass
            if not formated:
                post_text = f'{photo_url}\n{post_text}'
                post_text = f'{post_text}\n{author_caption}'
                post_text = my_telegraph.text_to_telegraph_format(post_text)
            try:
                res = self.telegraph.create_page(title, html_content=post_text,
                                                 author_name=self.params.telegraph_author,
                                                 author_url=self.params.telegraph_author_url)
                tg_url = res['url']
            except Exception as ex:
                self.loger.error(f'Не удалось создать страницу в телеграф: {ex}')
                tg_url = ''
        return tg_url

    async def update(self, show_progress=True, use_proxie = True):
        #
        try:
            new_num = 0
            print(f'Обновление начато.')
            if type(self.params.target_ids) is list:
                target_ids = self.params.target_ids
            else:
                target_ids = []
                target_ids.append(self.params.target_ids)
            for target_id in target_ids:
                # Получаем количество постов в группе
                tmp = self.params.post_count
                try:
                    self.params.post_count = 1
                    group_info = self.__get_vk_wall(target_id, use_proxie)
                    if group_info == None:
                        continue
                    self.params.post_count = tmp
                    post_count = group_info['response']['count']
                    self.params.offset = 0
                except:
                    self.params.post_count = tmp
                    post_count = 100000
                    self.params.offset = 0
                if show_progress:
                    rng = tqdm(range(0, post_count, self.params.post_count), colour='green', desc='Выгружаем данные')
                else:
                    rng = range(0, post_count, self.params.post_count)
                for posts_got in rng:
                    # Парсим
                    #start = time.time()
                    post_src = self.__parse(target_id, use_proxie=use_proxie)
                    if type(post_src) is MainParserReturns:
                        self.loger.error(f'Ошибка получения записей со стены ВК: {post_src}')
                        continue
                    #end = time.time()
                    #print(f'\nВремя операции - {end - start} сек.')
                    posts = self.__analysis_posts(post_src, target_id)
                    if len(posts) == 0:
                        break # Если ничего подходящего в 100 записях нет, дальше можно не искать
                    new_num=new_num+len(posts)
                    self.__save_posts(posts, target_id)
            print(f'Обновление завершено. Добавлено {new_num} записей.')
            return Errors.NoError
        except Exception as ex:
            return ex


    def __parse(self, target_id: int, use_proxie = True):
        # Полуаем стену из Вконтакте
        json_data = self.__get_vk_wall(target_id, use_proxie)
        if json_data != None:
            pass
        else:
            return MainParserReturns.GetVKWallError
        # Преобразовываем данные в стандартный формат и отправляем в исполнителю
        result = self.__normalize_data(json_data)
        return result


    def __get_vk_wall(self, target_id: int, use_proxie = True):
        '''
        Получение записей со стены, используя внутренее API ВК
        '''
        try:
            proxie_not_got = True
            proxies = {}
            px_tries = 0
            if use_proxie:
                while proxie_not_got:
                    try:
                        proxy_obj = FreeProxy(anonym=True, https=True).get()
                        proxie_not_got = False
                        proxies = {
                            "https": proxy_obj,
                        }
                    except:
                        px_tries += 1
                        if px_tries < 10:
                            pass
                            #print('Доступные прокси отсутствуют. Ждем.')
                        else:
                            #print('Обновление не удалось, доступные прокси отсутствуют.')
                            self.loger.warning('Обновление не удалось, доступные прокси отсутствуют.')
                            return None
                        sleep(30)
            #proxies=urllib.request.getproxies()
            url = f"https://api.vk.com/method/wall.get?owner_id={target_id}&offset={self.params.offset}&count={self.params.post_count}&filter={self.params.filter}&access_token={self.params.token}&v=5.131"
            ua = UserAgent()
            header = {'User-Agent': str(ua.random)}
            req = requests.get(url, headers=header, proxies=proxies)
            if req.status_code != 200:
                url = f"https://api.vk.com/method/wall.get?owner_id={target_id}&offset={self.params.offset}&count={self.params.post_count}&filter={self.params.filter}&access_token={self.params.reserve_token}&v=5.131"
                req = requests.get(url, headers=header, proxies=proxies)
            # print(req.text)
            if req.status_code != 200:
                # error = service_func.check_error_code_in_json(req)
                self.loger.error(
                    f'Парсер: VKParser (target_id={target_id}, filter={filter}) ошибка парсинга:'
                    f' код requests - {req.status_code}')
                return None
            else:
                res = req.json()
                try:
                    self.params.offset = int(res['response']['next_from'])
                except:
                    pass
                return res
        except Exception as ex:
            self.loger.error(
                f'Парсер VKParser (target_id={target_id}, filter={filter}) ошибка парсинга: {ex}')
            return None

    def __normalize_data(self, json_data) -> Union[list[VkPost], MainParserReturns]:
        '''
        Приводит спарсеные данные в стандартизированную форму
        :param json_data:
        :param task_id:
        :return:
        '''
        try:
            res = []
            if "response" not in json_data:
                err_str = f'Ошибка при выполнении normalize_data(task_key={self.params.task_id}): "в данных нет ключа [response]"'
                self.loger.error(err_str)
                return MainParserReturns.NormalizeDataError
            # Просматриваем все посты
            post_num = 0
            for i, post in enumerate(json_data['response']['items']):
                try:  # Если закрепленный пост то пропускаем его
                    pinned = post['is_pinned']
                    if pinned == True:
                        continue
                except:
                    try:
                        post_id = post['id']
                        try:
                            text = post['text']
                            text = text.strip()
                            text = self.__del_forbiden_tg_char(text)
                        except:
                            text = VOID_CHAR
                        try:
                            post_datetime = post['date']
                        except:
                            post_datetime = 0
                        try:
                            views_count = post['views']['count']
                        except:
                            views_count = 0
                        try:
                            likes_count = post['likes']['count']
                        except:
                            likes_count = 0
                        try:  # Если репост
                            repost_text = post['copy_history'][0]['text']
                            repost_text = self.__del_forbiden_tg_char(repost_text)
                            text = str(text) + str(repost_text)
                            post = post['copy_history'][0]
                        except Exception as ex:
                            pass
                        if text == '': text = VOID_CHAR
                        hashtags = self.__get_hashtags(text)
                        # Лематизируем хэштеги
                        # hashtags=self.__lematize_words(hashtags)
                        #hash = hashlib.md5(text.encode('utf-8'))
                        #text_hash = hash.hexdigest()
                        post_src = VkPost(post_id, text, views_count, likes_count, post_datetime, hashtags, text_hash='')
                        # Работаем с медиафайлами
                        if "attachments" in post:
                            attachments = post["attachments"]
                            for src in attachments:
                                if 'type' in src:
                                    match src['type']:
                                        case 'photo':
                                            try:
                                                max_size = len(src['photo']['sizes']) - 1
                                            except:
                                                max_size = 0
                                            if max_size < 0: max_size = 0
                                            photo_text = src['photo']['text']
                                            photo = {}
                                            photo['url'] = src['photo']['sizes'][max_size]['url']
                                            photo['caption'] = photo_text
                                            post_src.photos.append(photo)
                                        case 'link':
                                            try:
                                                try:
                                                    max_size = len(src['link']['photo']['sizes']) - 1
                                                except:
                                                    max_size = 0
                                                if max_size < 0: max_size = 0
                                                photo_text = src['link']['photo']['text']
                                                photo = {}
                                                photo['url'] = src['link']['photo']['sizes'][max_size]['url']
                                                photo['caption'] = photo_text
                                                post_src.photos.append(photo)
                                            except:
                                                pass
                                            try:
                                                title = src['link']['title']
                                                url = src['link']['url']
                                                #post_src.text = f'{post_src.text}\n<a href="{url}">{title}</a>'
                                                post_src.url = f'<a href="{url}">Продолжение -> {title}</a>'
                                                post_src.url_name = title
                                            except:
                                                pass
                        res.append(post_src)
                        post_num = post_num + 1
                    except Exception as ex:
                        self.loger.error(f'Ошибка нормализации данных. Номер поста: {post_id}. Ошибка: {ex}')
                        continue
            return res
        except Exception as ex:
            self.loger.error(f'Ошибка нормализации данных. Ошибка: {ex}')
            return MainParserReturns.NormalizeDataError


    def __analysis_posts(self, posts: list[VkPost], target_id: int) -> list[VkPost]:
        '''
        Выбираем из спарсеного массива постов те, которые соответсвют заданным критериям задачи
        '''
        res=[]
        for i, post in enumerate(posts):
            # Анализируем длинну текста
            if len(post.text) < self.params.min_text_len:
                 continue
            # Если в тексте есть ссылки то тоже пропускаем
            if not self.__check_text(post.text):
                continue
            # Добавляем безопасные ссылки
            if post.url != '':
                post.text=f'{post.text}\n{post.url}'
            # Проверяем чтобы уже добавленые посты не добавлялись
            post_ex = data_model.get_post(post.post_id, target_id)
            if post_ex!=None:
                continue
            # Удаляем внутренние ссылки ВК
            posts[i].text=re.sub(r'\[.+?\]\s', '', post.text)
            #posts[i].text = 'Test'
            # Проверяем текст на уникальность по хэшу
            hash = hashlib.md5(posts[i].text.encode('utf-8'))
            hash_str = hash.hexdigest()
            post_ex = data_model.get_post(text_hash=hash_str)
            if post_ex != None:
                continue
            posts[i].text_hash=hash_str
            res.append(post)
        return res

    def __save_posts(self, posts: list[VkPost], target_id: int):
        '''
        Сохраняем посты в базу
        :param posts:
        :return:
        '''
        try:
            for post in posts:
                tg_url =''
                # Сохраняем текст
                post_index = data_model.PostIndex.create(text=post.text)
                post_index.save()
                post_index_id=post_index.get_id()
                post_obj = data_model.Post.create(post_id=post.post_id, source_id=target_id, text=post_index_id, views=0, old_views=post.views,
                                           likes=post.likes, dt=post.dt, in_telegraph=post.in_telegraph, telegraph_url=tg_url, text_hash=post.text_hash)
                post_obj.save()
                # Сохраняем хэштеги
                for hashtag in post.hashtags:
                    # Проверяем существует ли такой хэштег
                    hashtag_obj = data_model.get_hashtag(hashtag)
                    if hashtag_obj == None:
                        hashtag_obj = data_model.Hashtag.create(value=hashtag)
                        hashtag_obj.save()
                    post_hashtag = data_model.Post_Hashtag.create(post=post_obj, hashtag=hashtag_obj)
                    post_hashtag.save()
                # Сохраняем картинки
                for photo in post.photos:
                    photo_obj = data_model.Photo.create(owner_id=post_obj, caption=photo['caption'], url=photo['url'])
                    photo_obj.save()
            return Errors.NoError
        except Exception as ex:
            return Errors.PyError

    def get_vk_object_id(self, vk_object_name: str):
        urls = []
        urls.append(
            f"https://api.vk.com/method/utils.resolveScreenName?screen_name={vk_object_name}&access_token={self.params.token}&v=5.131")
        urls.append(
            f"https://api.vk.com/method/utils.resolveScreenName?screen_name={vk_object_name}&access_token={self.params.reserve_token}&v=5.131")
        ua = UserAgent()
        header = {'User-Agent': str(ua.random)}
        for url in urls:
            page = requests.get(url, headers=header)
            res = page.json()
            try:
                vk_group_id = res['response']['object_id']
                return vk_group_id
            except:
                # Если ошибка пробуем с резервным токеном
                continue
        return None


    def get_vk_group_info(self, vk_group_id):
        urls = []
        urls.append(
            f"https://api.vk.com/method/groups.getById?group_id={vk_group_id}&fields=description,members_count&access_token={self.params.token}&v=5.131")
        urls.append(
            f"https://api.vk.com/method/groups.getById?group_id={vk_group_id}&fields=description,members_count&access_token={self.params.reserve_token}&v=5.131")
        ua = UserAgent()
        header = {'User-Agent': str(ua.random)}
        for url in urls:
            req_gr_info = requests.get(url, headers=header)
            gr_info = req_gr_info.json()
            try:
                res={}
                res['name'] = gr_info['response'][0]['name']
                res['description'] = gr_info['response'][0]['description']
                res['members_count'] = gr_info['response'][0]['members_count']
                return res
            except:
                continue
        return None


    def get_vk_user_info(self, vk_user_id):
        urls = []
        urls.append(
            f"https://api.vk.com/method/users.get?user_ids={vk_user_id}&access_token={self.params.token}&v=5.131")
        urls.append(
            f"https://api.vk.com/method/users.get?user_ids={vk_user_id}&access_token={self.params.reserve_token}&v=5.131")
        ua = UserAgent()
        header = {'User-Agent': str(ua.random)}
        for url in urls:
            req_user_info = requests.get(url, headers=header)
            user_info = req_user_info.json()
            try:
                res={}
                res['first_name'] = user_info['response'][0]['first_name']
                res['last_name'] = user_info['response'][0]['last_name']
                return res
            except:
                continue
        return None

    def __del_forbiden_tg_char(self, oldstr: str):
        newstr = oldstr.replace("'", "")
        newstr = newstr.replace("|", "")
        newstr = newstr.replace(">", "")
        newstr = newstr.replace("<", "")
        return newstr

    def __get_hashtags(self, text: str) -> list:
        pat = re.compile(r"#(\w+)")
        res = pat.findall(text)
        return res

    def __lematize_words(self, words: list[str]) -> list[str]:
        morph = pymorphy3.MorphAnalyzer()
        res = []
        for word in words:
            norm_word = morph.parse(word)
            res.append(norm_word[0].normal_form)
        return res

    def __check_text(self, text: str) -> bool:
        res = True
        if text.find('https:') != -1 or text.find('http:') != -1 or text.find('www.') != -1 or \
        text.find('.com') != -1 or text.find('.ru') != -1 or text.find('club') != -1:
            res = False
        return res

    def __get_url_name(self, text: str, prefix: str = ''):
        if prefix != '':
            pos_start = text.find(prefix)
            pos_end = text.find('</a>', pos_start)
            if pos_start != -1 and pos_end != -1:
                res = text[pos_start + len(prefix):pos_end]
            else:
                res = ''
        else:
            pos_start = text.find('<a href="')
            pos_end = text.find('">', pos_start)
            if pos_start!= -1 and pos_end!= -1:
                res = text[pos_start + len('<a href="'):pos_end]
            else:
                res = ''
        return res





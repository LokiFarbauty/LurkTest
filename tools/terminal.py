import datetime
import config
import os
from time import sleep
from aioconsole import ainput
from telegraph import Telegraph
#
from errors import Errors
from dbs import data_model


err_no_parametrs='не указаны требуемые параметры'

async def console(args):
    first = True
    while True:
        try:
            sleep(1)
            if first:
                print('Терминал активен, можно вводить команды:')
                parser_obj = args['parser_obj']
                bot = args['bot']
                first = False
            inp = await ainput('>>> ')
            dt_now = datetime.datetime.now()
            #dt_now = dt_now.replace(hour=0, minute=0, second=0, microsecond=0)
            dt_now = dt_now.replace(microsecond=0)
            dt_now = dt_now.timestamp()
            n = inp.find('->')
            pars = ''
            if n == -1:
                command = inp
                args=[]
            else:
                args = []
                command = inp[:n]
                command = command.lower()
                pars = inp[n + 2:]
                args0=pars.split(',')
                for el in args0:
                    args.append(el.strip())
            command = command.strip()
            if command=='exit':
                os._exit(0)
            elif (command=='create_db' or command=='create_dm'):
                # Команда создает либо обновляет базу данных для парсера Вконтакте
                try:
                    data_model.create_data_model()
                    print('Модель данных создана.')
                except Exception as ex:
                    print(f'Ошибка: {ex}')
                pass
            elif command=='update':
                await parser_obj.update(use_proxie=False)
            elif command=='public_post':
                if len(args) > 0:
                    err = await parser_obj.public_post_to_channel(bot, post_id=args[0], random=False)
                    print(err)
                else:
                    print(f'Ошибка: {err_no_parametrs}')
            elif command=='delete_post':
                if len(args) > 0:
                    try:
                        post = data_model.Post.get_by_id(args[0])
                        # post_index = data_model.PostIndex.get_by_id(args[0])
                        if post != None:
                            # Удаляем у пользователей из последних
                            users = data_model.User.update(last_post_read=None).where(data_model.User.last_post_read==args[0])
                            users.execute()
                            # Удаляем картинки
                            photos = data_model.Photo.delete().where(data_model.Photo.owner == post)
                            photos.execute()
                            # Удаляем хэштэги
                            hashtags = data_model.Post_Hashtag.delete().where(data_model.Post_Hashtag.post == post)
                            hashtags.execute()
                            # Удаляем пост из избранного пользователей
                            user_favorites = data_model.User_Post.delete().where(data_model.User_Post.post == post)
                            user_favorites.execute()
                            # Удаляем пост и текст
                            data_model.PostIndex.delete_by_id(args[0])
                            data_model.Post.delete_by_id(args[0])
                            print('Пост удален')
                        else:
                            print('Пост не найден')
                    except Exception as ex:
                        print(ex)
                else:
                    print(f'Ошибка: {err_no_parametrs}')
            elif command=='public_random_post':
                err = await parser_obj.public_post_to_channel(bot)
                print(err)
            elif command=='telegraph_create_account':
                if len(args) > 2:
                    telegraph = Telegraph()
                    #res = telegraph.create_account(short_name='Lurk Alive', author_name='MyLurkoBot', author_url='t.me/my_lurk_alive')
                    try:
                        res = telegraph.create_account(short_name=args[0], author_name=args[1],
                                                   author_url=args[2])
                        print(res)
                    except Exception as ex:
                        print(ex)
                else:
                    print(f'Ошибка: {err_no_parametrs}')
                pass
            elif command=='vk_get_object_id':
                # Команда возвращает id объекта по его имени
                if len(args) > 0:
                    try:
                        res=parser_obj.get_vk_object_id(args[0])
                    except Exception as ex:
                        res = ex
                    print(res)
                else:
                    print(f'Ошибка: {err_no_parametrs}')
                pass
            elif command=='vk_get_group_info':
                # Команда возвращает информацию о группе по id
                if len(args) > 0:
                    res=parser_obj.get_vk_group_info(args[0])
                    print(res)
                else:
                    print(f'Ошибка: {err_no_parametrs}')
                pass
            elif command=='vk_get_user_info':
                # Команда возвращает информацию о пользователе по id
                if len(args) > 0:
                    res=parser_obj.get_vk_user_info(args[0])
                    print(res)
                else:
                    print(f'Ошибка: {err_no_parametrs}')
                pass
            elif command=='clear_db':
                # Команда очищает базу данных
                try:
                    data_model.Photo.delete().execute()
                    data_model.Post_Hashtag.delete().execute()
                    data_model.Hashtag.delete().execute()
                    data_model.Post.delete().execute()
                    print('База успешно очищена')
                except Exception as ex:
                    print(f'Ошибка: {ex}')
                pass
            else:
                print('Неправильная команда')
        except (KeyboardInterrupt, SystemExit):
            break

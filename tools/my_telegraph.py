

def text_to_telegraph_format(text: str) -> str:
    '''Функция заменяет абзацы \n на html параграфы'''
    res_text = ''
    pos = text.find('\n')
    if pos != -1:
        par_start = text[:pos].strip()
        res_text = f'{res_text}<p>{par_start}</p>\n'
    else:
        return f'<p>{text}</p>'
    while pos != -1:
        # ищем следующий перенос
        pos_end = text.find('\n', pos + 1)
        if pos_end == -1:
            # Больше переносов нет
            par = text[pos + 1:]
        else:
            par = text[pos + 1:pos_end]
        # закидываем параграф в текст
        par = par.strip()
        if par != '':
            res_text = f'{res_text}<p>{par}</p>\n'
        pos = pos_end
    return res_text

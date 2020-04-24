from os import path, listdir

import yaml
from flask import url_for, render_template


def get_user_content_right():
    result_html = ''
    file_list = listdir(path.join(path.dirname(__file__), 'static', 'user'))
    for file_name in sorted(file_list):
        if file_name.endswith('.yaml'):
            with open(path.join(path.dirname(__file__), 'static', 'user', file_name), mode='r') as f:
                item = yaml.full_load(f)

            if 'title' in item:
                title_style = []
                if 'background' in item['title']:
                    bg = item['title']['background']
                    if 'color' in bg:
                        title_style.append('background-color:' + bg['color'])
                    if 'image' in bg:
                        title_style.append('background-image:url(' + url_for('static', filename='user/' + bg['image']) + ')')
                        title_style.append('background-repeat:no-repeat')
                    if 'size' in bg:
                        title_style.append('background-size:' + bg['size'])
                    if 'pos-x' in bg:
                        title_style.append('background-position-x:' + bg['pos-x'])
                    if 'pos-y' in bg:
                        title_style.append('background-position-y:' + bg['pos-y'])
                if 'color' in item['title']:
                    title_style.append('color:' + item['title']['color'])
                if 'height' in item['title']:
                    title_style.append('height:' + item['title']['height'])
                title_style = ';'.join(title_style)

            result_html += render_template('user_block.html', **item, title_style=title_style)

    return result_html

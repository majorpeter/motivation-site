from os import path, listdir

import yaml
from flask import url_for, render_template


def _parse_title_style(item):
    title_style = []
    if 'background' in item:
        for key, css_prop in {
            'color': 'background-color',
            'size': 'background-size',
            'pos-x': 'background-position-x',
            'pos-y': 'background-position-y',
        }.items():
            if key in item['background']:
                title_style.append(css_prop + ':' + item['background'][key])
        if 'image' in item['background']:
            title_style.append('background-image:url(' + url_for('static', filename='user/' + item['background']['image']) + ')')
            title_style.append('background-repeat:no-repeat')
    for key, css_prop in {
        'color': 'color',
        'height': 'height',
    }.items():
        if key in item:
            title_style.append(css_prop + ':' + item[key])
    return ';'.join(title_style)


def get_user_content_right():
    result_html = ''
    file_list = listdir(path.join(path.dirname(__file__), 'static', 'user'))
    for file_name in sorted(file_list):
        if file_name.endswith('.yaml'):
            with open(path.join(path.dirname(__file__), 'static', 'user', file_name), mode='r') as f:
                item = yaml.full_load(f)

            title_style = _parse_title_style(item['title']) if 'title' in item else ''
            result_html += render_template('user_block.html', **item, title_style=title_style)

    return result_html

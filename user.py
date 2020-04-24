from os import path, listdir

import yaml
from flask import url_for


def get_user_content_right():
    result_html = ''
    file_list = listdir(path.join(path.dirname(__file__), 'static', 'user'))
    for file_name in sorted(file_list):
        if file_name.endswith('.yaml'):
            with open(path.join(path.dirname(__file__), 'static', 'user', file_name), mode='r') as f:
                item = yaml.full_load(f)

            result_html += '<div class="mdl-color--white mdl-shadow--2dp">'
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

                result_html += '<div class="mdl-card__title mdl-card--expand" style="' + title_style + '">' \
                  '<h2 class="mdl-card__title-text">' + item['title']['text'] + '</h2>' \
                  '</div><div class="mdl-card__supporting-text mdl-color-text--grey-600">'
            result_html += item['content']
            result_html += '</div>'
            if 'actions' in item:
                result_html += '<div class="mdl-card__actions mdl-card--border">'
                for action in item['actions']:
                    result_html += '<a href="' + action['url'] + '" class="mdl-button mdl-js-button mdl-js-ripple-effect" data-upgraded=",MaterialButton,MaterialRipple" target="_blank">' + action['text'] + '<span class="mdl-button__ripple-container"><span class="mdl-ripple"></span></span></a>'
                result_html += '</div>'
            result_html += '</div>'
    return result_html

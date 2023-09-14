from collections import namedtuple
from datetime import datetime, timezone
from threading import Lock

import caldav
import re
import time

from flask import render_template


class Todos:
    class Item(namedtuple('Item', ['summary', 'description', 'priority', 'sort_order', 'due'])):
        @staticmethod
        def format_content(s: str) -> str:
            return re.sub(r'^<([A-Z-]+\{.*})', '', re.sub(r'>$', '', s))

        @staticmethod
        def from_vobject(task: caldav.Todo):
            summary = None
            description = None
            priority = None
            sort_order = None
            due = None

            for child in task.vobject_instance.getChildren():
                if child.name == 'VTODO':
                    if 'x-apple-sort-order' in child.contents:
                        sort_order = int(Todos.Item.format_content(str(child.contents['x-apple-sort-order'][0])))
                    else:
                        # generate sort order the same way as NextCloud Tasks
                        # @see https://github.com/nextcloud/tasks/blob/bec28f9b54bda16c720591350920abba85d9fdf3/src/models/task.js#L657
                        if 'created' not in child.contents:
                            sort_order = 0
                        else:
                            created = datetime.fromisoformat(Todos.Item.format_content(str(child.contents['created'][0])))
                            sort_order = int((created.astimezone(timezone.utc) - datetime(2001, 1, 1, 0, 0, 0, tzinfo=timezone.utc)).total_seconds())

                    summary = Todos.Item.format_content(str(child.summary))
                    if 'description' in child.contents:
                        description = Todos.Item.format_content(str(child.description))
                    if 'due' in child.contents:
                        due = datetime.fromisoformat(Todos.Item.format_content(str(child.due)))
                    if 'priority' in child.contents:
                        priority = int(Todos.Item.format_content(str(child.contents['priority'][0])))
                    else:
                        priority = 10

            return Todos.Item(summary, description, priority, sort_order, due)

        @property
        def past_due(self):
            return self.due is not None and self.due.timestamp() < time.time()

        @property
        def due_string(self):
            if not self.due:
                return ''
            if self.due.hour == 0 and self.due.minute == 0:
                return self.due.strftime('%Y-%m-%d')  #TODO config
            return self.due.strftime('%Y-%m-%d %H:%M')

    def __init__(self, config):
        self._todos = []
        self._update_lock = Lock()
        self._fetch_time = None

        # set up the connection to the Nextcloud server
        url = config['protocol'] + '://' + config['hostname'] + '/remote.php/dav/calendars/' + config['login']
        client = caldav.DAVClient(url, username=config['login'], password=config['password'])
        self._calendar = client.calendar(url=url+'/' + config['calendar_name'] + '/')

        self._edit_url = config['protocol'] + '://' + config['hostname'] + '/index.php/apps/tasks/#/calendars/' + config['calendar_name']

    def _update(self):
        def _sort_function(x: Todos.Item) -> str:
            """
            sort by due date first (if present)
            otherwise sort by priority and then by summary
            """
            if x.due:
                return x.due_string
            return ('%x' % x.priority) + x.summary

        todos = []
        for task in self._calendar.todos():
            todos.append(Todos.Item.from_vobject(task))
        todos = sorted(todos, key=_sort_function)
        self._todos = todos
        self._fetch_time = time.localtime()

    def is_cache_up_to_date(self, max_age=600):
        if self._fetch_time is None:
            return False
        if time.mktime(time.localtime()) - time.mktime(self._fetch_time) > max_age:
            return False
        return True

    def _get_or_update(self):
        with self._update_lock:
            if self.is_cache_up_to_date():
                return self._todos

            self._update()
            return self._todos

    def render_layout(self):
        return render_template('todos.html', todos=self._todos, edit_url=self._edit_url, need_update=not self.is_cache_up_to_date())

    def render_content(self):
        return render_template('todos_content.html', todos=self._get_or_update())

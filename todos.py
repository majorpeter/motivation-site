from collections import namedtuple
from datetime import datetime, timezone

import caldav
import re

from flask import render_template


class Todos:
    class Item(namedtuple('Item', ['summary', 'description', 'sort_order', 'due'])):
        @staticmethod
        def format_content(s: str) -> str:
            return re.sub(r'^<([A-Z-]+\{.*})', '', re.sub(r'>$', '', s))

        @staticmethod
        def from_vobject(task: caldav.Todo):
            summary = None
            description = None
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
                            sort_order = int((created - datetime(2001, 1, 1, 0, 0, 0, tzinfo=timezone.utc)).total_seconds())

                    summary = Todos.Item.format_content(str(child.summary))
                    if 'description' in child.contents:
                        description = Todos.Item.format_content(str(child.description))
                    if 'due' in child.contents:
                        due = Todos.Item.format_content(str(child.due))

            return Todos.Item(summary, description, sort_order, due)

    def __init__(self, config):
        self._todos = []

        # set up the connection to the Nextcloud server
        url = config['dav']['protocol'] + '://' + config['dav']['hostname'] + '/remote.php/dav/calendars/' + config['dav']['login']
        client = caldav.DAVClient(url, username=config['dav']['login'], password=config['dav']['password'])
        self._calendar = client.calendar(url=url+'/personal/')

        self.update()  # TODO

    def update(self):
        todos = []
        for task in self._calendar.todos():
            todos.append(Todos.Item.from_vobject(task))
        todos = sorted(todos, key=lambda x: x.sort_order)
        self._todos = todos

    def render_layout(self):
        return render_template('todos.html', todos=self._todos)

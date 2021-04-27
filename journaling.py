import io
from datetime import datetime, date

import easywebdav2
from flask import render_template


class Journaling:
    REQUIRED = 3

    def __init__(self, config):
        self._config = config
        self._modified_date = None
        self._journal = ''
        self._client = easywebdav2.Client(self._config['dav']['hostname'], protocol=config['dav']['protocol'],
                                         username=self._config['dav']['login'],
                                         password=self._config['dav']['password'])
        self._fetch_journal()

    def _fetch_journal(self):
        buffer = io.BytesIO()
        self._client.download(remote_path=self._config['dav']['baseurl'] + self._config['dav']['path'],
                              local_path_or_fileobj=buffer)
        self._journal = buffer.getvalue().decode('utf8')

    def _save_journal(self):
        buffer = io.BytesIO(self._journal.encode('utf8'))
        self._client.upload(remote_path=self._config['dav']['baseurl'] + self._config['dav']['path'],
                            local_path_or_fileobj=buffer)
        self._modified_date = None

    @property
    def days(self):
        result = []
        for line in self._journal.split('\n'):
            if line.startswith(self._config['day_prefix']):
                date = datetime.strptime(line[len(self._config['day_prefix']):], self._config['date_format']).date()
                result.append(date)
        return result

    @property
    def entries_for_today(self):
        return self.get_entries_for_day(date.today(), strip_listing=True)

    @entries_for_today.setter
    def entries_for_today(self, entries):
        self.set_entries_for_day(date.today(), entries, prepend_listing=True)

    def get_entries_for_day(self, day: date, strip_listing: bool):
        in_day = False
        result = []
        for line in self._journal.split('\n'):
            if line.startswith(self._config['day_prefix']):
                found_day = datetime.strptime(line[len(self._config['day_prefix']):], self._config['date_format']).date()
                if found_day == day:
                    in_day = True
                elif in_day:
                    break
            elif in_day:
                if len(line) == 0:
                    continue
                if strip_listing and line.startswith('* '):
                    line = line[2:]
                result.append(line)
        return result

    def __create_day_entry(self, day: date, content: list, prepend_listing: bool):
        if prepend_listing:
            content = ['* ' + item for item in content]
        return '\n'.join([self._config['day_prefix'] + date.strftime(day, self._config['date_format'])] + content + ['', ''])

    def set_entries_for_day(self, day: date, content: list, prepend_listing: bool):
        day_inserted = False
        in_day = False
        result = ''
        for line in self._journal.split('\n'):
            if line.startswith(self._config['day_prefix']):
                found_day = datetime.strptime(line[len(self._config['day_prefix']):], self._config['date_format']).date()
                if found_day == day:
                    in_day = True
                else:
                    if not day_inserted and found_day < day:
                        result += self.__create_day_entry(day, content, prepend_listing)
                        day_inserted = True
                    result += line + '\n'
                    in_day = False
            elif not in_day:
                result += line + '\n'
        if not day_inserted:
            result += self.__create_day_entry(day, content, prepend_listing)
        self._journal = result[:-1]  # drop last new line char
        self._save_journal()

    def render_journal(self, update_from_server=False):
        if update_from_server:
            self._fetch_journal()
        return render_template('journaling.html', **self.get_journal_data())

    def get_journal_data(self):
        entries = self.entries_for_today
        done_percent = int(len(entries) / Journaling.REQUIRED * 100)
        color = '#ff4242'
        if len(entries) >= Journaling.REQUIRED:
            color = '#7ed67e'
        elif len(entries) > 0:
            color = '#fb962c'
        return {'entries': entries, 'done_percent': done_percent, 'color': color}

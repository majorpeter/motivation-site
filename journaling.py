import io
from datetime import datetime, date

from webdav3.client import Client as WebDavClient


class Journaling:
    def __init__(self, config):
        self._config = config
        self._modified_date = None
        self._journal = ''
        self._client = WebDavClient({
            'webdav_hostname': self._config['dav']['hostname'],
            'webdav_login': self._config['dav']['login'],
            'webdav_password': self._config['dav']['password']
        })
        self._fetch_journal()
        print(self.entries_for_today)

    def _fetch_journal(self):
        modified_date = self._client.info(self._config['dav']['path'])['modified']
        if self._modified_date != modified_date:
            buffer = io.BytesIO()
            self._client.download_from(buffer, remote_path=self._config['dav']['path'])
            self._journal = buffer.getvalue().decode('utf8')
            self._modified_date = modified_date

    def _save_journal(self):
        buffer = io.BytesIO(self._journal.encode('utf8'))
        self._client.upload_to(buffer, remote_path=self._config['dav']['path'])
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

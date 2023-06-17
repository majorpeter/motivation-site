from flask import render_template


class Audio:
    def __init__(self, config):
        self._config = config

    def render_layout(self):
        return render_template('audio.html', url=self._config['src'], autoplay=self._config['autoplay'])

from flask import render_template


class WeatherWidget:
    def __init__(self, config):
        self._config = config

    def render_layout(self):
        return render_template('weather.html', location=self._config['location'], label=self._config['label'], lang=self._config['lang'])

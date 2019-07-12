# coding: utf-8


class Config(object):
    DEBUG = False

    API_HOST = 'api.tracker.yandex.net'
    API_VER = '2'

    @property
    def api_protocol(self):
        return 'http' if Config.DEBUG else 'https'

    @property
    def api_url(self):
        return '{protocol}://{host}/v{ver}'.format(
            protocol=self.api_protocol, host=Config.API_HOST,
            ver=Config.API_VER)


config = Config()

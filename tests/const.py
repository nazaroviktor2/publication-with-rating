from conf.config import settings

API_PREFIX = settings.API_PREFIX + settings.API_V1_PREFIX

URLS = {
    'api': {
        'v1': {
            'auth': {
                'registration': API_PREFIX + '/auth/registration',
                'token': API_PREFIX + '/auth/token',
            },
            'publication': {
                'publication': API_PREFIX + '/publication',
                'vote': API_PREFIX + '/publication/{publication_id}/vote',
            },
            'vote': {'vote': API_PREFIX + '/vote'},
        },
    },
}

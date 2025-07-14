import os

import requests

user_cache = []

POCKET_API_KEY = os.environ.get('POCKET_API_KEY', 'default_pocket_api_key')
POCKET_API_URL_BASE = os.environ.get('POCKET_API_URL_BASE', 'https://pocket.site.de/api/')


def get_pocket_users():
    page = 1
    users = []

    while True:
        res = requests.get(
            POCKET_API_URL_BASE + 'users',
            headers={'X-API-KEY': POCKET_API_KEY, 'Accept': 'application/json'},
            params={'page': page}
        )
        if res.status_code != 200:
            raise Exception(f"Failed to fetch users: {res.status_code} {res.text}")

        data = res.json()
        users.extend(data.get('data', []))

        if page >= data['pagination']['totalPages']:
            break
        page += 1
    return users


def update_user_cache():
    global user_cache
    user_cache = get_pocket_users()

def get_users_from_cache():
    global user_cache
    if user_cache is None or len(user_cache) == 0:
        update_user_cache()
    return user_cache

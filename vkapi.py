from urllib.parse import urlencode

OAUTH_URL = 'https://oauth.vk.com/authorize'
OAUTH_PARAMS = {
    'client_id': 7242321,
    # 'redirect_uri': '',
    'display': 'page',
    'response_type': 'token',
    'scope': 'status' 'groups' 'friends'
}

print('?'.join(
    (OAUTH_URL, urlencode(OAUTH_PARAMS))
))

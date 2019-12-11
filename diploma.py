import json
import time
import requests


class UserVk(object):
    id = None
    friends = []
    groups = []
    Access_Token = '12f6bc7dd84d6c50c2a938b3192ca6c8e82c3d66501499d74ebaf7f4463d4a58ce0f491efa76d9b5f52ca'
    version_api = '5.103'

    def __init__(self, user_name):
        response = requests.get('https://api.vk.com/method/users.get', {
            'user_ids': user_name,
            'access_token': self.Access_Token,
            'v': self.version_api
        })
        try:
            self.id = response.json()['response'][0]['id']
        except KeyError:
            self.id = None
        else:
            self.get_friends()
            self.get_groups()

    def get_friends(self):
        response = requests.get('https://api.vk.com/method/friends.get', {
            'user_id': self.id,
            'access_token': self.Access_Token,
            'v': self.version_api
        })
        self.friends = response.json()['response']['items']

    def get_groups(self):
        response = requests.get('https://api.vk.com/method/groups.get', {
            'user_id': self.id,
            'access_token': self.Access_Token,
            'v': self.version_api
        })
        self.groups = response.json()['response']['items']


class GroupVk(object):
    gid = None
    name = ''
    count = 0
    members = []
    access_token = '12f6bc7dd84d6c50c2a938b3192ca6c8e82c3d66501499d74ebaf7f4463d4a58ce0f491efa76d9b5f52ca'
    version_api = '5.103'

    def __init__(self, gid):
        self.gid = gid
        self.get_members()

    def get_members(self):
        response = requests.get('https://api.vk.com/method/groups.getMembers', {
            'group_id': self.gid,
            'access_token': self.access_token,
            'v': self.version_api
        })
        self.members = response.json()['response']['items']
        self.count = response.json()['response']['count']

    def get_group_name(self):
        response = requests.get('https://api.vk.com/method/groups.getById', {
            'group_ids': self.gid,
            'access_token': self.access_token,
            'v': self.version_api
        })
        self.name = response.json()['response'][0]['name']


def get_user():
    while True:
        user_name = input('Введите имя или id пользователя ВКонтакте: ')
        user_vk = UserVk(user_name)
        if user_vk.id:
            if user_vk.friends and user_vk.groups:
                break
            else:
                if not user_vk.friends:
                    print('Не найдены друзья пользователя')
                if not user_vk.groups:
                    print('Пользователь не состоит в группах')
        else:
            print('Ошибка, пользователь с таким именем во ВКонтакте не найден')
    # print('Данные пользователя ВК получены')
    return user_vk


def check_groups_for_friends(user_vk):
    group_count = len(user_vk.groups)
    print('Количество групп в которых состоит пользователь: {}'.format(group_count))
    print('Проверяем группы пользователя на наличие друзей:')
    private_groups = []
    friends = set(user_vk.friends)
    for index, gid in enumerate(user_vk.groups):
        group_vk = GroupVk(gid)
        time.sleep(0.3)
        if friends.isdisjoint(group_vk.members):
            group_vk.get_group_name()
            time.sleep(0.3)
            private_groups.append(group_vk)
        percent_done = int((index + 1) / group_count * 100)
        print('\r{}%'.format(percent_done), end='')
    print('')
    return private_groups


def save_result(private_groups):
    result = []
    for group in private_groups:
        result.append({
            'name': group.name,
            'gid': group.gid,
            'members_count': group.count
        })
    with open('groups.json', 'w', encoding="utf-8") as f:
        json.dump(result, f)
    print('Результаты поиска записаны в файл')


def main():
    user_vk = get_user()
    private_groups = check_groups_for_friends(user_vk)
    if private_groups:
        print('Найдено секретных групп: {}'.format(len(private_groups)))
        save_result(private_groups)
    else:
        print('У пользователя нет секретных групп')


if __name__ == '__main__':
    main()

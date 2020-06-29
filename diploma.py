import requests
import time

TOKEN = '8a60793fdd7c4b2b39a1ec085f29eca0694708def01d2f4b73502201fa50f4571ed016bc5ea3496e98c8d'


class UserVK:

    def __init__(self, token):
        self.token = token

    def obtain_request(self, url, request_parameters, attempts=1):
        global json_response
        response = None
        if 'access_token' not in request_parameters.keys():
            request_parameters['access_token'] = self.token
        for i in range(attempts):
            try:
                response = requests.get(url, request_parameters)
                json_response = response.json()
                response = json_response['response']
                break
            except KeyError:
                print("Не удалось получить доступ к профилю, статус: ")
                if 'error' in json_response.keys():
                    response = json_response['error']['error_msg']
                    print(response)
                time.sleep(0.34)
        return response

    def get_num_id(self, user_id):
        if not user_id.isdigit():
            try:
                params = {
                    'v': '5.110',
                    'user_ids': user_id
                }
                id_res = self.obtain_request('https://api.vk.com/method/users.get', params)
                user_id = int(id_res[0]['id'])
            except KeyError:
                print('Пользователь не найден')
        print('ID пользователя верно')
        return user_id

    def closed_profile(self, user_id):
        params = {
            'v': '5.110',
            'user_ids': user_id
        }
        status = self.obtain_request('https://api.vk.com/method/users.get', params)
        if_is_closed = status[0]['is_closed']

        return if_is_closed

    def get_user_friends(self, user_id):
        params = {
            'user_id': user_id,
            'v': '5.110'
        }
        friends = self.obtain_request('https://api.vk.com/method/friends.get', params)
        friends_list = friends['items']
        print('Получен список друга пользователя')
        return friends_list

    def get_user_groups(self, user_id):
        params = {
            'user_id': user_id,
            'v': '5.110'
        }
        user_groups = self.obtain_request('https://api.vk.com/method/groups.get', params)
        user_groups_list = user_groups['items']
        groups_count = len(user_groups_list)
        print('Количество групп в которых состоит пользователь: {}'.format(groups_count))
        return user_groups_list

    def friends_groups(self, friends_list):
        global friends_groups_list

        friends_groups_list = []
        for friend_id in friends_list:
            active = UserVK(friend_id)
            params = {
                'user_id': friend_id,
                'v': '5.110'
            }
            global friends_groups
            friends_groups = self.obtain_request('https://api.vk.com/method/groups.get', params)

            if active:
                friends_groups_list.append(friends_groups)
                time.sleep(0.34)
            else:
                pass

            print('Получен список групп друга пользователя')
        return friends_groups_list

    def exclusive_groups(self, user_groups_list, friends_groups_list):

        private_groups = set(user_groups_list) - set(friends_groups)
        private_groups_count = len(private_groups)
        print('Количество приватных групп в которых состоит пользователь: {}'.format(private_groups_count))
        return private_groups

    def get_groups_info(self, private_groups):

        group_fields = ['name', 'id', 'members_count']
        groups_string = [str(s) for s in private_groups]

        params = {
            'group_ids': ','.join(groups_string),
            'fields': ','.join(group_fields),
            'v': '5.110'
        }

        response = self.obtain_request('https://api.vk.com/method/groups.getById', params)

        groups_info = response

        with open('groups.json', 'w', encoding='utf-8') as f:
            private_groups_list = [
                '{"name": "%s","gid": "%s","members_count": %d }' % (group['name'], group['id'], group['members_count'])
                for group in groups_info]
            f.write(','.join(private_groups_list))

        print('Создан файл groups.json с информацией о группах\n\n')
        return groups_info

    def api_call(self):

        close_status = self.closed_profile(user_id)

        if close_status == False:
            friends_list = self.get_user_friends(user_id)
            user_groups_list = self.get_user_groups(user_id)
            friends_groups_list = self.friends_groups(friends_list)
            exclusive_groups_set = self.exclusive_groups(user_groups_list, friends_groups_list)
            self.get_groups_info(exclusive_groups_set)
        else:
            print('Закрытый аккаунт, информация не доступна')


if __name__ == '__main__':
    user = UserVK(TOKEN)
    while True:

        try:
            user_id = user.get_num_id(input(
                'Введите имя или id пользователя ВКонтакте: '))
        except KeyError:
            print('Пользователь не найден')
            user_id = user.get_num_id(input('Введите валидный ID пользователя: '))
        except IndexError:
            print('Пользователь не найден')
            user_id = user.get_num_id(input('Введите валидный ID пользователя: '))
        except TypeError:
            print('Пользователь не найден')
            user_id = user.get_num_id(input('Введите валидный ID пользователя: '))
        user.api_call()
        exit()

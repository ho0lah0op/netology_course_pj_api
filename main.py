import requests
import os
import time
import json
from tqdm import tqdm
from pprint import pprint
from dotenv import dotenv_values

config = dotenv_values(".env")


class PhotoDownload:

    def __init__(self, user_id: str, token_vk: str):
        self.user_id = user_id
        self.token_vk = token_vk
        self.direct = r'C:\Personal\Netology\Misc\vk_photo'

    def download_vk_photo(self):
        os.chdir(self.direct)
        url_vk = 'https://api.vk.com/method/photos.get'
        params_vk = {
            'owner_id': self.user_id,
            'album_id': 'profile',
            'extended': '1',
            'access_token': self.token_vk,
            'v': '5.131'
        }
        res = requests.get(url_vk, params=params_vk)
        response_json = res.json()
        pprint(response_json)
        photo_items = response_json['response']['items']
        with tqdm(total=len(photo_items), desc='Загрузка фотографий') as pbar:
            for item in photo_items:
                url_photo = item['sizes'][-1]['url']
                self.size = item['sizes'][-1]['type']
                response = requests.get(url_photo)
                filename = f"{item['likes']['count']}.jpg"
                with open(filename, "wb") as f:
                    f.write(response.content)
                pbar.update(1)
                time.sleep(1)
                logs_list = []
                download_log = {'file_name': filename, 'size': self.size}
                logs_list.append(download_log)
                with open(f'{self.direct}/log.json', 'a') as file:
                    json.dump(logs_list, file, indent=2)


class PhotoUpload:

    def __init__(self, token_yandex: str):
        self.token_yandex = token_yandex
        self.direct = r'C:\Personal\Netology\Misc\vk_photo'

    def upload_photo_to_yadisk(self, path, num_photos=5):
        os.chdir(self.direct)
        files_list = [name for name in os.listdir(self.direct) if name.endswith(".jpg")]
        sorted_photos = sorted(files_list, key=lambda x: os.path.getsize(x), reverse=True)
        pbar = tqdm(total=min(num_photos, len(sorted_photos)), desc='Отправление фотографий на Я.диск')
        number_of_sent = 0
        for name_file in sorted_photos[:num_photos]:
            number_of_sent += 1
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'OAuth {self.token_yandex}'
            }
            params = {
                'path': f'{path}/{name_file}',
                'overwrite': True
            }
            upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
            response = requests.get(upload_url, headers=headers, params=params)
            href = response.json().get("href", "")
            response = requests.api.put(href, data=open(name_file, 'rb'), headers=headers)
            pbar.update(1)
            time.sleep(0.5)
        pbar.close()
        if number_of_sent == 1:
            print(f'\nНа Я.диск отправлена {number_of_sent} фотография!')
        else:
            print(f'\nНа Я.диск отправлено {number_of_sent} фотографий!')

    def create_folder_yadisk(self, name_folder: str):
        headers = {
            "Accept": 'application/json',
            'Authorization': f'OAuth {self.token_yandex}'
        }
        params = {
            'path': f'/{name_folder}',
        }
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources"
        requests.put(upload_url, headers=headers, params=params)
        return name_folder


if __name__ == '__main__':
    photo_downloader = PhotoDownload(config['id'], config['token_vk'])
    photo_uploader = PhotoUpload(config['token_yandex'])
    folder_name = photo_uploader.create_folder_yadisk('Пользовательские фото VK')
    photo_downloader.download_vk_photo()

    num_photos_to_upload = input("Введите количество фотографий для загрузки на Я.Диск (по умолчанию 5): ")
    if num_photos_to_upload.strip() == "":
        num_photos_to_upload = 5
    else:
        num_photos_to_upload = int(num_photos_to_upload)

    photo_uploader.upload_photo_to_yadisk(folder_name, num_photos=num_photos_to_upload)


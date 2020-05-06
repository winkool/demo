import json
import time

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.reverse import reverse


class qweTestCase(SimpleTestCase):
    visited_links_url = reverse('visited_links')
    visited_domains_url = reverse('visited_domains')

    def test_visited_links(self):
        data = json.dumps(
            {
                "links": [
                    "https://ya.ru",
                    "https://ya.ru?q=123",
                    "funbox.ru",
                    "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor"
                ]
            }
        )
        response = self.client.post(self.visited_links_url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_visited_links_not_valid(self):
        data = json.dumps(
            {
                "links": [
                    "https://ya.ru",
                    "https://ya.ru?q=123",
                    "funbox.ru",
                    "https://stackoverflow.co1m/questions/11828270/how-to-exit-the-vim-editor"
                ]
            }
        )
        response = self.client.post(self.visited_links_url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_visited_links_bad_json(self):
        data = json.dumps(
            [
                "https://ya.ru",
                "https://ya.ru?q=123",
                "funbox.ru",
                "https://stackoverflow.co1m/questions/11828270/how-to-exit-the-vim-editor"
            ]
        )
        response = self.client.post(self.visited_links_url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_visited_domains(self):
        data1 = json.dumps(
            {
                "links": [
                    "https://ya.ru",
                    "https://ya.ru?q=123"
                ]
            }
        )
        start_time = int(time.time())
        self.client.post(self.visited_links_url, data1, content_type='application/json')
        time.sleep(1)
        data2 = json.dumps(
            {
                "links": [
                    "funbox.ru",
                    "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor"
                ]
            }
        )

        middle_time = int(time.time())
        self.client.post(self.visited_links_url, data2, content_type='application/json')
        time.sleep(1)
        end_time = int(time.time())
        data = {'from': start_time, "to": middle_time}
        response = self.client.get(self.visited_domains_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'domains': ['ya.ru'], 'status': 'OK'})

        data = {'from': middle_time, "to": end_time}
        response = self.client.get(self.visited_domains_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.get('domains')), {'funbox.ru', 'stackoverflow.com'})

    def test_visited_domains_failed(self):
        data = {'from': 1123, "to": "qwe"}
        response = self.client.get(self.visited_domains_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_visited_domains_all(self):
        response = self.client.get(self.visited_domains_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

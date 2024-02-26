from django.test import TestCase
import json
import base64

class EventTestCase(TestCase):
    def setUp(self):
        pass

    def test_get_audio(self):
        with open('./test_files/audio_test.mp3', 'rb') as f:
            audio_content = base64.b64encode(f.read()).decode('utf-8')
        data = {
            'id': 'test_id',
            'name': 'test_name',
            'date': "2023-10-26T10:56:30.000Z",
            'type': 'audio',
            'content': audio_content
        }
        resp = self.client.post('/wechat/receive_msg', data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)

    def test_get_image(self):
        with open('./test_files/image_test.jpg', 'rb') as f:
            image_content = base64.b64encode(f.read()).decode('utf-8')
        data = {
            'id': 'test_id',
            'name': 'test_name',
            'date': "2023-10-26T10:56:30.000Z",
            'type': 'image',
            'content': image_content
        }
        resp = self.client.post('/wechat/receive_msg', data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)

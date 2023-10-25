from django.test import TestCase
from .models import Event


# Create your tests here.


class EventTestCase(TestCase):
    def setUp(self):
        self.e1, _ = Event.create_event({"hour": 0, "minute": 0}, "2020-01-10")
        self.e2, _ = Event.create_event({"hour": 0, "minute": 0}, "2020-01-01", repeat="daily")

    def test_get_event(self):
        resp = self.client.get(f'/event/{self.e1.hash}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['data']['event']['hash'], self.e1.hash)

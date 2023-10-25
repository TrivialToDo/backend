from django.test import TestCase
from event.models import Event

# Create your tests here.


class ScheduleTestCase(TestCase):
    def setUp(self):
        self.e1 = Event.create_event({"hour": 0, "minute": 0}, "2020-01-10")
        self.e2 = Event.create_event({"hour": 0, "minute": 0}, "2020-01-01", repeat="daily")
        self.e2 = Event.create_event({"hour": 0, "minute": 0}, "2020-01-10", repeat="weekly")

    def test_get_day(self):
        resp = self.client.get('/schedule/day/2020-01-17')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()['data']['list']), 2)

    def test_get_week(self):
        resp = self.client.get('/schedule/week/2020-01-17')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()['data']['list']), 7)
        self.assertEqual(len(resp.json()['data']['list'][0]), 2)
        self.assertEqual(len(resp.json()['data']['list'][1]), 1)

    def test_get_month(self):
        resp = self.client.get('/schedule/month/2020-01-17')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()['data']['list']), 15)
        self.assertEqual(len(resp.json()['data']['list'][0]), 2)
        self.assertEqual(len(resp.json()['data']['list'][1]), 1)

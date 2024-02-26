from django.test import TestCase
from .models import Event


# Create your tests here.


class EventTestCase(TestCase):
    def setUp(self):
        # resp = self.get("/token")
        self.test_token = "Bearer " + "???"

    def test_create_event(self):
        resp = self.client.post(
            "/event/new",
            {
                "timeStart": {"hour": 0, "minute": 0},
                "dateStart": "2020-01-01",
            },
            HTTP_AUTHORIZATION=self.test_token
        )
        self.assertEqual(resp.status_code, 200)
        self.e1_hash = resp.json()["data"]["hash"]

    def test_get_event_1(self):
        resp = self.client.get(f"/event/{self.e1_hash}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["event"]["hash"], self.e1_hash)
        self.assertEqual(resp.json()["data"]["event"]["title"], "Untitled")

    def test_modify_event_1(self):
        resp = self.client.post(
            "/event/modify",
            {
                "hash": self.e1_hash,
                "title": "test",
                "timeStart": {"hour": 0, "minute": 0},
                "dateStart": "2020-01-01",
            },
            HTTP_AUTHORIZATION=self.test_token
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["hash"], self.e1_hash)
        self.assertEqual(resp.json()["data"]["title"], "test")

    def test_modify_event_2(self):
        resp = self.client.post(
            "/event/modify",
            {
                "hash": "123",
                "title": "test",
                "timeStart": {"hour": 0, "minute": 0},
                "dateStart": "2020-01-01",
                "repeat": "daily",
            },
            HTTP_AUTHORIZATION=self.test_token
        )
        self.assertEqual(resp.status_code, 404)

    def test_del_event(self):
        resp = self.client.delete(f"/event/{self.e1_hash}")
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get(f"/event/{self.e1_hash}")
        self.assertEqual(resp.status_code, 404)

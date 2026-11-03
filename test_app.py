import unittest
from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_hello(self):
        r = self.client.get('/hello?name=TEST')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'Hello, TEST!', r.data)

if __name__ == '__main__':
    unittest.main()
import unittest
from unittest.mock import patch
from main import app

class MainTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_get_hello(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Hello, world!')

    @patch('main.requests.post')
    def test_post_data(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = 'Data received'
        data = {'key': 'value'}
        response = self.app.post('/data', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Data received')
        mock_post.assert_called_once_with('https://example.com/api', data=data)

if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock
import os
from main import query_endpoint

class TestQueryEndpoint(unittest.TestCase):

    @patch('main.requests.post')
    @patch('main.os.getenv')
    def test_query_endpoint(self, mock_getenv, mock_post):
        # Mock environment variables
        mock_getenv.side_effect = lambda key, default=None: {
            'APP_USERNAME': 'test_user',
            'APP_PASSWORD': 'test_pass'
        }.get(key, default)

        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'thread_id': 'test_thread_id',
            'answer': {'content': 'Test answer'}
        }
        mock_post.return_value = mock_response

        # Call the function
        thread_id, answer = query_endpoint('Test question', 'test_thread', 'test_channel')

        # Assertions
        self.assertEqual(thread_id, 'test_thread_id')
        self.assertEqual(answer, 'Test answer')

        # Check if post was called with correct arguments
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('auth', call_args.kwargs)
        self.assertEqual(call_args.kwargs['auth'], ('test_user', 'test_pass'))

    @patch('main.requests.post')
    @patch('main.os.getenv')
    def test_query_endpoint_error(self, mock_getenv, mock_post):
        # Mock environment variables with default values
        mock_getenv.side_effect = lambda key, default=None: default

        # Mock an error response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_post.return_value = mock_response

        # Call the function
        thread_id, answer = query_endpoint('Test question')

        # Assertions
        self.assertIsNone(thread_id)
        self.assertEqual(answer, 'Error: 404')

        # Check if post was called with correct arguments
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('auth', call_args.kwargs)
        self.assertEqual(call_args.kwargs['auth'], ('admin', 'test1234'))

if __name__ == '__main__':
    unittest.main()
EOL;cat tests/unit/test_query_api.py
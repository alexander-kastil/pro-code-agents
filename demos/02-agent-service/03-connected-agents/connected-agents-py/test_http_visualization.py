"""
Unit tests for HTTP visualization improvements in Mermaid logger.

This test suite validates:
1. HTTP log handler correctly captures and parses Azure SDK logs
2. Endpoint normalization works correctly
3. HTTP diagram generation produces expected output
4. Operation descriptions are accurate
"""
import unittest
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from mermaid_logger import MermaidLogger
from logging_config import HttpLogHandler


class TestHttpVisualization(unittest.TestCase):
    """Test suite for HTTP visualization functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a fresh mermaid logger for each test
        self.mermaid_logger = MermaidLogger(enabled=True, verbose=False, http_log=True)
        
        # Create HTTP handler
        self.handler = HttpLogHandler(self.mermaid_logger)
        self.handler.setLevel(logging.INFO)
        
        # Create test logger
        self.http_logger = logging.getLogger("test_azure_http")
        self.http_logger.setLevel(logging.INFO)
        self.http_logger.handlers.clear()
        self.http_logger.addHandler(self.handler)
    
    def tearDown(self):
        """Clean up after each test."""
        self.http_logger.handlers.clear()
    
    def _simulate_http_request(self, method, url, status):
        """Helper to simulate an Azure SDK HTTP request/response."""
        self.http_logger.info(f"Request method: '{method}'")
        self.http_logger.info(f"Request URL: '{url}'")
        self.http_logger.info(f"Response status: {status}")
    
    def test_endpoint_normalization(self):
        """Test that endpoints are properly normalized with {id} placeholders."""
        # Test assistant creation
        self._simulate_http_request(
            'POST',
            'https://example.com/api/projects/test-proj/assistants?api-version=2024-07-01',
            '201'
        )
        
        events = self.mermaid_logger._http_events
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['endpoint'], '/assistants')
        
        # Test thread with ID
        self.mermaid_logger._http_events.clear()
        self._simulate_http_request(
            'GET',
            'https://example.com/api/projects/test-proj/threads/thread-abc123/messages?api-version=2024-07-01',
            '200'
        )
        
        events = self.mermaid_logger._http_events
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['endpoint'], '/threads/{id}/messages')
    
    def test_operation_descriptions(self):
        """Test that operation descriptions are accurate."""
        logger = self.mermaid_logger
        
        # Test various endpoint patterns
        test_cases = [
            ('POST', '/assistants', 'Create agent'),
            ('GET', '/assistants', 'List agents'),
            ('DELETE', '/assistants/{id}', 'Delete agent'),
            ('POST', '/threads', 'Create thread'),
            ('POST', '/threads/{id}/messages', 'Add message'),
            ('GET', '/threads/{id}/messages', 'List messages'),
            ('POST', '/threads/{id}/runs', 'Start run'),
            ('GET', '/threads/{id}/runs/{id}', 'Get run status'),
        ]
        
        for method, endpoint, expected_desc in test_cases:
            with self.subTest(method=method, endpoint=endpoint):
                desc = logger._get_operation_description(method, endpoint)
                self.assertEqual(desc, expected_desc)
    
    def test_status_emoji(self):
        """Test that status codes get appropriate emoji indicators."""
        logger = self.mermaid_logger
        
        test_cases = [
            ('200', '✓'),
            ('201', '✓'),
            ('204', '✓'),
            ('400', '⚠'),
            ('404', '⚠'),
            ('500', '✗'),
            ('503', '✗'),
        ]
        
        for status, expected_emoji in test_cases:
            with self.subTest(status=status):
                emoji = logger._get_status_emoji(status)
                self.assertEqual(emoji, expected_emoji)
    
    def test_diagram_generation(self):
        """Test that HTTP diagram is generated correctly."""
        # Simulate a sequence of API calls
        api_calls = [
            ('POST', 'https://example.com/api/projects/test/assistants?api-version=2024-07-01', '201'),
            ('POST', 'https://example.com/api/projects/test/threads?api-version=2024-07-01', '200'),
            ('POST', 'https://example.com/api/projects/test/threads/thread-123/messages?api-version=2024-07-01', '200'),
            ('GET', 'https://example.com/api/projects/test/threads/thread-123/messages?api-version=2024-07-01', '200'),
        ]
        
        for method, url, status in api_calls:
            self._simulate_http_request(method, url, status)
        
        # Generate diagram
        diagram = self.mermaid_logger.get_mermaid_diagram(log_level='http')
        
        # Verify diagram content
        self.assertIn('sequenceDiagram', diagram)
        self.assertIn('participant Client', diagram)
        self.assertIn('participant API', diagram)
        self.assertIn('POST /assistants', diagram)
        self.assertIn('Create agent', diagram)
        self.assertIn('POST /threads', diagram)
        self.assertIn('Add message', diagram)
        self.assertIn('List messages', diagram)
        self.assertIn('[1]', diagram)  # Sequential numbering
        self.assertIn('✓', diagram)  # Status emoji
    
    def test_pattern_matching(self):
        """Test that endpoint pattern matching works correctly."""
        logger = self.mermaid_logger
        
        test_cases = [
            ('/threads/{id}/messages', '/threads/thread-abc123/messages', True),
            ('/threads/{id}/runs/{id}', '/threads/thread-abc123/runs/run-xyz789', True),
            ('/assistants/{id}', '/assistants/asst_123456789', True),
            ('/threads/{id}', '/threads/messages', False),
            ('/assistants', '/assistants/{id}', False),
        ]
        
        for pattern, endpoint, expected in test_cases:
            with self.subTest(pattern=pattern, endpoint=endpoint):
                result = logger._matches_pattern(endpoint, pattern)
                self.assertEqual(result, expected)
    
    def test_http_events_captured(self):
        """Test that HTTP events are properly captured."""
        # Simulate multiple requests
        self._simulate_http_request(
            'POST',
            'https://example.com/api/projects/test/assistants?api-version=2024-07-01',
            '201'
        )
        
        self._simulate_http_request(
            'DELETE',
            'https://example.com/api/projects/test/assistants/asst-123?api-version=2024-07-01',
            '204'
        )
        
        events = self.mermaid_logger._http_events
        
        # Should have 2 events
        self.assertEqual(len(events), 2)
        
        # First event should be POST
        self.assertEqual(events[0]['type'], 'http_request')
        self.assertIn('POST', events[0]['request'])
        self.assertEqual(events[0]['status'], '201')
        
        # Second event should be DELETE
        self.assertEqual(events[1]['type'], 'http_request')
        self.assertIn('DELETE', events[1]['request'])
        self.assertEqual(events[1]['status'], '204')
    
    def test_empty_diagram_when_no_events(self):
        """Test that empty string is returned when no HTTP events are captured."""
        diagram = self.mermaid_logger.get_mermaid_diagram(log_level='http')
        self.assertEqual(diagram, '')
    
    def test_id_detection(self):
        """Test that various ID formats are properly detected."""
        handler = self.handler
        
        test_cases = [
            ('https://example.com/api/projects/test/threads/thread-abc123/messages', '/threads/{id}/messages'),
            ('https://example.com/api/projects/test/assistants/asst_1234567890abcdef', '/assistants/{id}'),
            ('https://example.com/api/projects/test/runs/run-xyz-123-456', '/runs/{id}'),
            ('https://example.com/api/projects/test/threads/very-long-uuid-12345678901234567890', '/threads/{id}'),
        ]
        
        for url, expected_endpoint in test_cases:
            with self.subTest(url=url):
                endpoint = handler._parse_endpoint(url)
                self.assertEqual(endpoint, expected_endpoint)


class TestMermaidLoggerIntegration(unittest.TestCase):
    """Integration tests for the complete Mermaid logger workflow."""
    
    def test_complete_workflow(self):
        """Test the complete workflow from logging to diagram generation."""
        # Create logger
        logger = MermaidLogger(enabled=True, verbose=True, http_log=True)
        
        # Set user prompt
        logger.log_message_sent('User', 'triage-agent', 'user_prompt', 'Test ticket')
        
        # Simulate HTTP events
        logger.log_http_request('POST /assistants', '201', '/assistants')
        logger.log_http_request('POST /threads', '200', '/threads')
        logger.log_http_request('GET /threads/{id}/messages', '200', '/threads/{id}/messages')
        
        # Generate all diagrams
        default_diagram = logger.get_mermaid_diagram('default')
        verbose_diagram = logger.get_mermaid_diagram('verbose')
        http_diagram = logger.get_mermaid_diagram('http')
        
        # Verify all diagrams are generated
        self.assertIn('sequenceDiagram', default_diagram)
        self.assertIn('graph TD', verbose_diagram)
        self.assertIn('sequenceDiagram', http_diagram)
        
        # Verify HTTP diagram has expected content
        self.assertIn('Create agent', http_diagram)
        self.assertIn('Create thread', http_diagram)
        self.assertIn('List messages', http_diagram)


if __name__ == '__main__':
    unittest.main(verbosity=2)

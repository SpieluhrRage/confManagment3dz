import unittest
import json
from io import StringIO
from config_to_json import ConfigParser, SyntaxError  # Предполагается, что файл называется config_parser.py

class TestConfigParser(unittest.TestCase):

    def setUp(self):
        self.parser = ConfigParser()

    def test_simple_key_value(self):
        config = "key1 => 42, key2 => \"value\""
        result = self.parser.parse(config)
        expected = {
            "key1": 42,
            "key2": "value"
        }
        self.assertEqual(result, expected)

    def test_array(self):
        config = "arr => [1, 2, 3]"
        result = self.parser.parse(config)
        expected = {
            "arr": [1, 2, 3]
        }
        self.assertEqual(result, expected)

    def test_empty_array(self):
        config = "arr => []"
        result = self.parser.parse(config)
        expected = {
            "arr": []
        }
        self.assertEqual(result, expected)

    def test_table(self):
        config = "tbl => table(key1 => 1, key2 => \"value\")"
        result = self.parser.parse(config)
        expected = {
            'tbl':{
                "key1": 1,
            "key2": "value"
            }
            
        }
        self.assertEqual(result, expected)

    def test_empty_table(self):
        config = "table()"
        result = self.parser.parse(config)
        expected = {}
        self.assertEqual(result, expected)

    def test_constants(self):
        config = "set x = 5\nkey => @{+ x x}"
        result = self.parser.parse(config)
        expected = {
            "key": 10
        }
        self.assertEqual(result, expected)

    def test_expression_sqrt(self):
        config = "key => @{sqrt 16}"
        result = self.parser.parse(config)
        expected = {
            "key": 4.0
        }
        self.assertEqual(result, expected)

    def test_expression_abs(self):
        config = "key => @{abs -42}"
        result = self.parser.parse(config)
        expected = {
            "key": 42
        }
        self.assertEqual(result, expected)

    def test_multiline_comments(self):
        config = """
        key1 => 42, {# This is a multiline
        comment #} key2 => \"value\"
        """
        result = self.parser.parse(config)
        expected = {
            "key1": 42,
            "key2": "value"
        }
        self.assertEqual(result, expected)

    def test_syntax_error_invalid_key_value(self):
        config = "key1 : 42"
        with self.assertRaises(SyntaxError):
            self.parser.parse(config)

    def test_syntax_error_invalid_table(self):
        config = "table(key1, key2)"
        with self.assertRaises(SyntaxError):
            self.parser.parse(config)

if __name__ == "__main__":
    unittest.main()

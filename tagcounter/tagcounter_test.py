import unittest
import unittest.mock
from tagcounter.tagcounter import MyHTMLParser
from tagcounter.tagcounter import TagInfo
from unittest.mock import MagicMock


class TestHrmlParser(unittest.TestCase):
    def setUp(self):
        tag_info = TagInfo()
        tag_info.find_by_url = MagicMock(return_value=None)
        self.htmlParser = MyHTMLParser(tag_info)

    def test_format_url(self):
        url = 'yandex.ru'
        self.assertEqual(self.htmlParser.format_url(url), 'https://yandex.ru')

    def test_process_get(self):

        result = self.htmlParser.process_get('https://yandex.ru')

        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # Проверим, что s.split не работает, если разделитель - не строка
        with self.assertRaises(TypeError):
            s.split(2)


if __name__ == '__main__':
    unittest.main()

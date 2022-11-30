import unittest.mock
from unittest.mock import patch

import pytest

import tagcounter.tagcounter
from tagcounter.tagcounter import MyHTMLParser
from tagcounter.tagcounter import TagInfo


class TestMyHrmlParser(unittest.TestCase):
    @staticmethod
    def createMockHtml():
        return bytes('''
        <h1>A Guide to Solving Web Development Problems</h1>
        <p>This is about how to solve technical problems that arise from using front or back end technologies to make web pages or apps but some of these steps will be applicable to solving technical problems in general.</p>
        <p>Half the technical problems in development are caused by something trivial but for all the problems past this level, you'll probably need to do some structured thinking.</p>
        <h2>Troubleshooting Steps Summary</h2>
        ''', 'utf-8')

    @staticmethod
    def createMockTagInfo():
        return TagInfo(url='url', domain='domain', tag_dictionary='{"h1": 1, "p": 2, "h2": 1}')

    @pytest.fixture(autouse=True)
    def _pass_fixtures(self, capsys):
        self.capsys = capsys

    def setUp(self):
        tag_info = TagInfo()
        self.htmlParser = MyHTMLParser(tag_info)

    def test_format_url(self):
        url = 'yandex.ru'
        self.assertEqual(self.htmlParser.format_url(url), 'https://yandex.ru')

    @patch.object(tagcounter.tagcounter.TagInfo, 'find_by_url')
    @patch.object(tagcounter.tagcounter.MyHTMLParser, 'load_site')
    @patch.object(tagcounter.tagcounter.TagInfo, 'persist')
    def test_process_get(self, mock_find_by_url, mock_load_site, mock_persist):
        mock_find_by_url.return_value = None
        mock_load_site.return_value = self.createMockHtml()
        mock_persist.return_value = ''
        expected = {"h1": 1, "p": 2, "h2": 1}
        self.htmlParser.process_get('https://yandex.ru')
        result = self.htmlParser.tag_dictionary
        mock_find_by_url.assert_called()
        mock_load_site.assert_called()
        mock_persist.assert_called()
        self.assertEqual(expected, result)

    @patch.object(tagcounter.tagcounter.TagInfo, 'find_by_url')
    def test_process_view(self, mock_find_by_url):
        test_cases = [
            {
                'arguments': {'site_url': 'https://yandex.ru'},
                'mock': None,
                'expected_result': 'Данные по https://yandex.ru отсутствуют. Для загрузки данных используйте --get '
                                   '"https://yandex.ru"\n'
            },
            {
                'arguments': {'site_url': 'https://mail.yandex.ru'},
                'mock': self.createMockTagInfo(),
                'expected_result': '{"h1": 1, "p": 2, "h2": 1}\n'
            }
        ]

        for test_case in test_cases:
            mock_find_by_url.return_value = test_case['mock']
            self.htmlParser.process_view(**test_case['arguments'])
            captured = self.capsys.readouterr()
            self.assertEqual(test_case['expected_result'],
                             captured.out)
        # self.htmlParser.process_view('https://yandex.ru')
        # captured = self.capsys.readouterr()
        # self.assertEqual('Данные по https://yandex.ru отсутствуют. Для загрузки данных используйте --get '
        #                  '"https://yandex.ru"\n',
        #                  captured.out)


if __name__ == '__main__':
    unittest.main()

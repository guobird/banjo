import unittest
from banjo import Application


class TestApplication(unittest.TestCase):
    def test_segment_match(self):
        self.assertTrue(Application.segment_match('username', 'username', {}))
        self.assertTrue(Application.segment_match('username', 'uder', {}) == False)
        named_dict = {}
        result = Application.segment_match(':username', 'bird', named_dict)
        self.assertTrue((named_dict['username']=='bird') and result==True)
        named_dict.clear()

        self.assertTrue(Application.segment_match(':year-:month-:day', '1984-11-17', named_dict))
        print(named_dict)
        self.assertTrue(named_dict['year'] == '1984')
        self.assertTrue(named_dict['month'] == '11')
        self.assertTrue(named_dict['day'] == '17')


if __name__ == '__main__':
    unittest.main()

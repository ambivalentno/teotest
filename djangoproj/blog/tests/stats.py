import unittest
from blog.calc import drop_stopwords, string_to_words, count_words


SENTENCE = '''I'll eat meat, dish.'''


class StatsTestCase(unittest.TestCase):

    def test_to_words(self):
        data = list(string_to_words(SENTENCE))
        self.assertListEqual(data, ['i', 'll', 'eat', 'meat', 'dish'])

    def test_drop_stopwords(self):
        data = list(drop_stopwords(string_to_words(SENTENCE)))
        self.assertListEqual(data, ['eat', 'meat', 'dish'])

    def test_count_words(self):
        text = SENTENCE * 10
        data = count_words(text)
        self.assertEqual(len(data.values()), 3)
        for item in data.values():
            self.assertEqual(item, 10)


import re
from WordEnumerator import WordEnumerator


class WordSequencer:

    def __init__(self, regex=r";|!|\?|,|[\w']+|\."):
        self.word_enumerator = WordEnumerator()
        self.regex = regex

    def normalize_string(self, s):
        return s

    def normalize_word(self, word):
        return word

    def tokenize_into_list_of_words(self, string_or_strings):
        strings = [string_or_strings] if isinstance(string_or_strings, str) else string_or_strings
        all_words = []
        for string in strings:
            try:
                words = re.findall(self.regex, self.normalize_string(string))
                all_words += map(lambda x: self.normalize_word(x), words)
            except:
                print("Error in re.findall:")
                print("regex: " + self.regex)
                print("string: " + string)
                exit(0)
        return all_words

    def tokenize_into_int_sequence(self, string_or_strings):
        words = self.tokenize_into_list_of_words(string_or_strings)
        return self.get_int_sequence_from_list_of_words(words)

    def tokenize_into_int_sequence_existing_words_only(self, string_or_strings):
        words = self.tokenize_into_list_of_words(string_or_strings)
        return self.get_int_sequence_from_list_of_words(words, self.word_enumerator.ints_by_word)

    def get_int_sequence_from_list_of_words(self, words, allowed_words=None):
        int_sequence = []
        for word in words:
            if allowed_words is None or word in allowed_words:
                int_sequence.append(self.word_enumerator.add_word(word))
            else:
                int_sequence.append(3)
        return int_sequence

    def get_list_of_words_from_int_sequence(self, int_sequence):
        words = []
        for i in int_sequence:
            words.append(self.word_enumerator.get_word_of_int(i))
        return words

    def count_words(self):
        return self.word_enumerator.count_words()

    def count_uses(self):
        return self.word_enumerator.count_uses()

    def get_all_words(self):
        return self.word_enumerator.get_all_words()

    def save_to_file(self, file):
        self.word_enumerator.save_to_file(file)

    def load_from_file(self, file):
        self.word_enumerator.load_from_file(file)

    def get_top_words(self, number_of_words):
        return self.word_enumerator.get_top_words(number_of_words)

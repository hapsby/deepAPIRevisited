import json


class WordEnumerator:
    def __init__(self):
        self.ints_by_word = {}
        self.words_by_int = []
        self.word_uses = {}

    def add_word(self, word):
        if word not in self.ints_by_word:
            i = len(self.words_by_int)
            self.ints_by_word[word] = i
            self.words_by_int.append(word)
            self.word_uses[word] = 1
            return i
        self.word_uses[word] += 1
        return self.ints_by_word[word]

    def add_words(self, words):
        for word in words:
            self.add_word(word)

    def get_int_of_word(self, word):
        return self.ints_by_word[word]

    def get_word_of_int(self, i):
        return self.words_by_int[i]

    def count_words(self):
        return len(self.words_by_int)

    def count_uses(self):
        return sum(self.word_uses.values())

    def get_all_words(self):
        return set(self.words_by_int)

    def save_to_file(self, file):
        json.dump(self.words_by_int, file)
        print("Wrote " + str(len(self.words_by_int)) + " words to " + file.name + ".")

    def load_from_file(self, file):
        words = json.load(file)
        self.add_words(words)

    def get_top_words(self, number_of_words):
        sorted_items = sorted(self.word_uses.items(), key=lambda x: x[1], reverse=True)
        words = []
        for item in sorted_items[:number_of_words]:
            words.append(item[0])
        return words

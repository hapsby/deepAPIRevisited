from WordSequencer import WordSequencer


class ApiSequencer(WordSequencer):

    def __init__(self):
        super().__init__(r"[^.]+|\.")

    def normalize_string(self, s):
        return s

    def normalize_word(self, word):
        return word

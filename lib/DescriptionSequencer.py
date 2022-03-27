import re
import nltk
from WordSequencer import WordSequencer


def extract_description(docstring):
    lines = list(map(lambda x: x.strip(), docstring.splitlines()))
    primary_description = find_primary_description(lines)
    returns_description = find_returns_description(lines)
    return primary_description + " " + returns_description


def find_primary_description(lines):
    for i, line in enumerate(lines):
        if line != "":
            lines = read_lines_from_offset(lines, i)
            return " ".join(lines)
    return ""


def find_returns_description(lines):
    first_was_found = False
    for i, line in enumerate(lines):
        if line != "":
            if not first_was_found:
                first_was_found = True
            else:
                first_word = get_first_word(line).lower()
                if first_word == "return" or first_word == "returns":
                    lines = read_lines_from_offset(lines, i)
                    string = " ".join(lines)
                    return re.sub(r'^:?returns?:?', 'return', string)
    return ""


def read_lines_from_offset(lines, first_line):
    sublist_of_lines = []
    params_words = ["param", "params", "parameter", "parameters"]
    return_words = ["return", "returns"]
    for line in lines[first_line:]:
        if line == "":
            break
        first_word = get_first_word(line).lower()
        if first_word in params_words:
            break
        if len(sublist_of_lines) > 0 and first_word in return_words:
            break
        sublist_of_lines.append(line)
    return sublist_of_lines


def get_first_word(line):
    words = re.findall(r"\w+", line)
    if len(words) > 0:
        return words[0]
    return ""


class DescriptionSequencer(WordSequencer):

    def __init__(self):
        regex = re.compile(r";|!|\?|,|[a-z][a-z']*[a-z]|[a-z]|\.", re.IGNORECASE)
        self.porter = nltk.stem.PorterStemmer()
        super().__init__(regex)

    def normalize_string(self, s):
        return extract_description(s)

    def normalize_word(self, word):
        return self.porter.stem(word.lower())


def read_lines_as_set(file_path):
    try:
        file_handle = open(file_path, "r")
    except FileNotFoundError:
        return set()
    set_of_strings = set()
    for line in file_handle:
        string = line.strip()
        if string != "":
            set_of_strings.add(string)
    file_handle.close()
    return set_of_strings


class SetOfStringsInFile:

    def __init__(self, file_path):
        self.set_of_strings = read_lines_as_set(file_path)
        self.file_handle = open(file_path, "a")

    def add_string(self, string):
        if string not in self.set_of_strings:
            self.set_of_strings.add(string)
            self.file_handle.write(string + "\n")
            self.file_handle.flush()

    def add_strings(self, new_strings):
        new_strings = new_strings.difference(self.set_of_strings)
        if new_strings != set():
            self.set_of_strings.update(new_strings)
            list_of_strings = [str(s) for s in new_strings]
            joined_string = "\n".join(list_of_strings) + "\n"
            self.file_handle.write(joined_string)
            self.file_handle.flush()

    def close(self):
        self.file_handle.close()

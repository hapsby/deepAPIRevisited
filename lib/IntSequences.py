import tables
import numpy as np


class IntegerColumnTable(tables.IsDescription):
    i = tables.UInt32Col


class IntSequences:

    def __init__(self, file_path, title):
        self.file = tables.open_file(file_path, mode="w", title=title)
        self.indices = self.file.create_earray("/", 'indices', obj=np.array([], dtype=np.uint32))
        self.phrases = self.file.create_earray("/", 'phrases', obj=np.array([], dtype=np.uint32))


    def add_sequence(self, int_sequence):
        self.phrases.append(int_sequence)
        self.indices.append([self.phrases.nrows])


    def close(self):
        self.file.close()


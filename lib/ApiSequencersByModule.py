from ApiSequencer import ApiSequencer
from functions import *


class ApiSequencersByModule:

    def __init__(self):
        self.api_sequencers_by_module = {}
        self.counts_by_module = {}

    def add_api_call(self, api_call):
        module = get_module_of_api_call(api_call)
        if module not in self.api_sequencers_by_module:
            self.api_sequencers_by_module[module] = ApiSequencer()
            self.counts_by_module[module] = 1
        else:
            self.counts_by_module[module] += 1
        self.api_sequencers_by_module[module].tokenize_into_int_sequence(api_call)

    def get_modules_by_descending_uses(self):
        sorted_items = sorted(self.counts_by_module.items(), key=lambda x: x[1], reverse=True)
        modules_by_descending_uses = []
        for item in sorted_items:
            modules_by_descending_uses.append(item[0])
        return modules_by_descending_uses

    def get_modules_with_limited_symbols(self, max_symbols):
        modules = set()
        words = set()
        for module in self.get_modules_by_descending_uses():
            test_words = words.union(self.api_sequencers_by_module[module].get_all_words())
            if len(test_words) <= max_symbols:
                modules.add(module)
                words = test_words
        return modules

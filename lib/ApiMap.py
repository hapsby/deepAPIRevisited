from DescriptionSequencer import DescriptionSequencer
from DuplicatePairDetector import DuplicatePairDetector
from functions import *
from ApiMapStats import ApiMapStats

class ApiMap:
    """ This remembers the API calls and descriptions of all functions in a project. """

    def __init__(self, api_map_stats: ApiMapStats = None):
        self.api_calls_by_function_name = {}
        self.descriptions_by_function_name = {}
        self.stats = api_map_stats if api_map_stats is not None else ApiMapStats()

    def set_pair_with_stats(self, function_name, description, api_calls):
        self.stats.total_functions += 1
        if function_name not in self.descriptions_by_function_name:
            self.stats.total_functions_minus_duplicates += 1
            if len(api_calls) > 0:
                self.stats.total_functions_minus_no_api_calls += 1
                if len(api_calls) < 15:
                    self.stats.total_functions_minus_too_many_api_calls += 1
                    self.set_pair(function_name, description, api_calls)

    def set_pair(self, function_name, description, api_calls):
        self.descriptions_by_function_name[function_name] = description
        self.api_calls_by_function_name[function_name] = api_calls

    def add_api_map(self, other_api_map, prefix):
        for function_name, api_calls in other_api_map.api_calls_by_function_name.items():
            description = other_api_map.descriptions_by_function_name[function_name]
            self.set_pair(prefix + function_name, description, api_calls)
        self.stats.add(other_api_map.stats)

    def filter_functions(self, filter_callback):
        functions_to_remove = []
        for function_name, api_calls in self.api_calls_by_function_name.items():
            if not filter_callback(self.descriptions_by_function_name[function_name], api_calls):
                functions_to_remove.append(function_name)
        for function_name in functions_to_remove:
            del self.descriptions_by_function_name[function_name]
            del self.api_calls_by_function_name[function_name]

    def filter_by_allowed_modules(self, allowed_modules):
        def filter_callback(description, api_calls):
            nonlocal allowed_modules
            for api_call in api_calls:
                module = get_module_of_api_call(api_call)
                if module not in allowed_modules:
                    return False
            return True
        self.filter_functions(filter_callback)

    def filter_by_allowed_descriptions(self, allowed_description_words):
        description_sequencer = DescriptionSequencer()

        def filter_callback(description, api_calls):
            nonlocal description_sequencer, allowed_description_words
            words = description_sequencer.tokenize_into_list_of_words(description)
            for word in words:
                if word not in allowed_description_words:
                    return False
            return True
        self.filter_functions(filter_callback)

    def filter_non_unique(self, duplicate_pair_detector : DuplicatePairDetector):
        def filter_callback(description, api_calls):
            nonlocal duplicate_pair_detector
            return duplicate_pair_detector.add_if_new(description, api_calls)
        self.filter_functions(filter_callback)

    def count_pairs(self):
        return len(self.descriptions_by_function_name)

    def get_set_of_api_calls(self):
        api_calls = set()
        for api_calls_of_function in self.api_calls_by_function_name.values():
            api_calls.update(api_calls_of_function)
        return api_calls


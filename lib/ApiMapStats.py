

class ApiMapStats:

    def __init__(self):
        self.total_functions = 0
        self.total_functions_minus_duplicates = 0
        self.total_functions_minus_no_api_calls = 0
        self.total_functions_minus_too_many_api_calls = 0
        self.total_files = 0
        self.total_utf8_files = 0
        self.total_parsed_files = 0

    @classmethod
    def from_object(cls, o):
        api_map_stats = cls()
        api_map_stats.total_functions = o['total_functions']
        api_map_stats.total_functions_minus_duplicates = o['total_functions_minus_duplicates']
        api_map_stats.total_functions_minus_no_api_calls = o['total_functions_minus_no_api_calls']
        api_map_stats.total_functions_minus_too_many_api_calls = o['total_functions_minus_too_many_api_calls']
        api_map_stats.total_files = o['total_files']
        api_map_stats.total_utf8_files = o['total_utf8_files']
        api_map_stats.total_parsed_files = o['total_parsed_files']
        return api_map_stats

    def to_object(self):
        return {
            "total_functions": self.total_functions,
            "total_functions_minus_duplicates": self.total_functions_minus_duplicates,
            "total_functions_minus_no_api_calls": self.total_functions_minus_no_api_calls,
            "total_functions_minus_too_many_api_calls": self.total_functions_minus_too_many_api_calls,
            "total_files": self.total_files,
            "total_utf8_files": self.total_utf8_files,
            "total_parsed_files": self.total_parsed_files
        }

    def add(self, other):
        self.total_functions += other.total_functions
        self.total_functions_minus_duplicates += other.total_functions_minus_duplicates
        self.total_functions_minus_no_api_calls += other.total_functions_minus_no_api_calls
        self.total_functions_minus_too_many_api_calls += other.total_functions_minus_too_many_api_calls
        self.total_files += other.total_files
        self.total_utf8_files += other.total_utf8_files
        self.total_parsed_files += other.total_parsed_files

    def print(self):
        print("Total files: " + str(self.total_files))
        print("Total UTF8 files: " + str(self.total_utf8_files))
        print("Total parsed files: " + str(self.total_parsed_files))
        print("Total functions: " + str(self.total_functions))
        print("After removing duplicate function names: " + str(self.total_functions_minus_duplicates))
        print("After removing those with no API calls: " + str(self.total_functions_minus_no_api_calls))
        print("After removing those with too many API calls: " + str(self.total_functions_minus_too_many_api_calls))



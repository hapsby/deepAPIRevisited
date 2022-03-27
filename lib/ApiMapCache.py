import json
from ApiMap import ApiMap
from ApiMapStats import ApiMapStats

class ApiMapCache:

    def __init__(self):
        self.known_projects = set()

    def load(self, name):
        try:
            with open(name + ".json", "r") as file:
                encoded = json.load(file)
                pairs = encoded['pairs']
                api_map = ApiMap()
                api_map.stats = ApiMapStats.from_object(encoded['stats'])
                for function_name, pair in pairs.items():
                    api_map.set_pair(function_name, pair[0], pair[1])
                self.known_projects.add(name)
                return api_map
        except Exception:
            return None

    def save(self, name, api_map):
        try:
            with open(name + ".json", "w") as file:
                pairs = {}
                for function_name, description in api_map.descriptions_by_function_name.items():
                    if function_name in api_map.api_calls_by_function_name:
                        api_calls = api_map.api_calls_by_function_name[function_name]
                        pairs[function_name] = [description, api_calls]
                json.dump({"pairs": pairs, "stats": api_map.stats.to_object()}, file)
                self.known_projects.add(name)
        except Exception:
            return None


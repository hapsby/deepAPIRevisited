import hashlib


class DuplicatePairDetector:

    def __init__(self):
        self.hashes = set()

    def add_if_new(self, description, api_calls):
        hash_binary = self.get_hash_binary(description, api_calls)
        if hash_binary in self.hashes:
            return False
        self.hashes.add(hash_binary)
        return True

    def get_hash_binary(self, description, api_calls):
        hasher = hashlib.md5(description.encode('utf-8'))
        for api_call in api_calls:
            hasher.update(api_call.encode('utf-8'))
        return hasher.digest()[0:5]


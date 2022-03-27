from IntSequences import IntSequences
import random
import json
from functions import *
from ApiSequencer import ApiSequencer
from DescriptionSequencer import DescriptionSequencer


class DataSets:
    """An instance of this class is used to build the training and test datasets."""

    def __init__(
            self,
            training_weight: int,
            test_weight: int,
            api_sequencer: ApiSequencer,
            description_sequencer: DescriptionSequencer
    ):
        """
        :param training_weight: The relative probability of a pair being added to the training set.
        :param test_weight: The relative probability of a pair being added to the test set.
        """
        self.weights = [training_weight, test_weight]
        self.apiseq_dbs = [
            IntSequences("train.apiseq.h5", "Training API sequences"),
            IntSequences("test.apiseq.h5", "Test API sequences")
        ]
        self.desc_dbs = [
            IntSequences("train.desc.h5", "Training descriptions"),
            IntSequences("test.desc.h5", "Test descriptions"),
        ]
        self.codebert_dbs = [
            open("api_train.jsonl", "w"),
            open("api_test.jsonl", "w")
        ]
        self.api_sequencer = api_sequencer
        self.description_sequencer = description_sequencer
        self.removed_for_short = 0
        self.removed_for_test_in_function_name = 0
        self.removed_for_test_in_desc = 0

    def write_api_map(self, api_map, allowed_description_words):
        for function_name, description in api_map.descriptions_by_function_name.items():
            if function_name in api_map.api_calls_by_function_name:
                function_calls = api_map.api_calls_by_function_name[function_name]
                api_sequence = self.api_sequencer.tokenize_into_list_of_words(function_calls)
                desc_sequence = self.description_sequencer.tokenize_into_list_of_words(description)
                if self.should_map_be_included(function_name, api_sequence, desc_sequence):
                    self.write_pair(api_sequence, desc_sequence, allowed_description_words, description)

    def write_pair(self, api_sequence, desc_sequence, allowed_description_words, description):
        i = self.choose_set()
        self.write_int_pair(i, api_sequence, desc_sequence, allowed_description_words)
        self.write_codebert_pair(i, api_sequence, [description])

    def write_int_pair(self, i, api_sequence, desc_sequence, allowed_description_words):
        api_int_sequence = self.api_sequencer.get_int_sequence_from_list_of_words(api_sequence)
        desc_int_sequence = self.description_sequencer.get_int_sequence_from_list_of_words(
            desc_sequence,
            allowed_description_words
        )
        self.apiseq_dbs[i].add_sequence(api_int_sequence)
        self.desc_dbs[i].add_sequence(desc_int_sequence)

    def write_codebert_pair(self, i, api_sequence, desc_sequence):
        line_dict = {
            "code_tokens": api_sequence,
            "docstring_tokens":  desc_sequence
        }
        self.codebert_dbs[i].write(json.dumps(line_dict) + "\n")

    def choose_set(self):
        r = random.randrange(0, sum(self.weights))
        for i, weight in enumerate(self.weights):
            if r < weight:
                return i
            r -= weight
        return 0

    def close(self):
        for db in self.apiseq_dbs:
            db.close()
        for db in self.desc_dbs:
            db.close()
        for file in self.codebert_dbs:
            file.close()

    def should_map_be_included(self, function_name, api_sequence, desc_sequence):
        if len(desc_sequence) < 3:
            self.removed_for_short += 1
            return False
        name_words = get_description_from_name(function_name).split(" ")
        for word in name_words:
            if word.lower() == "test":
                self.removed_for_test_in_function_name += 1
                return False
        for word in desc_sequence:
            if word.lower() == "test":
                self.removed_for_test_in_desc += 1
                return False
        return True

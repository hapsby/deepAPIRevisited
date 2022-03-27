
import glob
import sys
import os
import shlex
import shutil
import time
from lib.consume_project import consume_project
from lib.ApiSequencer import ApiSequencer
from lib.ApiSequencersByModule import ApiSequencersByModule
from lib.DescriptionSequencer import DescriptionSequencer
from lib.DataSets import DataSets
from lib.ApiMapCache import ApiMapCache
from lib.ApiMapStats import ApiMapStats
from lib.DuplicatePairDetector import DuplicatePairDetector


if len(sys.argv) < 3:
    print("Use:  consume_projects.py </path/to/dbs> </path/to/repos>")
    exit(1)

initial_symbols = ['<pad>', '<s>', '</s>', '<unk>']
api_sequencer = ApiSequencer()
api_sequencer.get_int_sequence_from_list_of_words(initial_symbols)
description_sequencer = DescriptionSequencer()
description_sequencer.get_int_sequence_from_list_of_words(initial_symbols)

os.chdir(sys.argv[1])

data_sets = DataSets(96, 4, 0, api_sequencer, description_sequencer)

apiseq_vocab_file = open("vocab.apiseq.json", "w")
desc_vocab_file = open("vocab.desc.json", "w")

os.chdir(sys.argv[2])

api_map_cache = ApiMapCache()

api_map_stats = ApiMapStats()

for filename in glob.glob('*.7z', recursive=False):
    subdir = filename[:-3]
    try:
        api_map = api_map_cache.load(subdir)
        if api_map is None:
            os.system('"C:/Program Files/7-Zip/7z" x -aoa ' + shlex.quote(filename))
            api_map = consume_project(subdir)
            api_map_cache.save(subdir, api_map)
        else:
            print("Loaded " + subdir + " from cache.")
        api_map_stats.add(api_map.stats)
    except Exception as e:
        print(subdir + " failed: " + str(e))
        if str(e) == "unsupported operand type(s) for +: 'NoneType' and 'str'":
            print("dbg")
        continue
    finally:
        try:
            if os.path.isdir(subdir):
                shutil.rmtree(subdir)
        except Exception:
            time.sleep(1)
            try:
                if os.path.isdir(subdir):
                    shutil.rmtree(subdir)
            except Exception:
                pass
            pass

api_map_stats.print()

api_sequencers_by_module = ApiSequencersByModule()

print("Sorting by module...")

for project_name in api_map_cache.known_projects:
    api_map = api_map_cache.load(project_name)
    if api_map is not None:
        for api_calls in api_map.api_calls_by_function_name.values():
            for api_call in api_calls:
                api_sequencers_by_module.add_api_call(api_call)

allowed_modules = api_sequencers_by_module.get_modules_with_limited_symbols(10000 - 4)
big_description_sequencer = DescriptionSequencer()

print("Finding all description tokens...")

for project_name in api_map_cache.known_projects:
    api_map = api_map_cache.load(project_name)
    if api_map is not None:
        api_map.filter_by_allowed_modules(allowed_modules)
        for description in api_map.descriptions_by_function_name.values():
            big_description_sequencer.tokenize_into_int_sequence(description)

allowed_description_words = big_description_sequencer.get_top_words(10000 - 4)

function_count_1 = 0
function_count_2 = 0
function_count_3 = 0

duplicate_pair_detector = DuplicatePairDetector()

print("Filtering and saving...")

for project_name in api_map_cache.known_projects:
    api_map = api_map_cache.load(project_name)
    if api_map is not None:
        function_count_1 += api_map.count_pairs()
        api_map.filter_by_allowed_modules(allowed_modules)
        function_count_2 += api_map.count_pairs()
        api_map.filter_non_unique(duplicate_pair_detector)
        function_count_3 += api_map.count_pairs()
        data_sets.write_api_map(api_map, allowed_description_words)

api_sequencer.save_to_file(apiseq_vocab_file)
description_sequencer.save_to_file(desc_vocab_file)

print("Pairs before filtering: " + str(function_count_1))
print("Pairs after filtering modules: " + str(function_count_2))
print("Pairs after filtering duplicates: " + str(function_count_3))
print("Pairs removed for short descriptions: " + str(data_sets.removed_for_short))
print("Pairs removed for test in function name: " + str(data_sets.removed_for_test_in_function_name))
print("Pairs removed for test in description: " + str(data_sets.removed_for_test_in_desc))

data_sets.close()



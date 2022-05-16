# Deep API Learning Revisited

This is the code repository for the [Deep API Learning Revisited](https://arxiv.org/abs/2205.01254) paper.  The scripts provided
here are used for collecting and preparing the data sets for the experiments.  The code for
the actual machine learning is found in separate projects.  The RNN experiment was done using
the deepAPI project published by Xiaodong Gu, Hongyu Zhang, Dongmei Zhang, and Sunghun Kim: 

<https://github.com/guxd/deepAPI>

The Transformer experiment was done using the CodeBERT project published by Microsoft:

<https://github.com/microsoft/CodeBERT>


## Data set

You can use the scripts in this repository to create the data set (not trivial), or you can
download the existing data set from [Zenodo](https://zenodo.org/record/6388030).

#### Files used by deepAPI:  

`vocab.apiseq.json`: A JSON file with the vocabulary used in the API sequences.

`vocab.desc.json`: A JSON file with the vocabulary used in the descriptions.

`train.apiseq.h5`: An HDF5 database with all API sequences in the training set.

`test.apiseq.h5`: An HDF5 database with all API sequences in the test set.

`train.desc.h5`: An HDF5 database with all descriptions in the training set.

`test.desc.h5`: An HDF5 database with all descriptions in the test set.

#### Files used by CodeBERT:

`api_train.jsonl`: A JSON file with the entire training set, for use by CodeBERT.

`api_test.jsonl`: A JSON file with the entire test set, for use by CodeBERT.


## Experiments

To run the experiment using the deepAPI code, you have to use the fork of the
deepAPI repository here:

<https://github.com/hapsby/deepAPIPython>

You have to use the fork because the format of the .h5 files is slightly different.

To run the experiment using CodeBERT, you can use this fork of CodeBERT:

<https://github.com/hapsby/CodeBERT-deepAPI>

The following line can be used to train CodeBERT if the datasets are in a subdirectory "codebertdata":

`python run.py --do_train --do_eval --model_type roberta --model_name_or_path microsoft/codebert-base --dev_filename ./codebertdata/api_validate.jsonl --train_filename ./codebertdata/api_train.jsonl --output_dir ./codebertdata --max_source_length 256 --max_target_length 128 --beam_size 10 --train_batch_size 64 --eval_batch_size 64 --learning_rate 5e-5 --train_steps 100000 --eval_steps 1000`




## Scripts

The scripts in this repository can be used to curate the Python data set.

### get_list_of_repos.py

This script is used to scan GitHub for projects that seem suitable for inclusion in the
data set.  The script is designed to be resumable; if you abort the script with ctrl-C and
run it again, it will continue where it left off.

Use: `python get_list_of_repos.py <path-to-repos> <allwords.txt>`

For <allwords.txt> you must specify a list of words that are used to search against the 
GitHub database (I don't know of a better way to get a list of projects from GitHub).  A
list of all words is provided in this project's data repository.

The script writes various files to `<path-to-repos>`:

`list_of_repos.txt`:  The repositories that were found by this tool are written to this
file.  This file can be used directly by the `get_repos.php` script (detailed below), or
you can sort the repositories from highest star to lowest star first using the 
`sort_repos.py` script.

`repos.csv`:  The repositories that were found by this tool are also written to this file,
along with the stars of each repository.  This file can be used with `sort_repos.py` to
produce a list of repos sorted by descending star rating.

`usedwords.txt`: The words from the word list that have already been used are written to
this file.  The file is loaded again if the script is restarted, so that the script resumes
from where it left off.

### sort_repos.py

Use: `python sort_repos.py <path-to-repos>`

This is useful if you do not necessarily plan to download all projects that were found 
by `get_list_of_repos.py`.  This reads `repos.csv`, which was written by
`get_list_of_repos.py`, and outputs `sorted_repos.txt`, which is like `list_of_repos.txt`
except that the highest rated repositories are listed first.

### get_repos.php

Use: `php get_repos.php </path/to/repos> this_part number_of_parts`

This script is used to download the repos in `sorted_repos.txt`, which is output by
`sort_repos.py` above (or you can rename `list_of_repos.txt`, which is output by 
`get_list_of_repos.py`).  The script downloads the projects and creates .7z archives
of the repositories.  You can exit and rerun the script; it will resume where it left off
(although it will repeat the failed downloads first).

If the file `external_repos.txt` is found in the specified path, then this file can be
full of the filenames of the .7z files that already exist (perhaps on another machine).
These repos will not be downloaded.  This can be used to coordinate downloads across
multiple machines.

You can also coordinate downloads across multiple machines by using the `this_part`
and `number_of_parts` arguments.  To download all repositories, set these to 1 and 1:

`php get_repos.php ~/myrepos 1 1`

However, if `number_of_parts` is greater than 1, then the list of repos is partitioned
into that many parts, and only the specified part is downloaded.  For example, you can
have three different computers downloading files at once.  On the first machine:

`php get_repos.php ~/myrepos 1 3`

On the second machine:

`php get_repos.php ~/myrepos 2 3`

On the third machine:

`php get_repos.php ~/myrepos 3 3`

As long as the `number_of_parts` is the same on each computer, and each computer has the
same `sorted_repos.txt`, then the repos are partitioned consistently; hence each
repo is downloaded by exactly one computer.

### consume_projects.py

Use: `consume_projects.py </path/to/dbs> </path/to/repos>`

This script reads the .7z files that were placed in `</path/to/repos>` by `get_repos.php`
and outputs the following database files to `</path/to/dbs>`:



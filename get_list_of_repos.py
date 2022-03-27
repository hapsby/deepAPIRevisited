import pycurl
from io import BytesIO
import json
import sys
import itertools
from lib.Throttler import Throttler
from lib.SetOfStringsInFile import *
import urllib.parse
import random
from lib.GitRepo import GitRepo

per_page = 100


def get_search_url(page, word):
    params = {
        "l": "Python",
        "q": word + " stars:>4 size:<=300000 language:python",
        "per_page": str(per_page),
        "page": str(page)
    }

    url = 'https://api.github.com/search/repositories?' + urllib.parse.urlencode(params)
    return url


def count_lines_in_file(path):
    try:
        file = open(path, "r")
    except FileNotFoundError:
        return 0
    return sum(1 for line in file)


def get_page_of_git_repos(page, word):
    bytes_io = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(curl.URL, get_search_url(page, word))
    curl.setopt(curl.WRITEDATA, bytes_io)
    curl.perform()
    curl.close()
    response_body = bytes_io.getvalue()

    decoded = json.loads(
        response_body.decode('utf8')
    )
    if 'items' not in decoded:
        return []
    repo_urls = []
    for item in decoded['items']:
        if item['size'] > 300000:
            print(item['git_url'] + ": " + str(item['size']))
        else:
            repo_urls.append(GitRepo(item['git_url'], item['stargazers_count']))
    return repo_urls


def get_git_repos(throttler, word):
    all_repo_urls = set()
    for i in itertools.count(0):
        throttler.wait_for_iteration()
        page = i + 1
        print(word + " page " + str(page) + "...")
        git_repos = get_page_of_git_repos(page, word)
        if len(git_repos) == 0:
            break
        all_repo_urls.update(git_repos)
        if len(git_repos) < per_page:
            break
    return all_repo_urls


if len(sys.argv) < 4:
    print("Use: python get_list_of_repos.py <path-to-repos> <allwords.txt>")
    exit(1)


repos_file = SetOfStringsInFile(sys.argv[1] + "/list_of_repos.txt")
repos_csv_file = open(sys.argv[1] + "/repos.csv", "a")
words = read_lines_as_set(sys.argv[2])
used_words_file = SetOfStringsInFile(sys.argv[1] + "/usedwords.txt")

words.difference_update(used_words_file.set_of_strings)

throttler = Throttler(6)    # limit for non-logged-in is 10 requests per minute

while words != set():
    word = random.choice(tuple(words))
    repo_urls = set()
    repo_strings = set()
    for git_repo in get_git_repos(throttler, word):
        if git_repo.url not in repos_file.set_of_strings:
            repo_urls.add(git_repo.url)
            repo_strings.add(str(git_repo))
    repos_file.add_strings(repo_urls)
    repos_csv_file.write("\n".join(repo_strings) + "\n")
    repos_csv_file.flush()
    used_words_file.add_string(word)
    words.remove(word)

repos_file.close()
used_words_file.close()





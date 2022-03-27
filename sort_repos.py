import sys
from lib.GitRepo import GitRepo

if len(sys.argv) < 2:
    print("Use: python sort_repos.py <path-to-repos>")
    exit(1)

file = open(sys.argv[1] + "/repos.csv", 'r')
git_repos = []
for line in file.readlines():
    comma_pos = line.rfind(',')
    if comma_pos != -1:
        url = line[0:comma_pos]
        stars = int(line[comma_pos+1:])
        git_repos.append(GitRepo(url, stars))

git_repos.sort(key=lambda x: -x.stars)
git_urls = []
for git_repo in git_repos:
    git_urls.append(git_repo.url)

file = open(sys.argv[1] + "/sorted_repos.txt", 'w')
file.write("\n".join(git_urls) + "\n")


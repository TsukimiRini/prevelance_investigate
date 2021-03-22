import jieba
import os
from git.repo import Repo
import json

# repo_dir = "/Users/tannpopo/Documents/Study/ChangeLint/repos"
repo_dir = "/home/repos"
word_bags = {}


def computeRepo(repo_name):
    print(8 * '=', "start to handle repo ", repo_name, 8 * '=')
    repo = Repo(os.path.join(repo_dir, repo_name))
    commits = list(repo.iter_commits())

    for idx, commit in enumerate(commits):
        xml_cnt = 0
        kot_jav_cnt = 0

        for file in list(commit.stats.files):
            if len(file) > 4 and file[-4:] == '.xml':
                xml_cnt += 1
            elif len(file) > 3 and file[-3:] == '.kt' or len(
                    file) > 5 and file[-5:] == '.java':
                kot_jav_cnt += 1
        if xml_cnt >= 1 and kot_jav_cnt >= 1:
            for seg in jieba.cut(commit.message.lower(), cut_all=False):
                if len(seg) > 1 and seg != '\t' and seg != '\n':
                    if seg in word_bags:
                        word_bags[seg] += 1
                    else:
                        word_bags[seg] = 1
    print(8 * '=', "repo ", repo_name, "done", 8 * '=')


def goThroughAll():
    repo_list = "/home/yuailun/repo_list"
    with open(repo_list) as list_fd:
        json_obj = json.load(list_fd)
        assert (len(json_obj) == 100)
        for repo in json_obj:
            repo_name = repo["owner"]["login"] + "-" + repo["name"]
            assert (os.path.exists(os.path.join(repo_dir, repo_name)))
            computeRepo(repo_name)

    word_freq = []
    for word, freq in word_bags.items():
        word_freq.append((word, freq))

    word_freq.sort(key=lambda x: x[1], reverse=True)

    with open("bag_of_words_res", 'w') as res_fd:
        for (word, freq) in word_freq:
            res_fd.write("{} {}\n".format(word, freq))


goThroughAll()
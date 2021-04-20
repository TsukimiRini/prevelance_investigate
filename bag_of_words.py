import jieba
import os
from git.repo import Repo
import json
import wordninja
from nltk.corpus import stopwords
from google_trans_new import google_translator
import re
from sys import platform

if platform == "darwin":
    repo_dir = "/Users/tannpopo/Documents/Study/ChangeLint/repo"
if platform == "linux":
    repo_dir = "/home/repos"
plot_dir = "../plots"
word_bags = {}
stop_words = stopwords.words('english')

translator = google_translator()
reg = re.compile(r"[a-zA-z0-9']")

chinese_mst_cnt = 0


def check_contain_chinese(check_str):
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


def checkEng(check_str):
    if reg.match(check_str):
        return True
    return False


def computeRepo(repo_name):
    global chinese_mst_cnt
    shas = set()
    print(8 * '=', "start to handle repo ", repo_name, 8 * '=')
    repo = Repo(os.path.join(repo_dir, repo_name))
    for b in repo.remote().fetch():
        if '/' not in b.name:
            continue
        print("start to check branch {} of {}".format(b.name, repo_name))
        branch_name = b.name.split('/')[1]
        repo.git.checkout('-B', branch_name, b.name)
        commits = list(repo.iter_commits(branch_name))

        for idx, commit in enumerate(commits):
            if str(commit) in shas:
                continue
            else:
                shas.add(str(commit))
            xml_cnt = 0
            kot_jav_cnt = 0

            for file in list(commit.stats.files):
                if len(file) > 4 and file[-4:] == '.xml':
                    xml_cnt += 1
                elif len(file) > 3 and file[-3:] == '.kt' or len(
                        file) > 5 and file[-5:] == '.java':
                    kot_jav_cnt += 1
            if xml_cnt >= 1 and kot_jav_cnt >= 1:
                msg = commit.message
                # msg = str.strip(
                #     translator.translate(msg,
                #                          lang_tgt='en')).lower()
                # print(msg)
                if (check_contain_chinese(msg)):
                    chinese_mst_cnt += 1
                    try:
                        msg = str.strip(
                            translator.translate(msg, lang_tgt='en')).lower()
                    except:
                        print(chinese_mst_cnt)
                        pass
                    seg_list = jieba.cut(msg, cut_all=False)
                    cn = True
                else:
                    seg_list = wordninja.split(commit.message.lower())
                    cn = False
                for seg in seg_list:
                    if cn is True and check_contain_chinese(seg) is False:
                        seg_split_again = wordninja.split(seg)
                        for _seg in seg_split_again:
                            if len(
                                    _seg
                            ) > 1 and _seg != '\t' and _seg != '\n' and _seg != '\r\n' and _seg not in stop_words:
                                if _seg in word_bags:
                                    word_bags[_seg] += 1
                                else:
                                    word_bags[_seg] = 1
                    elif cn is True:
                        if len(
                                seg
                        ) > 1 and seg != '\t' and seg != '\n' and seg != '\r\n' and seg not in stop_words:
                            if seg in word_bags:
                                word_bags[seg] += 1
                            else:
                                word_bags[seg] = 1
                    else:
                        if len(
                                seg
                        ) > 1 and seg != '\t' and seg != '\n' and seg != '\r\n' and seg not in stop_words:
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

    translated_dict = {}
    for word, freq in word_bags.items():
        translated = str.strip(translator.translate(
            word, lang_tgt='en')).lower().split(' ')
        for t in translated:
            if t in translated_dict:
                translated_dict[t] += freq
            else:
                translated_dict[t] = freq
    translated_word_freq = []
    for word, freq in translated_dict.items():
        translated_word_freq.append((word, freq))
    translated_word_freq.sort(key=lambda x: x[1], reverse=True)
    with open("translated_bag_of_words_res", 'w') as res_fd:
        for (word, freq) in translated_word_freq:
            res_fd.write("{} {}\n".format(word, freq))


if platform == "linux":
    goThroughAll()
elif platform == "darwin":
    computeRepo("Auto.js")

print("chinese msg count:", chinese_mst_cnt)
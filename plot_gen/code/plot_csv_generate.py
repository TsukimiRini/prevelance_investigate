import os
from git.repo import Repo
import json
import csv
from sys import platform

if platform == "darwin":
    # work_dir = "/Users/tannpopo/Documents/Study/ChangeLint/repo"
    work_dir = "/Users/tannpopo/Projects"
    csv_dir = "."
elif platform == "linux":
    work_dir = "/home/repos"
    csv_dir = "/home/yuailun/plot_data"

metric_type = ["changed files", "hunks", "added lines", "deleted lines"]

# commit_cnt = 0
# changed_files_cnt = 0
# all_commit_cnt = 0
# all_changed_cnt = 0


def check(repo_name):
    # global commit_cnt
    # global changed_files_cnt
    # global all_commit_cnt
    # global all_changed_cnt

    repo = Repo(os.path.join(work_dir, repo_name))
    commits = list(repo.iter_commits())
    for idx, commit in enumerate(commits):
        if len(commits[idx - 1].parents) > 1:
            continue
        if idx == 0:
            continue
        xml_cnt = 0
        kot_jav_cnt = 0

        # if idx == len(commits)-1:
        file_list = list(commits[idx - 1].stats.files)
        for file in file_list:
            if len(file) > 4 and file[-4:] == '.xml':
                xml_cnt += 1
            elif len(file) > 3 and file[-3:] == '.kt' or len(
                    file) > 5 and file[-5:] == '.java':
                kot_jav_cnt += 1

        patch = repo.git.diff(commit.tree, commits[idx - 1].tree).split('\n')
        hunks_cnt = 0
        added = 0
        deleted = 0
        for line in patch:
            if len(line) >= 2 and line[0] == '@' and line[1] == '@':
                hunks_cnt += 1
            elif len(line) >= 1 and line[0] == '+' and (len(line) < 3
                                                        or line[1] != '+'
                                                        or line[2] != '+'):
                added += 1
            elif len(line) >= 1 and line[0] == '-' and (len(line) < 3
                                                        or line[1] != '-'
                                                        or line[2] != '-'):
                deleted += 1

        commit_type = ""
        if xml_cnt >= 1 and kot_jav_cnt >= 1:
            commit_type = "Multi-lang"
        else:
            commit_type = "Normal"

        with open(os.path.join(csv_dir, metric_type[0] + ".csv"),
                  'a',
                  newline="") as csv_fd:
            csv_writer = csv.writer(csv_fd,
                                    delimiter=',',
                                    quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow([commit_type, len(file_list)])
        if len(file_list) == 0:
            print("!!" + str(commits[idx - 1]))
        with open(os.path.join(csv_dir, metric_type[1] + ".csv"),
                  'a',
                  newline="") as csv_fd:
            csv_writer = csv.writer(csv_fd,
                                    delimiter=',',
                                    quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow([commit_type, hunks_cnt])
        with open(os.path.join(csv_dir, metric_type[2] + ".csv"),
                  'a',
                  newline="") as csv_fd:
            csv_writer = csv.writer(csv_fd,
                                    delimiter=',',
                                    quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow([commit_type, added])
        with open(os.path.join(csv_dir, metric_type[3] + ".csv"),
                  'a',
                  newline="") as csv_fd:
            csv_writer = csv.writer(csv_fd,
                                    delimiter=',',
                                    quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow([commit_type, deleted])
        #     break
        # diff_index = commit.diff(commits[idx+1])

        # for diff_item in diff_index:
        #     if diff_item.a_path[-4:] == '.xml':
        #         xml_cnt += 1
        #     elif diff_item.a_path[-3:] == '.kt' or diff_item.a_path[-5:] == '.java':
        #         kot_jav_cnt += 1
        # if xml_cnt >= 1 and kot_jav_cnt >= 1:
        #     commit_cross += 1
    print("repo {} done".format(repo_name))


def allRepos():
    repo_list = "/home/yuailun/repo_list"
    with open(repo_list) as list_fd:
        json_obj = json.load(list_fd)
        assert (len(json_obj) == 100)
        for repo in json_obj:
            assert (os.path.exists(
                os.path.join(work_dir,
                             repo["owner"]["login"] + "-" + repo["name"])))
            check(repo["owner"]["login"] + "-" + repo["name"])


for t in metric_type:
    with open(os.path.join(csv_dir, t + ".csv"), 'w', newline='') as csv_fd:
        csv_writer = csv.writer(csv_fd,
                                delimiter=',',
                                quotechar='"',
                                quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(["commit type", t + " count"])

if platform == "darwin":
    # check("TeamNewPipe-NewPipe")
    check("three-D-demo-for-self-assembly")
elif platform == "linux":
    allRepos()
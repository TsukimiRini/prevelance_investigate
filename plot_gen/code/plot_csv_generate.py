import os
from git.repo import Repo
import json
import csv
import sys

work_dir = sys.argv[1]
csv_dir = sys.argv[2]
repo_list = sys.argv[3]

metric_type = [
    "changed files", "diff hunks", "added lines", "deleted lines",
    "modified directories"
]

# commit_cnt = 0
# changed_files_cnt = 0
# all_commit_cnt = 0
# all_changed_cnt = 0
multi_lang = 0
other = 0


def check(repo_name):
    # global commit_cnt
    # global changed_files_cnt
    # global all_commit_cnt
    # global all_changed_cnt
    global multi_lang
    global other

    shas = set()
    repo = Repo(os.path.join(work_dir, repo_name))
    for b in repo.remote().fetch():
        if '/' not in b.name:
            continue
        print("start to check branch {} of {}".format(b.name, repo_name))
        # branch_name = b.name.split('/')[1]
        # repo.git.checkout('-B', branch_name, b.name)
        commits = list(repo.iter_commits('remotes/' + b.name))
        for idx, commit in enumerate(commits):
            if str(commit) in shas:
                continue
            else:
                shas.add(str(commit))
            if len(commits[idx - 1].parents) > 1:
                continue
            if idx == 0:
                continue
            xml_cnt = 0
            kot_jav_cnt = 0

            # if idx == len(commits)-1:
            file_list = list(commits[idx - 1].stats.files)
            dir_set = set()
            for file in file_list:
                file = file.split(' => ')[-1]
                dir = file.split('/')[0]
                if dir == file:
                    dir_set.add('.')
                else:
                    dir_set.add(dir)
                if len(file) > 4 and file[-4:] == '.xml':
                    xml_cnt += 1
                elif len(file) > 3 and file[-3:] == '.kt' or len(
                        file) > 5 and file[-5:] == '.java':
                    kot_jav_cnt += 1

            dir_cnt = len(dir_set)

            patch = repo.git.diff(commit.tree,
                                  commits[idx - 1].tree).split('\n')
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
                multi_lang += 1
            else:
                commit_type = "Other"
                other += 1

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
            with open(os.path.join(csv_dir, metric_type[4] + ".csv"),
                      'a',
                      newline="") as csv_fd:
                csv_writer = csv.writer(csv_fd,
                                        delimiter=',',
                                        quotechar='"',
                                        quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow([commit_type, dir_cnt])
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

allRepos()
print("multi-lang:{} other:{}".format(multi_lang, other))
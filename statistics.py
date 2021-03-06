import os
from git.repo import Repo
import json
import xlwt
import sys

work_dir = sys.argv[1]
repo_list = sys.argv[2]
row = 0
wb = xlwt.Workbook(encoding='utf-8')
newsheet = wb.add_sheet('sheet1', cell_overwrite_ok=True)
newsheet.write(row, 0, "repo_name")
newsheet.write(row, 1, "stars")
newsheet.write(row, 2, "total")
newsheet.write(row, 3, "cross")
newsheet.write(row, 4, "percent")

commit_cnt = 0
changed_files_cnt = 0
all_changed_cnt = 0


def check(repo_obj):
    global row
    global commit_cnt
    global changed_files_cnt
    global all_changed_cnt

    repo_name = repo_obj["owner"]["login"] + "-" + repo_obj["name"]
    # print("="*8, "start to check repo ", repo_name, "="*8)
    commit_total = 0
    commit_cross = 0
    percent = 0

    shas = set()
    repo = Repo(os.path.join(work_dir, repo_name))
    for b in repo.remote().fetch():
        if '/' not in b.name:
            continue
        print("start to check branch {} of {}".format(b.name, repo_name))
        branch_name = b.name.split('/')[1]
        repo.git.checkout('-B', branch_name, b.name)
        commits = list(repo.iter_commits('remotes/' + b.name))
        # commit_total = len(commits)
        for idx, commit in enumerate(commits):
            if str(commit) in shas:
                continue
            else:
                shas.add(str(commit))
            if len(commit.parents) > 1:
                continue

            xml_cnt = 0
            kot_jav_cnt = 0

            commit_total += 1

            # if idx == len(commits)-1:
            file_list = list(commit.stats.files)
            all_changed_cnt += len(file_list)
            for file in file_list:
                if len(file) > 4 and file[-4:] == '.xml':
                    xml_cnt += 1
                elif len(file) > 3 and file[-3:] == '.kt' or len(
                        file) > 5 and file[-5:] == '.java':
                    kot_jav_cnt += 1
            if xml_cnt >= 1 and kot_jav_cnt >= 1:
                commit_cnt += 1
                changed_files_cnt += len(file_list)
                commit_cross += 1
            #     break
            # diff_index = commit.diff(commits[idx+1])

            # for diff_item in diff_index:
            #     if diff_item.a_path[-4:] == '.xml':
            #         xml_cnt += 1
            #     elif diff_item.a_path[-3:] == '.kt' or diff_item.a_path[-5:] == '.java':
            #         kot_jav_cnt += 1
            # if xml_cnt >= 1 and kot_jav_cnt >= 1:
            #     commit_cross += 1

    percent = float(commit_cross) / commit_total
    repo_name_full = repo_obj["full_name"]

    # excel
    row += 1
    formula = 'HYPERLINK("{}", "{}")'.format(repo_obj["html_url"],
                                             repo_name_full)
    newsheet.write(row, 0, xlwt.Formula(formula))
    newsheet.write(row, 1, repo_obj["stargazers_count"])
    newsheet.write(row, 2, commit_total)
    newsheet.write(row, 3, commit_cross)
    newsheet.write(row, 4, percent)
    res = "{} Total: {}, Cross: {}, Percent: {}".format(
        repo_name_full, commit_total, commit_cross, percent)
    print(res)
    # print("="*8, "check repo ", repo_name, "completed", "="*8)
    return commit_total, commit_cross, percent


def allRepos():
    with open(repo_list) as list_fd:
        json_obj = json.load(list_fd)
        assert (len(json_obj) == 100)
        for repo in json_obj:
            assert (os.path.exists(
                os.path.join(work_dir,
                             repo["owner"]["login"] + "-" + repo["name"])))
            check(repo)
    newsheet.write(row + 1, 0, "average multilang percentage")
    newsheet.write(row + 1, 1, xlwt.Formula('AVERAGE(E2:E101)'))
    wb.save('stats_res.xls')


allRepos()
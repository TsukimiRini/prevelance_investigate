# coding=utf-8
import os
import json
from pydriller import RepositoryMining

# work_dir = "/Users/tannpopo/Projects"
work_dir = "/home/repos"
stats_dir = "/home/yuailun/cross-lang-commits"
# stats_dir = "/Users/tannpopo/Documents/Study/ChangeLint/stats"

change_type_dict = {
    "MODIFY": "M",
    "ADD": "A",
    "DELETE": "D",
    "RENAME": "R",
    "UNKNOWN": "Unknown"
}


def getCommits(repo_name):
    commits_list = []
    repo = RepositoryMining(os.path.join(work_dir, repo_name), order='reverse')
    commits = list(repo.traverse_commits())
    for idx, commit in enumerate(commits):
        commit_collection = {}
        xml_cnt = 0
        kot_jav_cnt = 0

        file_list = list(commit.modifications)
        for file in file_list:
            filename = file.filename
            if len(filename) > 4 and filename[-4:] == '.xml':
                xml_cnt += 1
                if xml_cnt >= 1 and kot_jav_cnt >= 1:
                    break
            elif len(filename) > 3 and filename[-3:] == '.kt' or len(
                    filename) > 5 and filename[-5:] == '.java':
                kot_jav_cnt += 1
                if xml_cnt >= 1 and kot_jav_cnt >= 1:
                    break
        if xml_cnt >= 1 and kot_jav_cnt >= 1:
            commit_collection["commit_id"] = commit.hash
            commit_collection["commit_msg"] = commit.msg
            commit_collection["commit_time"] = str(commit.committer_date)
            commit_collection["committer_name"] = commit.committer.name
            commit_collection["committer_email"] = commit.committer.email

            diff_files = []
            for file in file_list:
                file_item = {}
                if file.new_path:
                    file_item["file_path"] = file.new_path
                elif file.old_path:
                    file_item["file_path"] = file.old_path
                assert (file_item is not None)
                file_item["change_type"] = change_type_dict[file.change_type.name]
                file_item["lang"] = os.path.splitext(file.filename)[1][1:]
                diff_files.append(file_item)

            commit_collection["diff_files"] = diff_files
            commit_collection["parent_commit_num"] = len(commit.parents)
            commits_list.append(commit_collection)

    repo_dump = json.dumps(commits_list, indent=2, ensure_ascii=False)
    with open(os.path.join(stats_dir, repo_name + "_crossLangCommits"),
              "w") as commit_fd:
        commit_fd.write(repo_dump)
        print(repo_name + " done")


def allRepos():
    repo_list = "/home/yuailun/repo_list"
    with open(repo_list) as list_fd:
        json_obj = json.load(list_fd)
        assert (len(json_obj) == 100)
        for repo in json_obj:
            assert (os.path.exists(
                os.path.join(work_dir,
                             repo["owner"]["login"] + "-" + repo["name"])))
            getCommits(repo["owner"]["login"] + "-" + repo["name"])


allRepos()
# getCommits("three-D-demo-for-self-assembly")
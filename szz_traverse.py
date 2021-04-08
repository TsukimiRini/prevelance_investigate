import os

# list_dir = "/Users/tannpopo/Documents/Study/ChangeLint/szz/issue_lists/bug_introducing_commits"
list_dir = "/home/yuailun/bug_introducing_commits"
system_cmd = 'java -jar {} -i {} -r {} -y {}'
# repo_dir = "/Users/tannpopo/Documents/Study/ChangeLint/repo"
repo_dir = "/home/repos"
jar_path = "/home/yuailun/prevalence/szz_find_bug_introducers-0.1.jar"
res_dir = "/home/yuailun/szz_res"
list_path = "/home/yuailun/prevalence/evet_list"


def traverse():
    with open(list_path, "r") as fd:
        lines = fd.readlines()
        for line in lines:
            owner, filename = str.strip(line).split(" ")
            file_path = os.path.join(list_dir, filename + "_issue.json")
            print(owner, filename, file_path)
            os.system(
                system_cmd.format(
                    jar_path, file_path,
                    os.path.join(repo_dir, owner + "-" + filename),
                    os.path.join(res_dir, filename)))


traverse()
import os
import sys

list_dir = sys.argv[1]
system_cmd = 'java -jar {} -i {} -r {} -y {}'
repo_dir = sys.argv[2]
jar_path = sys.argv[3]
res_dir = sys.argv[4]
list_path = sys.argv[5]


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
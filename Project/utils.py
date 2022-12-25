import VersionExtractor as ve
import os
import sys
import subprocess

def assessThreatScore(l_versions, tested_ver):
    avg = 0
    sum = 0
    count = 0
    for item in l_versions:
        res = ve.isVersionAffected(tested_ver, item[0])
        if res:  # version is affeceted
            count += 1
            if item[1]:
                sum += item[1]  # item[1] contains threat score
    if count:
        avg = sum/count

    return avg

def readLibsFile(file_name):
    with open(file_name) as f:
        lines = f.readlines()
    return lines

def createLibsFile(projectFolder):
    try:
        if not os.path.exists(projectFolder):
            return False,'Project folder does not exist'
        folder = os.path.join(projectFolder,'venv')
        if os.path.exists(folder):
            os.chdir(folder)
        os.system(f'cmd /c "pip freeze > Libs.txt"')
    except Exception as e:
        print(str(e))
        return False,'Something went wrong, please search your Libs manually'
    return True,''

def createListOfLibsVersions(l_file_data):
    l_out = []
    for line in l_file_data:
        l_out.append(line.strip().split('=='))
    return l_out




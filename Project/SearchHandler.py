import os
import _thread
import threading
import pandas as pd
import utils
import nvdlib
import re
import VersionExtractor as ve
from time import sleep
import concurrent.futures
import wx

re_version = '[0-9]+\.[0-9]+\.[0-9]+'
re_version_short = '[0-9]+\.[0-9]*'
API_KEY = '767d34d5-6922-45ab-ae4c-7c7c6e19ffa9'
def searchPKG(name):
    exception = ''
    try:
        l_search_result = nvdlib.searchCVE(keywordExactMatch=True, keywordSearch=name, key=API_KEY, delay=10)
    except Exception as e:
        return [], str(e)

    if len(l_search_result) == 0:
        err_msg = 'Library not found'
        return [], err_msg

    return l_search_result,''

def getVersionsFromDescription(description):
    version = re.findall(re_version, description)
    return version

def getEffectedVersions(versions, description,score):
    l_versions = []
    for ver in versions:
        sentence = ve.get_sentence_with_version(ver, description)
        if len(sentence):
            lowVer = ve.assesVersion(sentence, ve.low_words, ver, True)
            highVer = ve.assesVersion(sentence, ve.high_words, ver, False)
            aVer = ve.getVersion(ver, lowVer, highVer)
            l_versions.append((aVer, score))
    return l_versions

def singleSearch(keyWord, tested_ver):
    # Search for package, return is list of objects
    l_search_result,err_msg = searchPKG(keyWord)
    print(l_search_result)
    print(err_msg)
    score = 0
    maxScore = 0
    data = []

    if err_msg:
        data = [[keyWord,tested_ver,0,err_msg]]
        return pd.DataFrame(data, columns=['Package', 'Version', 'Score', 'Description']), err_msg

    # Prepare list of effected versions
    for item in l_search_result:
        description = item.descriptions[0].value
        score = item.score[1]
        l_versions = getVersionsFromDescription(description)
        l_effected_versions = getEffectedVersions(l_versions, description,score)

        # compare tested version with the effected versions
        for version in l_effected_versions:
            res = ve.isVersionAffected(tested_ver, version[0])
            if res:
                score = item.score[1]
                if score:
                    maxScore = score if score > maxScore else maxScore
                data.append([keyWord, tested_ver, score, description])

    # create output data
    df_out = pd.DataFrame(data, columns=['Package', 'Version', 'Score', 'Description'])

    return df_out,''

# def runSearch(pkg_name,ver):
#     print(pkg_name)
#     df, msg = singleSearch(pkg_name, ver)
#     return df,msg

def runSearch(l_pkg_ver):
    print(l_pkg_ver[0])
    df, msg = singleSearch(l_pkg_ver[0], l_pkg_ver[1])

    return df,msg



def runReqFileSearch(file_name):
    if not os.path.exists(file_name):
        return pd.DataFrame(), f'file {file_name} does not exist'

    lines = utils.readLibsFile(file_name)
    df_out = pd.DataFrame(columns=['Package', 'Version', 'Score', 'Description'])

    # for line in lines:
    #     err_msg = ''
    #     df_pkg_res = pd.DataFrame(columns=['Package', 'Version', 'Score', 'Description'])
    #     l_pkgName_version = line.strip().split('==')
    #     pkgName = l_pkgName_version[0]
    #     version = l_pkgName_version[1]
    #     print(f"Scanning {pkgName}")
    #     df_pkg_res, err_msg = singleSearch(pkgName, version)
    #     print(f"{pkgName} finished")
    #
    #     # _thread.start_new_thread(runSearch,(df_pkg_res, err_msg, pkgName, version))
    #
    #     if not df_pkg_res.empty:
    #         df_out = pd.concat([df_out,df_pkg_res], axis=0, ignore_index=True)
    df_out = runMultiThreadScan(lines)
    return df_out, ''


def createInputList(lines):
    l_out=[]

    for line in lines:
        l_pkgName_version = line.strip().split('==')
        # l_out.append((l_pkgName_version[0],l_pkgName_version[1]))
        l_out.append(l_pkgName_version)
    return l_out

def runMultiThreadScan(lines):
    l_input = createInputList(lines)
    df_out = pd.DataFrame(columns=['Package', 'Version', 'Score', 'Description'])
    if not len(l_input):
        print("No packages and versions was found")
        return df_out

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(runSearch, l_input)

        for df, err_msg in results:
            df_out = df_out.append(df)
    return df_out









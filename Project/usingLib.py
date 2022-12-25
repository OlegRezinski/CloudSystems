import os
import utils
import nvdlib
import re
import VersionExtractor as ve
import pickle
# import pandas as pd


re_version = '[0-9]+\.[0-9]+\.[0-9]+'
re_version_short = '[0-9]+\.[0-9]*'
# r = nvdlib.searchCPE(keywordSearch='pycharm')

# try:
#
#     pickleFile = open('numpy_data','rb')
#     a = pickle.load(pickleFile)
# except Exception as e:
#     a = nvdlib.searchCVE(keywordExactMatch=True, keywordSearch='numpy')
#     numpy_data = open('numpy_data', 'wb')
#     pickle.dump(a, numpy_data)
#     numpy_data.close()

# description =
# description = a[0].descriptions[0].value

# res = re.search(re_version,description)
# r = nvdlib.searchCPE(cpeNameId='006F2182-A4A3-441C-8C71-5DDB125FE8AB')
def main(keyWord, tested_ver):
    err_msg = ''
    # df_res = pd.DataFrame(columns=['Name', 'Version', 'Description', 'Effected'])
    # data = []

    if not keyWord:
        return 0, 'Library cannot be empty'
    if not tested_ver:
        return 0, 'Version cannot be empty'

    l_search_result = nvdlib.searchCVE(keywordExactMatch=True, keywordSearch=keyWord)

    if len(l_search_result) == 0:
        err_msg = 'Library not found'
        return 0,err_msg

    l_versions = []
    for item in l_search_result:
        description = item.descriptions[0].value
        score = item.score[1]
        version = re.findall(re_version,description)
        # print(f"description:\n{description}\nVersion:{version}")
        version_short = re.findall(re_version_short,description)
        # print(f"description:\n{description}\nVersion:{version}")

        for ver in version:
            l = [vs in ver for vs in version_short]

            if True in l:
                # l_versions.append(ver)
                sentence = ve.get_sentence_with_version(ver, description)
                if len(sentence):
                    lowVer = ve.assesVersion(sentence, ve.low_words, ver, True)
                    highVer = ve.assesVersion(sentence, ve.high_words, ver,  False)
                    aVer = ve.getVersion(ver, lowVer, highVer)
                    l_versions.append((aVer,score))
            else:
                l_versions.append((version_short,score))

        print(f"description:\n{description}\nVersion:{l_versions}")

    for item in l_versions:
        res = ve.isVersionAffected(tested_ver,item[0])
        msg = f'Version version is affected. Threat score = {item[1]}' if res else 'version is safe'
        print(f'tested version = {tested_ver}, versions in danger {item[0]}\nTested {msg}' )

    avg = utils.assessThreatScore(l_versions, tested_ver)
    print(f'{keyWord} {tested_ver} threat score is {avg}')
    return avg, err_msg


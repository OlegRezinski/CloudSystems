
high_words = ['later', 'new', 'newer', 'follow', 'followed', 'following', 'low', 'lower']
low_words = ['older', 'old', 'before', 'prior', 'young', 'younger', 'high', 'higher', 'large', 'larger']


def get_sentence_with_version(ver, description):
    '''
    :param ver: verison as string, example '1.13.1'
    :param description: string
    :return: list of strings
    '''
    left_part = []
    right_part = []
    l_sentences = description.split(ver)
    if len(l_sentences)>1:
        left = l_sentences[0].split('.')
        right = l_sentences[1].split('.')
        for l in left:
           if l:
               left_part.append(l)
        for r in right:
            if r:
                right_part.append(r)

        try:
            l = left_part[-1] if len(left_part) else ''
            r = right_part[0] if len(right_part) else ''
            # res = left_part[-1] + right_part[0]
            res = l + r
        except:
            print('stoppped')
        return res
    return []

def assesVersion(sentence,l_words, ver, isLow):
    s = sentence.lower()
    l_res = [word in s for word in l_words]
    sign = '<' if isLow else '>'
    if True in l_res:
        return f'{sign}{ver}'
    return ver

def getVersion(ver,aVer,bVer):
    if ver==aVer and ver==bVer:
        return ver
    if ver==aVer:
        return bVer
    return aVer

def compareVersions(ver1, ver2):
    ver1 = cleanVersion(ver1)
    ver2 = cleanVersion(ver2)

    ver1 = ver1.split('.')
    ver2 = ver2.split('.')
    len1 = len(ver1)
    len2 = len(ver2)

    if len1 == len2:
        shorter = 0
        min_length = len1
    if len1 < len2:
        shorter = -1
        min_length = len1
    if len1 > len2:
        shorter = 1
        min_length = len2

    for i in range(min_length):
        num1 = convreteStrVerPartToInt(ver1[i])
        num2 = convreteStrVerPartToInt(ver2[i])

        if num1 < num2:
            return -1
        if num1 > num2:
            return 1

    if shorter < 0:
        return -1
    if shorter > 0:
        return 1
    return 0

def cleanVersion(ver):
    ver = ver.strip()
    ver = ver.strip('<')
    ver = ver.strip('>')
    return ver

def convreteStrVerPartToInt(strNum):
    try:
        num = int(strNum)
    except ValueError:  # that means that version is like '1.9.x'
        num = 9
    return num

def isVersionAffected(s_aVer, s_ver):
    action = s_ver[0]  # '<' or '>'
    res = compareVersions(s_aVer, s_ver)

    if action != '>' and action != '<':
        if s_ver[-1]=='x' and res <= 0:
            return True
        if res == 0:
            return True
        else:
            return False
    else:
        if action == '>' and res >= 0:
            return True
        if action == '>' and res < 0:
            return False
        if action == '<' and res > 0:
            return False
        if action == '<' and res <= 0:
            return True


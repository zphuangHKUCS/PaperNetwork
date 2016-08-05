import nltk
from nltk.stem.lancaster import LancasterStemmer
import io

def findall(s, sub):
    ret = []
    start = 0
    while True:
        index = s.find(sub, start)
        if index == -1:
            return ret
        else:
            ret.append(index)
            start = index + 1

def removeSpace(text):
    lines = text.strip().split('\n')
    for i in range(0, len(lines)):
        lines[i] = lines[i].strip()
    ret = ''
    endWithLine = 0
    for i in range(0, len(lines)):
        line = lines[i].strip()
        if len(line) == 0:
            endWithLine =0
            continue
        if endWithLine == 0:
            ret += ' '

        if line[len(line) - 1] == '-':
            endWithLine = 1
            line = line[0:-1]
        else:
            endWithLine = 0
        ret += line
    ret = ret.strip()
    return ret

def getAbstract(rawText):
    lowerText = rawText.lower()
    start = lowerText.find('abstract')
    if start == -1:
        return u''
    keyword = lowerText.find('keyword', start)
    introduction = lowerText.find('introduction')
    if keyword == -1:
        keyword = 99999
    end = min(keyword, introduction)
    if end < start:
        print 'Error. No keyword and no introduction'
        # print rawText
        return u''
    return removeSpace(rawText[start + 8:end])

def getConclusion(rawText):
    lowerTxt = rawText.lower()
    condlusionStarts = findall(lowerTxt, 'conclusion')
    referenceStarts = findall(lowerTxt, 'reference')
    if len(condlusionStarts) == 0:
        return ''
    dist = 99999
    bestEnd = -1
    bestStart = -1
    for conStart in condlusionStarts:
        refStart = lowerTxt.find('reference', conStart)
        ackStart = lowerTxt.find('acknowledg', conStart)
        if ackStart == -1:
            ackStart = refStart
        refStart = min(refStart,ackStart)
        if refStart == -1:
            continue
        if 'do not necessarily reflect those of' in removeSpace(rawText[conStart: refStart]):
            continue
        if refStart - conStart < dist:
            bestEnd = refStart
            bestStart = conStart
            dist = refStart - conStart
    if bestEnd == -1:
        return ''
    # print 'The conclusion is:'
    # print rawText[bestStart + len('conclusion'):bestEnd]
    bestStart = lowerTxt.find('\n', bestStart)
    # if rawText[bestStart + len('conclusion')] in ['s','S']:
    #     return removeSpace(rawText[bestStart + len('conclusions'):bestEnd])
    return removeSpace(rawText[bestStart:bestEnd])

def getReferenceStartEndPlace_ACM(s):
    startCandidates = findall(s, 'reference')
    if len(startCandidates) == 0:
        return [-1, -1]
    theBestStart = -1
    minDist = 999999
    for i in range(0, len(startCandidates)):
        index = s.find('[1]', startCandidates[i])
        dist = index - startCandidates[i]
        if dist > 0 and dist <= minDist:
            minDist = dist
            theBestStart = startCandidates[i]
    if theBestStart == -1:
        # not a reasonable start place for reference
        return [-1, -1]
    numofRef = 1
    endPlace = theBestStart
    while True:
        nextPlace = s.find('[' + str(numofRef) + ']', endPlace)
        if nextPlace != -1:
            endPlace = nextPlace
            numofRef += 1
        else:
            break

    while True:
        nextPlace = s.find('\r\n', endPlace + 1)
        #print s[nextPlace - 1]
        if nextPlace == -1 or s[nextPlace - 1] == '.':
            endPlace = nextPlace
            break
        else:
            endPlace = nextPlace
    return [theBestStart, endPlace]

def getReferenceText(rawText):
    lowerTxt = rawText.lower()
    [start, end] = getReferenceStartEndPlace_ACM(lowerTxt)
    return rawText[start:end]

def removeStopWords_Stemming(rawTxt, stemmer = LancasterStemmer()):
    # print 'The input text is:'
    # print rawTxt
    ret = u''
    lowerTxt = rawTxt.lower()
    tokens = nltk.word_tokenize(lowerTxt)

    filtered_words = [word for word in tokens if word not in nltk.corpus.stopwords.words('english')]
    if len(filtered_words) == 0:
        return u''
    ret += stemmer.stem(filtered_words[0])
    for i in range(1, len(filtered_words)):
        theStemWord = stemmer.stem(filtered_words[i])
        if len(theStemWord) == 0:
            continue
        if theStemWord in [',', '.', ' ','!','?', '\t', '\n', '\r', '\r\n', '\n\r', ':', '', '(', ')', '\'s', '-', '[', ']']:
            continue
        try:
            theStr = theStemWord.encode('ascii')
            # print theStr
        except:
            # print 'The error lien is'
            # print theStemWord
            continue

        if theStemWord.isdigit():
            continue
        ret += u':'
        #print[stemmer.stem(filtered_words[i])]
        ret += theStemWord

    # print ret
    return ret
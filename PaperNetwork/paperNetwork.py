import codecs
import pickle
import copy
import _heapq
import heapq
import fibonacci_heap_mod
from config import *
from RawTxtHandler import *


class Reference:
    def __init__(self):
        self.title_ = ''
        self.text_ = ''
        self.year_ = ''
    def __init__(self, s):
        fullText = removeSpace(s)
        self.text_ = fullText
        partitions = fullText.split('.')
        longestString = ''
        for s in partitions:
            s = s.strip()
            flag = 0
            for year in range(1970, 2016):
                if str(year) in s:
                    self.year_ = year
                    flag = 1
            if flag == 1:
                continue
            if len(s) > len(longestString):
                longestString = s
        self.title_ = longestString

class Paper:
    def __init__(self):
        self.key_ = ''
        self.title_ = ''
        self.authors_ = []
        self.venue_ = ''
        self.cite_ = []
        self.citeby_ = []

        self.topics_ = []

    def getReference(self):
        rawText = self.getRawTxt()
        refTxt = getReferenceText(rawText)
        index = 1
        ref = []
        while True:
            startPlace = refTxt.find('[' + str(index) + ']')
            if startPlace == -1:
                break
            index += 1
            endPlace = refTxt.find('[' + str(index) + ']')
            if endPlace == -1:
                endPlace = len(refTxt)
            ref.append(Reference(refTxt[startPlace:endPlace]))
        return ref


    def getRawPath(self):
        return RAW_TEXT_DIR + '\\' + self.key_ + '.raw'

    def getRawTxt(self):
        rawPath = self.getRawPath()
        with codecs.open(rawPath,encoding='utf-8', errors='ignore') as rawFile:
            return rawFile.read()

    def getLDAInputTxt(self):
        rawTxt = self.getRawTxt()

        title = self.title_
        abs = getAbstract(rawTxt)
        # print 'The abs is:'
        # print abs
        conclusion = getConclusion(rawTxt)
        # print 'The conclusion is:'
        # print conclusion
        return title + u' ' + abs + u' ' + conclusion

    def getBagOfWordsLine(self):
        ret = u''
        if len(self.authors_) > 0:
            ret += self.authors_[0]
            for i in range(1, len(self.authors_)):
                ret += u':'
                ret += self.authors_[i]
        ret += u'\t'

        LDAinputTxt = self.getLDAInputTxt()
        bagofwords = removeStopWords_Stemming(LDAinputTxt)
        ret += bagofwords
        # print ret
        return ret

class PaperNetwork:
    def __init__(self):
        self.key2paper_ = dict()

        # reverse indexes
        self.venue2key_ = dict()
        self.author2key_ = dict()
        self.topic2key_ = dict()

    def readRawPaperFile(self, path):
        # read venue short name first
        venue2short = dict()
        with codecs.open(VENUE_SHORT_PATH,encoding='utf-8',errors='ignore') as venue2shortFile:
            for line in venue2shortFile:
                strs = line.strip().split('\t')
                venue2short[strs[0]] = strs[1]
                #print strs
        # read the paper raw files
        with codecs.open(path,encoding='utf-8',errors='ignore') as raw_paper_file:
            lines = raw_paper_file.readlines()
        for i in range(0, len(lines), 7):
            key = lines[i].strip()
            # print line
            title = lines[i + 2].strip()
            venue = venue2short[lines[i + 3].strip()]
            #print venue
            authors = lines[i + 4].strip().split('\t')
            cite = lines[i + 5].strip().split('\t')
            citeby = lines[i + 6].strip().split('\t')

            tempPaper = Paper()
            [tempPaper.key_, tempPaper.title_, tempPaper.venue_, tempPaper.authors_, tempPaper.cite_, tempPaper.citeby_] = [key, title, venue, authors, cite, citeby]
            tempPaper.topics_ = title.split(' ')
            tempPaper.fullVenue_ = lines[i + 3].strip()
            # print tempPaper.topics_
            self.key2paper_[key] = tempPaper
        # build the reverse index
        for key in self.key2paper_:
            thePaper = self.key2paper_[key]
            # author2key
            for author in thePaper.authors_:
                if author not in self.author2key_:
                    self.author2key_[author] = []
                self.author2key_[author].append(key)
            # topic2key
            for topic in thePaper.topics_:
                if topic not in self.topic2key_:
                    self.topic2key_[topic] = []
                self.topic2key_[topic].append(key)
            # venue2key
            venue = thePaper.venue_
            if venue not in self.venue2key_:
                self.venue2key_[venue] = []
            self.venue2key_[venue].append(key)

    def saveToPickle(self, path):
        pfile = open(path, 'wb')
        pickle.dump(self,pfile)

    def showInfo(self):
        for key in self.key2paper_:
            thePaper = self.key2paper_[key]
            simDict = dict()


    def propagation_cite(self):
        print 'Start propogation.'
        # return the result dicts

        node2entry = dict()
        staticInk = dict()
        for key in self.key2paper_:
            staticInk[key] = dict()
        activeInk = fibonacci_heap_mod.Fibonacci_heap()

        #initialize the active ink
        for key in self.key2paper_:
            thePaper = self.key2paper_[key]
            for author in thePaper.authors_:
                tempNode = key + u'\t' +author
                entry = activeInk.enqueue(tempNode, -1.0 / len(thePaper.authors_))
                node2entry.update({tempNode:entry})
                #node2entry[tempNode] = entry

        #start propogation
        printCount = 0
        while activeInk.m_size > 0:
            printCount += 1

            topnode = activeInk.min()
            activeInk.dequeue_min()
            node = topnode.get_value()
            paperKey = node.split('\t')[0]
            authorName = node.split('\t')[1]
            # print [paperKey, authorName]
            if not node2entry.has_key(node):
                print 'node not in heap!'
                continue
            node2entry.pop(node)
            weight = -topnode.get_priority()

            if printCount == 10000:
                printCount = 0
                print 'size:' + (str)(activeInk.m_size) + '\t' + 'weight:' + '\t' + (str)(weight)

            if weight < PPR_THRESHOLD:
                # the weight is too small to continue
                break

            # print (str)(weight) + '\t' + thePaper.title_
            # print paperKey
            if not staticInk[paperKey].has_key(authorName):
                staticInk[paperKey][authorName] = (1.0 - PPR_ALPHA) * weight
            else:
                staticInk[paperKey][authorName] += (1.0 - PPR_ALPHA) * weight

            thePaper = self.key2paper_[node.split('\t')[0]]
            # if thePaper.fullVenue_ in testVenues:
            #     print 'HIT a test paper!'
            #     print staticInk[paperKey]
            if len(thePaper.citeby_) == 0:
                continue

            nextIncreaseWeight = PPR_ALPHA * weight / len(thePaper.citeby_)

            totalWeight = 0.0
            for nextPaper in thePaper.citeby_:
                if nextPaper == '':
                    continue
                totalWeight += product(self.key2paper_[nextPaper].topicVec_, thePaper.topicVec_)

            for nextPaper in thePaper.citeby_:
                if nextPaper == '':
                    continue
                tempnode = nextPaper + u'\t' + authorName
                if node2entry.has_key(tempnode):
                    tempentry = node2entry[tempnode]
                    # activeInk.decrease_key(tempentry, tempentry.get_priority() - nextIncreaseWeight)
                    activeInk.decrease_key(tempentry, tempentry.get_priority() - PPR_ALPHA *weight* product(self.key2paper_[nextPaper].topicVec_, thePaper.topicVec_) / totalWeight)
                else:
                    # tempentry = activeInk.enqueue(tempnode, -nextIncreaseWeight)
                    tempentry = activeInk.enqueue(tempnode, -PPR_ALPHA *weight* product(self.key2paper_[nextPaper].topicVec_, thePaper.topicVec_)/totalWeight)
                    node2entry[tempnode] = tempentry
        print 'End propogation.'
        return staticInk

    def getTMatrix_LDA(self, author2topic, topic2word):
        TMatrix = dict()
        for key in self.key2paper_:
            TMatrix[key] = dict()
            thePaper = self.key2paper_[key]
            sums = 0.0
            for nextKey in thePaper.citeby_:
                if nextKey not in self.key2paper_:
                    continue
                if nextKey == key:
                    continue
                TMatrix[key][nextKey] = pow(product(thePaper.topicVec_, self.key2paper_[nextKey].topicVec_), 0)
                TMatrix[key][nextKey] = max(0.0, TMatrix[key][nextKey])
                sums += TMatrix[key][nextKey]
            if sums != 0.0:
                for nextKey in thePaper.citeby_:
                    if nextKey not in self.key2paper_:
                        continue
                    if nextKey == key:
                        continue
                    TMatrix[key][nextKey] /= sums
            else:
                for nextKey in thePaper.citeby_:
                    if nextKey not in self.key2paper_:
                        continue
                    if nextKey == key:
                        continue
                    TMatrix[key][nextKey] = 1.0 / len(thePaper.citeby_)
            print TMatrix[key]

        return TMatrix

    def propagation_matrix(self, testVenues, matrix):
        print 'Start propogation.'
        # return the GT and the result dicts
        GT = dict()
        # remove the ground truth for the test data
        for key in self.key2paper_:
            thePaper = self.key2paper_[key]
            if thePaper.fullVenue_ in testVenues:
                GT[key] = []
                for author in thePaper.authors_:
                    GT[key].append(author)
                # print GT[key]
                thePaper.authors_ = []

        node2entry = dict()
        staticInk = dict()
        for key in self.key2paper_:
            staticInk[key] = dict()
        activeInk = fibonacci_heap_mod.Fibonacci_heap()

        #initialize the active ink
        for key in self.key2paper_:
            thePaper = self.key2paper_[key]
            for author in thePaper.authors_:
                tempNode = key + u'\t' +author
                entry = activeInk.enqueue(tempNode, -1.0 / len(thePaper.authors_))
                node2entry.update({tempNode:entry})
                #node2entry[tempNode] = entry

        #start propogation
        printCount = 0
        while activeInk.m_size > 0:
            printCount += 1

            topnode = activeInk.min()
            activeInk.dequeue_min()
            node = topnode.get_value()
            paperKey = node.split('\t')[0]
            authorName = node.split('\t')[1]
            # print [paperKey, authorName]
            if not node2entry.has_key(node):
                print 'node not in heap!'
                continue
            node2entry.pop(node)
            weight = -topnode.get_priority()

            if printCount == 10000:
                printCount = 0
                print 'size:' + (str)(activeInk.m_size) + '\t' + 'weight:' + '\t' + (str)(weight)

            if weight < PPR_THRESHOLD:
                # the weight is too small to continue
                break

            # print (str)(weight) + '\t' + thePaper.title_
            # print paperKey
            if not staticInk[paperKey].has_key(authorName):
                staticInk[paperKey][authorName] = (1.0 - PPR_ALPHA) * weight
            else:
                staticInk[paperKey][authorName] += (1.0 - PPR_ALPHA) * weight

            thePaper = self.key2paper_[node.split('\t')[0]]
            # if thePaper.fullVenue_ in testVenues:
            #     print 'HIT a test paper!'
            #     print staticInk[paperKey]
            if len(thePaper.citeby_) == 0:
                continue

            for nextPaper in thePaper.citeby_:
                if nextPaper not in self.key2paper_:
                    continue
                if nextPaper not in matrix[paperKey]:
                    continue
                nextIncreaseWeight = PPR_ALPHA * weight * matrix[paperKey][nextPaper]

                tempnode = nextPaper + u'\t' + authorName
                if node2entry.has_key(tempnode):
                    tempentry = node2entry[tempnode]
                    # print [tempentry.get_priority(), nextIncreaseWeight]
                    activeInk.decrease_key(tempentry, tempentry.get_priority() - nextIncreaseWeight)
                else:
                    tempentry = activeInk.enqueue(tempnode, -nextIncreaseWeight)
                    node2entry[tempnode] = tempentry
        print 'End propogation.'
        return [GT, staticInk]

    def guessAuthor_mostCite(self, testPapers):
        ret = dict()
        for key in testPapers:
            thePaper = self.key2paper_[key]
            resultDict = dict()
            for nextKey in thePaper.cite_:
                if nextKey not in self.key2paper_ or nextKey == '':
                    continue
                nextPaper = self.key2paper_[nextKey]
                for author in nextPaper.authors_:
                    if author not in resultDict:
                        resultDict[author] = 0
                    resultDict[author] += 1.0  / len(nextPaper.citeby_)
            ret[key] = resultDict
        return ret

    def guessAuthor_citeRank(self, testPapers):
        ret = dict()
        for key in testPapers:
            thePaper = self.key2paper_[key]

            resultDict = dict()
            refs = thePaper.getReference()
            title2ref = dict()
            for ref in refs:
                title2ref[ref.title_.lower()] = ref
            for nextKey in thePaper.cite_:
                if nextKey not in self.key2paper_:
                    continue
                if self.key2paper_[nextKey].title_.lower() not in title2ref:
                    refTimes = 1
                else:
                    rawTxt = thePaper.getRawTxt()
                    ref = title2ref[self.key2paper_[nextKey].title_.lower()]
                    ref_bracket = ref.text_[0:ref.text_.find(']')+1]
                    # print ref_bracket
                    refTimes = len(findall(rawTxt, ref_bracket))
                # print refTimes
                nextPaper = self.key2paper_[nextKey]
                for author in nextPaper.authors_:
                    if author not in resultDict:
                        resultDict[author] = 0
                    resultDict[author] += (refTimes + 0.0) / len(nextPaper.citeby_)
            ret[key] = resultDict
        return ret

    def removeGT(self, testPapers, authorPool):
        GT = dict()
        for key in self.key2paper_:
            thePaper = self.key2paper_[key]
            if key not in testPapers:
                continue
            GT[key] = []
            for a in thePaper.authors_:
                if a in authorPool:
                    GT[key].append(a)
            thePaper.authors_ = []
        return GT

def readTextVenues(path):
    ret = []
    with codecs.open(path,encoding='utf-8', errors='ignore') as venueFile:
        for line in venueFile:
            venue = line.strip()
            ret.append(venue)
    return ret

def evaluate(GT, result):
    for k in [1, 5, 10, 50, 100]:
        total = 0
        hit = 0
        for key in result:
            if key not in GT:
                continue
            topkList = heapq.nlargest(k, result[key], key=result[key].__getitem__)
            total += 1
            flag = 0
            # print GT[key]
            # print topkList
            # print result[key]
            # print ''
            for author in topkList:
                if author in GT[key]:
                    flag = 1
                    break
            if flag == 1:
                hit += 1
        print [k,total,hit]

def loadLDA(thetapath, phipath):
        author2vector = dict()
        with codecs.open(thetapath,encoding='utf-8',errors='ignore') as thetaFile:
            for line in thetaFile:
                strs = line.strip().split('\t')
                # print line
                if len(strs) < 3:
                    continue
                author = strs[0]
                topic = strs[1]
                pro = float(strs[2])
                if author not in author2vector:
                    author2vector[author] = dict()
                author2vector[author][topic] = pro

        topic2word =dict()
        with codecs.open(phipath, encoding='utf-8', errors='ignore') as phiFile:
            for line in phiFile:
                strs = line.strip().split('\t')
                if len(strs) < 3:
                    continue
                topic = strs[0]
                word = strs[1]
                pro = float(strs[2])
                if topic not in topic2word:
                    topic2word[topic] = dict()
                topic2word[topic][word] = pro
        return [author2vector, topic2word]

def getPaperVector(topic2word, word2frequency):
    # the vector to be returned
    pi = dict()
    for t in topic2word:
        pi[t] = 1.0 / len(topic2word)

    w_t = dict()
    for w in word2frequency:
        w_t[w] = dict()
        for t in topic2word:
            w_t[w][t] = 1.0 / len(topic2word)

    for iteration in range(0, 2000):
        for w in word2frequency:
            if w not in topic2word[t]:
                continue
            sum = 0
            for t in topic2word:
                # print pi[t]
                # print topic2word[t][w]
                w_t[w][t] = pi[t] * topic2word[t][w]
                sum += w_t[w][t]

            for t in topic2word:
                w_t[w][t] /= sum
        # update pi
        sum = 0
        for t in topic2word:
            pi[t] = 0
            for w in word2frequency:
                pi[t] += w_t[w][t] * word2frequency[w]
            sum += pi[t]
        for t in topic2word:
            pi[t] /= sum

    return pi

def getWord2Frequency(paperLine):
    # Stanford University, Stanford, CA program:analys:increas:us:softw:engin:task:audit:program:sec:vuln:find:er:gen:.:such:tool:oft:requir:analys:much:soph:tradit:us:compil:optim:.:in:particul:,:context-sensitive:point:alia:inform:prerequisit:sound:prec:analys:reason:us:heap:object:program:.:context-sensitive:analys:challeng:1014:context:typ:larg:program:,:ev:recurs:cyc:collaps:.:moreov:,:point:resolv:gen:without:analys:entir:program:.:thi:pap:pres:new:framework:,:bas:conceiv:deduc:databas:,:context-sensitive:program:analys:.:in:framework:,:program:inform:stor:rel:;:dat:access:analys:writ:datalog:query:.:to:handl:larg:numb:context:program:,:databas:repres:rel:bin:decid:diagram:(:bdds:):.:the:system:develop:,:cal:bddbddb:,:autom:transl:databas:query:high:optim:bdd:program:.:our:prelimin:expery:suggest:larg:class:analys:involv:heap:object:describ:succinct:datalog:impl:efficy:bdds:.:to:mak:develop:application-specific:analys:easy:program:,:also:cre:langu:cal:pql:mak:subset:datalog:query:intuit:defin:.:we:us:langu:find:many:sec:hol:web:apply:.:1:.

    paperLine = paperLine.strip()
    strs = paperLine.split('\t')
    if len(strs) == 1:
        wordTxt = strs[0]
    elif len(strs) == 2:
        wordTxt = strs[1]
    else:
        return None
    words = wordTxt.split(':')
    word2frequency = dict()
    for w in words:
        if len(w) == 0:
            continue
        if w not in word2frequency:
            word2frequency[w] = 0
        word2frequency[w] += 1
    return word2frequency

def product(v1, v2):
    sum = 0.0
    for i in v1:
        if i in v2:
            sum += v1[i] * v2[i]
    return sum
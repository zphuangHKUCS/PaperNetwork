from paperNetwork import *

from meta import *

def testLDA(network, testVenues, author2topic, topic2word):
    result = dict()
    for key in network.key2paper_:
        thePaper = network.key2paper_[key]
        if thePaper.fullVenue_ not in testVenues:
            continue
        paperLine = thePaper.getBagOfWordsLine()
        word2fre = getWord2Frequency(paperLine)
        paperVector = getPaperVector(topic2word,word2fre)
        result[key] = paperVector
    outFile = open('./LDAresult_T20', 'wb')
    pickle.dump(result,outFile)



def evaluate_LDA(network, testVenues, author2topic, topic2word):
    pfile = open('./LDAresult_T30', 'rb')
    paper2vec = pickle.load(pfile)


    similarityDict = dict()
    for key in paper2vec:
        similarityDict[key] = dict()
        for author in author2topic:
            similarityDict[key][author] = product(author2topic[author], paper2vec[key])

    for k in [1, 5, 10, 50, 100]:
        hit = 0
        total = 0
        for key in similarityDict:
            topkList = heapq.nlargest(k, similarityDict[key], key=similarityDict[key].__getitem__)
            total += 1
            flag = 0
            # print GT[key]
            # print topkList
            # print result[key]
            # print ''
            GT = network.key2paper_[key].authors_
            for author in topkList:
                if author in GT:
                    flag = 1
                    break
            if flag == 1:
                hit += 1
        print [k,total,hit]

def calHit(GT, results, k):
    hit = 0
    sortedList = heapq.nlargest(k,results, key=results.__getitem__)
    for item in sortedList:
        if item in GT:
            hit += 1
            break
    return hit

def exp_metapath(network, testPapers, authorPool):
    GT = network.removeGT(testPapers, authorPool)

    metapath_PPA = MetaPath(network,['cite', 'writeby'])
    metapath_PVPA = MetaPath(network,['publishby','publish', 'writeby'])
    metapath_PTPA = MetaPath(network,['mention','mentionby', 'writeby'])

    total = 0

    [hit_PCPPA, hit_PCPVPA, hit_PCPTPA, hit_PCRWPPA, hit_PCRWPVPA, hit_PCRWPTPA] = [dict(),dict(),dict(),dict(),dict(),dict()]
    for k in [1, 5, 10, 50, 100]:
        for l in [hit_PCPPA, hit_PCPVPA, hit_PCPTPA, hit_PCRWPPA, hit_PCRWPVPA, hit_PCRWPTPA]:
            l[k] = 0

    for key in testPapers:
        thePaper = network.key2paper_[key]

        pc_PPA = metapath_PPA.calPathCount(key)
        pcrw_PPA = metapath_PPA.calPCRW(key)

        pc_PVPA = metapath_PVPA.calPathCount(key)
        pcrw_PVPA = metapath_PVPA.calPCRW(key)

        pc_PTPA = metapath_PTPA.calPathCount(key)
        pcrw_PTPA = metapath_PTPA.calPCRW(key)

        total += 1
        for k in [1, 5, 10, 50, 100]:
            hit_PCPPA[k] += calHit(GT[key],pc_PPA, k)
            hit_PCPVPA[k] += calHit(GT[key],pc_PVPA, k)
            hit_PCPTPA[k] += calHit(GT[key],pc_PTPA, k)
            hit_PCRWPPA[k] += calHit(GT[key],pcrw_PPA, k)
            hit_PCRWPVPA[k] += calHit(GT[key],pcrw_PVPA, k)
            hit_PCRWPTPA[k] += calHit(GT[key],pcrw_PTPA, k)
    print total
    print [hit_PCPPA, hit_PCPVPA, hit_PCPTPA, hit_PCRWPPA, hit_PCRWPVPA, hit_PCRWPTPA]

def exp_mostCited(network, testPapers, authorPool):
    GT = network.removeGT(testPapers, authorPool)
    mostCiteResult = network.guessAuthor_mostCite(testPapers)
    hit = dict()
    for k in [1, 5, 10, 50, 100]:
        hit[k] = 0
        total = 0
        for key in mostCiteResult:
            hit[k] += calHit(GT[key], mostCiteResult[key], k)
            total += 1
    print total
    print hit

def loadPaperAuthorID():
    testPapers = []
    authorPool = []
    with codecs.open(TEST_PAPER_PATH,encoding='utf-8',errors='ignore') as testPaperFile:
        for line in testPaperFile:
            testPapers.append((line.strip()))
    with codecs.open(AUTHOR_POOL_PATH,encoding='utf-8',errors='ignore') as authorFile:
        for line in authorFile:
            authorPool.append(line.strip())
    return [testPapers, authorPool]

def exp_citeRank(network, testPapers, authorPool):
    GT = network.removeGT(testPapers, authorPool)
    mostCiteResult = network.guessAuthor_citeRank(testPapers)
    hit = dict()
    for k in [1, 5, 10, 50, 100]:
        hit[k] = 0
        total = 0
        for key in mostCiteResult:
            hit[k] += calHit(GT[key], mostCiteResult[key], k)
            total += 1
    print total
    print hit

def exp_citationPropagation(network, testPapers, authorPool):
    GT = network.removeGT(testPapers, authorPool)
    results = network.propagation_cite()
    hit = dict()
    for k in [1, 5, 10, 50, 100]:
        hit[k] = 0
        total = 0
        for key in GT:
            hit[k] += calHit(GT[key], results[key], k)
            total += 1
    print total
    print hit

def exp_metapath_comb(network, testPapers, authorPool):
    GT = network.removeGT(testPapers, authorPool)

    metapath_PPA = MetaPath(network,['cite', 'writeby'])
    metapath_PVPA = MetaPath(network,['publishby','publish', 'writeby'])
    metapath_PTPA = MetaPath(network,['mention','mentionby', 'writeby'])

    [pc_PPA, pcrw_PPA, pc_PVPA, pcrw_PVPA, pc_PTPA, pcrw_PTPA] = [dict(),dict(),dict(),dict(),dict(),dict()]
    for key in testPapers:
        thePaper = network.key2paper_[key]

        pc_PPA[key] = metapath_PPA.calPathCount(key)
        pcrw_PPA[key] = metapath_PPA.calPCRW(key)

        pc_PVPA[key] = metapath_PVPA.calPathCount(key)
        pcrw_PVPA[key] = metapath_PVPA.calPCRW(key)

        pc_PTPA[key] = metapath_PTPA.calPathCount(key)
        pcrw_PTPA[key] = metapath_PTPA.calPCRW(key)

    for alpha in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        for beta in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            ganma = 1.0 - alpha - beta
            if ganma < 0.0:
                continue
            print str(alpha) + '\t' + str(beta) + '\t' + str(ganma)
            total = 0
            hit_pc = dict()
            hit_pcrw = dict()
            for k in [1, 5, 10, 50, 100]:
                hit_pc[k] = 0
                hit_pcrw[k] = 0
            for key in testPapers:
                thePaper = network.key2paper_[key]
                total += 1

                simDict_pc = dict()
                for key1 in pc_PPA[key]:
                    if key1 not in simDict_pc:
                        simDict_pc[key1] = 0.0
                    simDict_pc[key1] += alpha * pc_PPA[key][key1]
                for key1 in pc_PVPA[key]:
                    if key1 not in simDict_pc:
                        simDict_pc[key1] = 0.0
                    simDict_pc[key1] += beta * pc_PVPA[key][key1]
                for key1 in pc_PTPA[key]:
                    if key1 not in simDict_pc:
                        simDict_pc[key1] = 0.0
                    simDict_pc[key1] += ganma * pc_PTPA[key][key1]

                simDict_pcrw = dict()
                for key1 in pcrw_PPA[key]:
                    if key1 not in simDict_pcrw:
                        simDict_pcrw[key1] = 0.0
                    simDict_pcrw[key1] += alpha * pcrw_PPA[key][key1]
                for key1 in pcrw_PVPA[key]:
                    if key1 not in simDict_pcrw:
                        simDict_pcrw[key1] = 0.0
                    simDict_pcrw[key1] += beta * pcrw_PVPA[key][key1]
                for key1 in pcrw_PTPA[key]:
                    if key1 not in simDict_pcrw:
                        simDict_pcrw[key1] = 0.0
                    simDict_pcrw[key1] += ganma * pcrw_PTPA[key][key1]

                for k in [1, 5, 10, 50, 100]:
                    hit_pc[k] += calHit(GT[key], simDict_pc,k)
                    hit_pcrw[k] += calHit(GT[key], simDict_pcrw, k)
            print hit_pc
            print hit_pcrw

def getAllTopicVec(network):
    network.venue2topic_ = dict()
    for venue in network.venue2key_:
        topicVec = dict()
        for key in network.venue2key_[venue]:
            thePaper = network.key2paper_[key]
            for t in thePaper.topicVec_:
                if t not in topicVec:
                    topicVec[t] = 0.0
                topicVec[t] += thePaper.topicVec_[t]
        total = 0.0
        for t in topicVec:
            total += topicVec[t]
        for t in topicVec:
            topicVec[t] /= total
        network.venue2topic_[venue] = topicVec
    # print network.venue2topic_

    network.author2topic_ = dict()
    for author in network.author2key_:
        topicVec = dict()
        for key in network.author2key_[author]:
            thePaper = network.key2paper_[key]
            for t in thePaper.topicVec_:
                if t not in topicVec:
                    topicVec[t] = 0.0
                topicVec[t] += thePaper.topicVec_[t]
        total = 0.0
        for t in topicVec:
            total += topicVec[t]
        for t in topicVec:
            topicVec[t] /= total
        network.author2topic_[author] = topicVec
    # print network.author2topic_

    network.topic2topic_ = dict()
    for topic in network.topic2key_:
        topicVec = dict()
        for key in network.topic2key_[topic]:
            thePaper = network.key2paper_[key]
            for t in thePaper.topicVec_:
                if t not in topicVec:
                    topicVec[t] = 0.0
                topicVec[t] += thePaper.topicVec_[t]
        total = 0.0
        for t in topicVec:
            total += topicVec[t]
        for t in topicVec:
            topicVec[t] /= total
        network.topic2topic_[topic] = topicVec
    # print network.topic2topic_

    network.saveToPickle('network_T20_allVec.pfile')

def getAuthorPool(network, testVenue):
    author2num = dict()
    for key in network.key2paper_:
        thePaper = network.key2paper_[key]
        if thePaper.fullVenue_ in testVenue:
            continue
        for author in thePaper.authors_:
            if author not in author2num:
                author2num[author] = 0
            author2num[author] += 1
    num2num = dict()
    for author in author2num:
        if author2num[author] not in num2num:
            num2num[author2num[author]] = 0
        num2num[author2num[author]] += 1
    # for num in num2num:
    #     print [num, num2num[num]]
    authorPool = set()
    for author in author2num:
        if author2num[author] >= 3:
            authorPool.add(author)

    with codecs.open(AUTHOR_POOL_PATH,'w',encoding='utf-8', errors='ignore') as authorFile:
        for a in authorPool:
            authorFile.write(a)
            authorFile.write(u'\n')

    testPaper = []
    for key in network.key2paper_:
        thePaper = network.key2paper_[key]
        if thePaper.fullVenue_ in testVenue:
            continue
        for author in thePaper.authors_:
            if author in authorPool:
                testPaper.append(key)
                break

    for p in testPaper:
        print p
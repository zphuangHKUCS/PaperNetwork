from paperNetwork import *


class MetaPath:

    def __init__(self, network, str):
        self.edgeTypes_ = str
        for e in self.edgeTypes_:
            if e not in ['cite', 'citeby', 'write', 'writeby', 'mention', 'mentionby', 'publish', 'publishby']:
                print 'Type error for meta path'
                exit(-1)

        self.isSyemetric_ = 1
        if len(self.edgeTypes_) % 2 != 0:
            self.isSyemetric_ = 0
        for i in range(0, len(self.edgeTypes_)/2):
            if self.edgeTypes_[i] + 'by' != self.edgeTypes_[len(self.edgeTypes_) - i - 1] and self.edgeTypes_[i] != self.edgeTypes_[len(self.edgeTypes_) - i - 1] + 'by':
                self.isSyemetric_ = 0

        self.network_ = network

    def randomWalk(self, s_key, TEST = 0):
        queue = []
        queue.append([s_key, 1.0])

        for i in range(0, len(self.edgeTypes_)):
            newQueue = []
            for qnode in queue:
                qkey = qnode[0]
                qweight = qnode[1]
                if len(qkey) == 0:
                    continue
                # print qkey
                nextCandidates = dict()
                if self.edgeTypes_[i] == 'cite':
                    for c in self.network_.key2paper_[qkey].cite_:
                        if c == '':
                            continue
                        # nextCandidates[c] = 1.0
                        # theProduct = product(self.network_.key2paper_[qkey].topicVec_, self.network_.key2paper_[c].topicVec_)
                        # print theProduct
                        # nextCandidates[c] = theProduct
                        nextCandidates[c] = 1.0
                    # nextCandidates = self.network_.key2paper_[qkey].cite_
                elif self.edgeTypes_[i] == 'citeby':
                    for c in self.network_.key2paper_[qkey].citeby_:
                        nextCandidates[c] = 1.0 / len(self.network_.key2paper_[qkey].citeby_)
                    # nextCandidates = self.network_.key2paper_[qkey].citeby_
                elif self.edgeTypes_[i] == 'write':
                    for k in self.network_.author2key_[qkey]:
                        # print k
                        # nextCandidates.append(k)
                        nextCandidates[k] = 1.0 / len(self.network_.author2key_[qkey])
                elif self.edgeTypes_[i] == 'writeby':
                    # nextCandidates = self.network_.key2paper_[qkey].authors_
                    for c in self.network_.key2paper_[qkey].authors_:
                        nextCandidates[c] = 1.0 / len(self.network_.key2paper_[qkey].authors_)
                elif self.edgeTypes_[i] == 'publish':
                    for k in self.network_.venue2key_[qkey]:
                        # nextCandidates.append(k)
                        nextCandidates[k] = 1.0 / len(self.network_.venue2key_[qkey])
                elif self.edgeTypes_[i] == 'publishby':
                    # nextCandidates.append(self.network_.key2paper_[qkey].venue_)
                    nextCandidates[self.network_.key2paper_[qkey].venue_] = 1.0
                elif self.edgeTypes_[i] == 'mention':
                    # nextCandidates = self.network_.key2paper_[qkey].topics_
                    for c in self.network_.key2paper_[qkey].topics_:
                        nextCandidates[c] = 1.0 / len(self.network_.key2paper_[qkey].topics_)
                elif self.edgeTypes_[i] == 'mentionby':
                    for k in self.network_.topic2key_[qkey]:
                        # nextCandidates.append(k)
                        nextCandidates[k] = 1.0 / len(self.network_.topic2key_[qkey])
                sums = 0.0
                for cand in nextCandidates:
                    sums += nextCandidates[cand]

                for cand in nextCandidates:
                    if cand == '':
                        continue
                    newQueue.append([cand, qweight * nextCandidates[cand] / sums])
            if TEST == 0:
                queue = newQueue
            else:
                queue = []
                for qnode in newQueue:
                    if qnode[0] != s_key:
                        queue.append(qnode)
        return queue

    def calPathCount(self, s_key, TEST = 0):
        ret = dict()
        key2pro = self.randomWalk(s_key, TEST)
        for keyPro in key2pro:
            if keyPro[0] not in ret:
                ret[keyPro[0]] = 0
            ret[keyPro[0]] += 1
        return ret

    def calPCRW(self, s_key, TEST = 0):
        ret = dict()
        key2pro = self.randomWalk(s_key, TEST)
        for keyPro in key2pro:
            if keyPro[0] not in ret:
                ret[keyPro[0]] = 0
            ret[keyPro[0]] += keyPro[1]
        return ret

    def calPathSim(self, s_key):
        if self.isSyemetric_ == 0:
            print 'Not symmetric. No PathSim'
            return dict()
        pc1 = self.calPathCount(s_key)
        ret = dict()
        for target in pc1:
            x = pc1[s_key]
            pc2 = self.calPathCount(target)
            y = pc2[target]
            ret[target] = 2.0 * pc1[target] / (x + y)
        return ret
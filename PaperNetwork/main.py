from paperNetwork import *
from config import *
from experiments import *
from meta import *

# pfile = open(PAPER_NETWORK_PICKLE_PATH, 'rb')
pfile = open('network_T20.pfile', 'rb')
network = pickle.load(pfile)
testVenue = readTextVenues(TEST_VENUE_PATH)

[testPapers, authorPool] = loadPaperAuthorID()
[author2topic, topic2word] = loadLDA(LDA_THETA_PATH, LDA_PHI_PATH)

# matrix = network.getTMatrix_LDA(author2topic, topic2word)
# [GT, result] = network.propagation_matrix(testVenue, matrix)


# # For experiments!!!
# exp_mostCited(network, testPapers, authorPool)
# exp_citeRank(network, testPapers, authorPool)
# exp_citationPropagation(network, testPapers, authorPool)
# exp_metapath(network, testPapers, authorPool)
# exp_metapath_comb(network, testPapers, authorPool)


# getAuthorPool(network, testVenue)


#
# for key in network.key2paper_:
#     thePaper = network.key2paper_[key]
#     vec = getPaperVector(topic2word,getWord2Frequency(thePaper.getBagOfWordsLine()))
#     print [key,vec]
#     thePaper.topicVec_ = vec
# network.saveToPickle('network_T20.pfile')

# testLDA(network,testVenue,author2topic,topic2word)
# evaluate_LDA(network,testPapers,author2topic,topic2word)


# getAllTopicVec(network)


############  Co-author recommendation  #########
# getGTForRecommendation(network, testPapers, authorPool)

coauthorGTpfile = open(COAUTHOR_GT_PICKLE_PATH, 'rb')
GT = pickle.load(coauthorGTpfile)

[TP, FP] = genTestPair(network, GT, testPapers)
exp_coauthor_recommend_propogation(network, GT, testPapers, TP, FP)
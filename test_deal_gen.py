import sAi
from sbridge import *

d = ['KQJ763.95.AT92.3', 'T.J8642.K8.JT752', 'A942.AQT7.J.AK96', '85.K3.Q76543.Q84']

deal = []
for s in d:
    deal.append(s.split('.'))
nd = Deal(0)                
test_deal_gen(nd, deal)

#for p in PLAYERS:
#    c,win = sAi.solver(p, 3, [], deal)

ai = sAi.ComputerPlayer(0) 
ai.new_deal(nd)
ai.deal.contract = Bid(7,3)   
ai.deal.hands[2] = nd.hands[2][:]
ai.deal.trick = ''
ai.deal.dummy = 2
for i in xrange(30):
    r = []
    for p in [0]:
        c,win = sAi.DealGenerator(ai, p)
        r.append([str(c),win])
    print r

#! /usr/bin/env python

# Old Lady
# Copyright (C) 2007 Paul Kuliniewicz <paul@kuliniewicz.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02111-1301, USA.

import importlib
import sbridge
from sbridge import *
import bidding
import sAi
import os
import defs
    
#sayc = bidding.Bidding ()
def debug(s, level = 0):
    #if not defs.testing: return
    #print('sai:',s)
    open('debug.log', 'a+').write('-debug: '+str(s)+'\n')
    
class ComputerPlayer:
    """
    A computer player.

    Currently, the AI is dumb as rocks, but it'll at least play by the rules.
    """
    bidState = None
    def __init__ (self, seat):
        self.algorithm = 'debug'
        self.seat = seat
        self.rubber = None
        self.deal = None
        self.history = []
    def new_deal (self, deal):
        """
        Reset the computer player's state for a new deal.

        Instances of this class are recycled between deals in case the AI
        eventually learns how the human plays and adapts its strategy
        accordingly....
        """

        #self.deal = deal
        self.deal = sbridge.Deal(deal.dealer)
        for p in sbridge.PLAYERS:
            if deal.hands[p] is not None:
                self.deal.hands[p] = deal.hands[p][:]
            else:
                self.deal.hands[p] = None
        self.bidState = AIBidStatus(self)
        self.history = []

    def bid_made(self, bid):
        """
        Called after each bid is placed.
        """
        self.deal.bid(bid)
        self.history.insert(0, bid)
        # relys on the history to find out the opening
        if self.deal.finishBidding() and self.seat == self.deal.dummy: return
        self.bidState.evaluateBid(bid)
        
    def trick_complete(self):
        """
        Called at the end of each trick.

        This should be used as part of keeping track of which cards have
        been played, but for now, does nothing.
        """

        self.deal.next_trick()

    def bid(self):
        """
        Place a bid during the bidding phase.

        Currently, this just passes all the time.  Eventually, it will use
        an actual, usable bidding strategy....
        """
        #bid = sayc.choose_bid (self.deal.hands[self.seat], self.history)
        #print 'prolog:',self.seat,bid
        bid = self.bidState.evaluate_deal()
        print(self.seat, 'pybid:', bid)
        return bid
        
    
    def play_self (self):
        """
        Play a card from the AI's own hand during a trick.
        """
        if 'simple' == self.algorithm:
            return self.play_from_hand(self.seat)

        # normally player just play its own card
        # so we return what card played to table manager
        return self.guess(self.seat)

    def play_dummy (self):
        """
        Play a card from the AI's partner's dummy hand during a trick.

        Currently, this is really dumb, treating playing the dummy's hand
        no differently than playing its own.
        """
        assert self.seat == self.deal.declarer
        if 'simple' == self.algorithm:
            return self.play_from_hand(self.deal.dummy)
        return self.guess(self.deal.dummy)

    def guess(self, player):
        if 'simple' == self.algorithm:
            return self.play_from_hand(player)
        c, win = DealGenerator(self, player)
        #debug([str(c),win])
        return c
        
    def play_from_hand(self, player):
        """
        Play a card during a trick from the specified player's hand.

        Currently, this is pretty dumb.  If leading a trick, it plays the
        highest-ranked card it has in an arbitrary suit.  Otherwise, it
        tries to play the lowest-ranked card that will take the trick for
        its team, or dump the lowest-ranked card in its hand.
        """

        hand = self.deal.hands[player][:]
        trick = self.deal.trick

        if trick.leader == player:
            # Lead the highest-ranked card in the hand.
            hand.sort()
            return hand[0]

        elif sbridge.team (trick.winner) == sbridge.team (player):
            # Dump the lowest-ranked card, non-trump if possible.
            candidates = [card for card in hand if card.suit == trick.lead]
            if len (candidates) == 0:
                candidates = [card for card in hand if card.suit != self.deal.contract.denom]
            if len (candidates) == 0:
                candidates = hand
            candidates.sort(key=by_rank)
            return candidates[0]

        else:
            # Try to take the trick with the lowest-ranked card possible.
            in_suit = [card for card in hand if card.suit == trick.lead]
            trumps = [card for card in hand if card.suit == self.deal.contract.denom]
            garbage = [card for card in hand if card.suit != trick.lead and card.suit != self.deal.contract.denom]
            if len (in_suit) > 0:
                candidates = []
                if trick.cards[trick.winner].suit == trick.lead:
                    candidates = [card for card in in_suit if card.rank > trick.cards[trick.winner].rank]
                if len (candidates) == 0:
                    candidates = in_suit
                candidates.sort(key=by_rank)
                return candidates[0]
            elif len (trumps) > 0:
                candidates = []
                if trick.cards[trick.winner].suit == self.deal.contract.denom:
                    candidates = [card for card in trumps if card.rank > trick.cards[trick.winner].rank]
                if len (candidates) == 0:
                    candidates = trumps
                candidates.sort(key=by_rank)
                return candidates[0]
            else:
                garbage.sort(key=by_rank)
                return garbage[0]
    def player(self): return self.deal.player
    def partner(self): return partner(self.seat)
    def lho(self): return seat_next(self.seat)
    def rho(self): return seat_prev(self.seat)


def by_rank (card:Card):
    """
    Sort function for comparing two cards strictly by rank.
    """
    return  card.rank

#--------------- AI bidding stuff -------------
def hand2suits(hand):
   suits = {0:[],1:[],2:[],3:[]} # somwhow list of list doesn't work
   for c in hand:
      idx = c.suit
      suits[idx].append(c.rank)
   return suits


def hcp(hand):
   h = 0
   for c in hand:
       h += c.hcp()
   return h
def shape(hand): return 0


class OneHand:
   '''
   define: balanced, semi-balance, un-balance
   opening bids,
   hcp=22+, 2NT hcp=22-24 shape=balanced
        3NT hcp=25-27 shape=balanced
        2C else
   hcp=0-12, 2x hcp=6-10, len=6x (x=DHS)
         3x (up to 5D), len=7+ (rule of two and three?)
         Pass else
   hcp=13-21, 1NT hcp=16-18 shap=balanced
          1H/S, len=5+, the longest, (if the same len, 1H)
          1D, len=4+
          1C, len=2+
          
   hcp=9+, len=5+ Overcall
   takeout double, hcp=12+, len(enemysuit)=short
   
   '''
   def __init__(self, bids):
      self.ai = bids.ai
      self.bidState = bids
      self.hand = self.ai.deal.hands[self.ai.seat]
      self.suits = hand2suits(self.hand)
   def hcp(self): return hcp(self.hand)
   def shortage(self):
       points = 0
       for s in sbridge.SUITS:
           slen = len(self.suits[s])
           if slen == 0: points += 5
           elif slen == 1: points += 3
           elif slen == 2: points += 1
       return points
   def lengthPoints(self):
       points = 0
       for s in sbridge.SUITS:
           slen = len(self.suits[s])
           if slen > 4: points += (slen -4)
       return points   
   def n_s(self): return len(self.suits[3])
   def n_h(self): return len(self.suits[2])
   def n_d(self): return len(self.suits[1])
   def n_c(self): return len(self.suits[0])
   def opening(self):
       rsp = self.checkAndReturn('opening1')
       return rsp
   def opening2(self,openbid):
       self.opening = openbid
       rsp = self.checkAndReturn('opening2')
       return rsp
   def gameon(self):
       '''idea is upto opener rebit, use predetermined bidding rule
       after that, use the exsiting bidding to generator possible deals, then
       use solvers to tell how many tricks possible to win,
       based on that go for invitation, game, or slams bidding convention'''
       return ' p'
   def response1(self, openbid):
      ''' short means the length of shortest suit, long means the lenght of longest suit
      suit the one in opening bid
      '''
      #print 'openbid',openbid
      rsp = self.check2('respons1')
      return rsp
   def response2(self):
      response = self.checkAndReturn('respons2')
      return response
   def openerNextBid(self):
       response = self.check2('openerNextBid')
       return response  

   def shape_type(self):
       """balanced {($h<5)&&($s<5)&&($s*$s+$h*$h+$d*$d+$c*$c)<=47}
semibalanced {$h<=5&&$s<=5&&$d<=6&&$c<=6&&$c>=2&&$d>=2&&$h>=2&&$s>=2}
       """
       shape = 'unbalanced'
       c,d,h,s = [len(self.suits[x]) for x in sbridge.SUITS]
       if (h<5)and(s<5)and((s*s+h*h+d*d+c*c)<=47): 
         shape = 'balanced'
       elif h<=5 and s<=5 and d<=6 and c<=6 and c>=2 and d>=2 and h>=2 and s>=2:
         # TODO semiblanced result in the same result as balanced, find a way to backtrack
         shape = 'unbalanced'
       print('type', c,d,h,s, shape)
       return shape
   def getLongestSuit(self):
       idx = 0
       slen = 0
       for s in sbridge.SUITS:
           if len(self.suits[s]) >= slen:
               idx = s
       return idx
   def longest(self):
       return len(self.suits[self.getLongestSuit()])
   def newsuit(self,bid):
       r = []
       for suit in range(4):
           if suit == bid.denom: continue
           r.append(len(self.suits[suit]))
       return max(r)
   def getNew(self,bid):
       slen = self.newsuit(bid)
       for suit in sbridge.SUITS:
           if suit == bid.denom: continue
           if len(self.suits[suit]) == slen:
               return bid.getNew(suit)       
   def getNew0(self, bid):
       slen = self.newsuit0(bid)
       for suit in range(bid.denom+1,4):
           if len(self.suits[suit]) == slen:
               return bid.getNew(suit)
   def newsuit0(self, bid):
       ''' intends to return max len suit in same level above prev valid bid
       '''
       denom = bid.denom
       if denom == sbridge.NO_TRUMP or denom == sbridge.SPADES: return 0
       r = []
       for suit in range(denom+1,4):
           r.append(len(self.suits[suit]))
       return max(r)   
   def check(self, ruleseqs):
      if ruleseqs == 'catchall': return True
      for r in ruleseqs.split(','):
         left,op,right = r.split()
         left = self.get(left)
         right = self.get(right)
         if not self.op(left,right,op): return False
      #print 'got',ruleseqs   
      return True
   def checkAndReturn(self, state):
       team = sbridge.team(self.ai.deal.player)
       bm = self.ai.bidState
       bidsys = bm.bid_system[team]
       ruleseqs = getattr(bm.bid_sys_m[team], bidsys+'_'+state)
       for rule in ruleseqs:
           if self.check(rule[1]): return rule[0]
       return ' p'
   def check2(self, state):
      bm = self.ai.bidState
      team = sbridge.team(self.ai.deal.player)
      bidsys = bm.bid_system[team]
      rules = getattr(bm.bid_sys_m[team], bidsys+'_'+state)       
      for rule in rules:
          if not self.check(rule[0]): continue
          if type(rule[1]) == type(''):
              if rule[1][:4] == 'case':
                  rule = rules[int(rule[1][-1])]
                  for onerule in rule[1:]:
                      if self.check(onerule[1]): return onerule[0]
              elif rule[1][:5] == 'refer':
                  return self.check2(rule[1].split()[1])
              else:
                  print('unknown item',rule)
              
          for onerule in rule[1:]:
              if self.check(onerule[1]): return onerule[0]
      return ' p'
                  
   def get(self, symbol):
       if symbol == 'hcp': return self.hcp()
       if symbol == 'longest':return self.longest()
       if symbol == 'newsuit':return self.newsuit(self.bidState.currentBid[1])
       if symbol == 'newsuit0': return self.newsuit0(self.bidState.currentBid[1])
       if symbol == 'hcp+shortage':return self.hcp()+self.shortage()
       if symbol == 'hcp+shortage+length':return self.hcp()+self.shortage()+self.lengthPoints()
       if symbol == 'shape_type': return self.shape_type()
       if symbol in ['opening1','opening1_type','respons1','respons1_type']:
           return str(self.bidState.getBid(symbol))
       if symbol == 'len_major': return max([len(self.suits[x]) for x in [2,3]])
       if symbol == 'len_minor': return max([len(self.suits[x]) for x in [0,1]])
       if symbol == 'suit': return len(self.suits[self.bidState.getBid('opening1').denom])
       if symbol in 'cdhs':
           return  len(self.suits[sbridge.KIDX[symbol]])
       if symbol.find('..') > 0:
           minv, maxv = symbol.split('..')
           return (int(minv),int(maxv))
       try:
           return int(symbol)
       except: return symbol
   def op(self, left, right, opcode):
      if opcode == '<': return (left < right)
      if opcode == '>': return (left > right)
      if opcode == '>=': return (left >= right)
      if opcode == '<=': return (left <= right)
      if opcode == '==': return (left == right)
      if opcode == 'in':
          minv,maxv = right
          #print('op_in', [left, minv, maxv, right])
          return (left >= minv) and (left <= maxv)
      if opcode == 'is': return left == right
      if opcode == 'isnot': return left != right
      print('unknown op', left, opcode, right)

# first 8 chars are used for keywords
BIDSTATE_IDX = {'opening1':0,'opening2':1,'respons1':2,'respons2':3,'openerNextBid':4, 'respons1_1n':2}
class AIBidStatus:
    ''' Another class record bid history, but interpret as hcp, shape etc. to help bidding and playing'''
    
    def __init__(self, ai):
        self.ai = ai
        self.handsEval = []
        for p in sbridge.PLAYERS:
            self.handsEval.append(HandEvaluation())
        self.first5 = [None,None,None,None,None]
        # not pass, double
        self.currentBid = None
        self.state = 'not opened'
        self.bid_system = ('sayc', 'mynew')
        self.bid_sys_m = [None] * 2
        for idx in range(len(self.bid_sys_m)):
            bidsys = self.bid_system[idx]
            self.bid_sys_m[idx] = importlib.import_module(f'bidsys_{bidsys}')

        self.hand = OneHand(self)
        self.distributionsScripts = 'main { accept }'

    def setOpening(self):
        if self.ai.history == []: return None
        if self.first5[0] is not None: return self.first5[0]
        player = self.ai.deal.dealer
        bids = self.ai.history[:]
        bids.reverse()
        for bid in bids:
            if not bid.is_pass():
                self.first5[0] = (player, bid)
                return (player, bid)
            player = sbridge.seat_next(player)
        return None

    def getBid(self, ask):
        if ask == 'respons1': return self.first5[2]
        elif ask == 'respons1_type': return self.first5[2].type()
        elif ask == 'opening1': return self.first5[0][1]
        elif ask == 'opening1_type': return self.first5[0][1].type()

    def rcheck2(self,bid,state):
        ''' based on bidding history and biding system rules, find out possible
        rules that are corresponding to the biding'''
        team = sbridge.team(sbridge.seat_prev(self.ai.deal.player))
        bidsys = self.bid_system[team]
        rules = getattr(self.bid_sys_m[team], bidsys+'_'+state)
        b = self.first5[0][1].difftype(bid)
        for rule in rules:
          mainrule = ''
          if rule[0][:7] not in ['opening','respons']:
              mainrule = rule[0]
          elif not self.hand.check(rule[0]): continue
          if type(rule[1]) == type(''):
              if rule[1][:4] == 'case':
                  rule = rules[int(rule[1][-1])]
              elif rule[1][:5] == 'refer':
                  return self.rcheck2(bid,rule[1].split()[1])
              else:
                  print ('unknown item',rule)
              
          for onerule in rule[1:]:
              if onerule[0] == str(bid) or onerule[0] == b:
                  if mainrule != '':
                      return mainrule+','+onerule[1]
                  return onerule[1]

    def evaluateBid(self, bid):
        """
        Evaluate the bid.
        """
        prev_player = sbridge.seat_prev(self.ai.deal.player)
        team = sbridge.team(prev_player)
        bidsys = self.bid_system[team]
        rule_opening1 = getattr(self.bid_sys_m[team], bidsys+'_opening1')
        rule_opening2 = getattr(self.bid_sys_m[team], bidsys+'_opening2')
        heval = self.handsEval[prev_player]
        openbid = self.setOpening()
     
        if not bid.is_pass() and not bid.is_double() and not bid.is_redouble():
            self.currentBid = (self.ai.deal.player, bid)

        print('evaluateBid', self.ai.seat, self.ai.deal.player, str(bid), self.state)
        if openbid is None:
            heval.opening = False
        elif openbid is not None and self.state == 'not opened':
            self.state = 'opening1'
            for rule in rule_opening1:
                if str(bid) == rule[0]:
                    heval.accept.append(rule[1])
                    break
        elif self.state == 'opening1':
            self.state = 'opening2'
            self.first5[1] = bid
            b = self.first5[0][1].difftype(bid)
            if self.ai.seat == sbridge.NORTH: print('opening2',b)
            for rule in rule_opening2:
                if str(bid) == rule[0]:
                    heval.accept.append(rule[1])
                    break
        elif self.state == 'opening2':
            self.state = 'respons1'
            self.first5[2] = bid
            rule = self.rcheck2(bid, 'respons1')
            heval.accept.append(rule)
        elif self.state == 'respons1':
            self.state = 'respons2'
            self.first5[3] = bid
        elif self.state == 'respons2':
            self.state = 'openerNextBid'
            self.first5[4] = bid
        elif self.state == 'openerNextBid':
            if self.ai.seat == sbridge.NORTH:
               for p in sbridge.PLAYERS:
                   heval = self.handsEval[p]  
                   print('rule', p, heval.accept)
            self.generateDealScript()        
        
    def evaluate_deal(self):
       ''' find the proper bid
       hand, in suit order
       print hcp, shape, estimate partner and opponents
       '''
       deal = self.ai.deal

       #mysuits = hand2suits(hand)
       if deal.trick is not None:           return
       #print 'HCP', self.hand.hcp()
       bid = ' p'
       openbid = self.first5[0]
       #determine bid state, opening, opening2, respons1, respons2
       # openerNextBid, Stayman, blackwood, jacob
       if self.state == 'not opened': bid = self.hand.opening()
       elif self.state == 'opening2': bid = self.hand.response1(openbid[1])
       elif self.state == 'opening1':  bid = self.hand.opening2(openbid[1])
       elif self.state == 'respons1': bid = self.hand.response2()
       elif self.state == 'respons2': bid = self.hand.openerNextBid()
       elif self.state == 'openerNextBid':
           # guess the hand distribtution,(running massive simulation on all possible hands,
           # eval the level we can make, select stratege accordingly
           bid = self.hand.gameon()
                 
       if bid[0] == '+':
           inc = int(bid[1])
           return openbid[1].getIncr(inc)
       if bid[1] == '_':
           n = int(bid[0])
           return sbridge.Bid(n, openbid[1].denom)
       elif bid == 'new':
           return self.hand.getNew(self.currentBid[1])
       elif bid == 'jumpshift':
           return self.hand.getNew(self.currentBid[1]).getIncr(1)
       elif bid == 'new0':
           return self.hand.getNew0(self.currentBid[1])
       elif bid == 'rule of two and three':
           suit = self.hand.getLongestSuit()
           if self.hand.longest() <= 8: bid = '4'+'cdhs'[suit]
           else: bid = '5'+'cdhs'[suit]
       elif bid == 'game in hand':
           bid = '2c'
       return sbridge.f2o_bid(bid)

    def generateDealScript(self):
       tcl = []
       for p in sbridge.PLAYERS:
           if p == self.ai.seat: continue
           if self.ai.deal.hands[p] is not None: continue
           t =  Translate2Tcl(self, p)
           for rule in self.handsEval[p].accept:
               if rule is None:
                   print('generateDealScript sth wrong, rule is None')
                   continue
               tcl.append(t.go(rule))
       s = ' && '.join(tcl)
       print('gends', s)
       head = '''source lib/utility.tcl
proc len_major {hand} {
    set s [spades $hand]
    set h [hearts $hand]
    if {$s > $h} {return $s}
    return $h
}
proc len_minor {hand} {
    set d [diamonds $hand]
    set c [clubs $hand]
    if {$d > $c} {return $d}
    return $c
}
proc shortage {hand} {
    set suits "spades hearts diamonds clubs"
    set r 0
    foreach suit "$suits" {
        set n [eval $suit $hand]
        if {$n == 0} {
          set r [expr $r + 5]
        } elseif {$n == 1} {
                set r [expr $r + 3]
        } elseif {$n == 2} {
                    set r [expr $r + 1]
        }
    }
    return $r
}
proc length_points {hand} {
    set suits "spades hearts diamonds clubs"
    set r 0
    foreach suit "$suits" {
        set n [eval $suit $hand]
        if {$n > 4} {set r [expr $r + $n - 4]}
    }
    return $r
}
main { if { 
'''
       if s != '': self.distributionsScripts = head+s+' } accept } \n'
       
       
class HandEvaluation:
    def __init__(self):
        self.hcp = ''
        self.opening = False
        self.accept = []
        self.reject = []

r='''
      if self.check(['hcp <= 9', 'long >= 5', 'short <= 1']): return '1'
      if self.check(['hcp >= 6','c < 5','d >= 4','h < 4','s < 4','opening1 == 1c']): return 'id'

       opening1 == minor, hcp >= 6, h == 4, h >= s -> 1h
       opening1 == minor, hcp >= 6, h > 4, h > s -> 1h
       opening1 == minor, hcp >= 6, s >= 4, s >= h -> 1s
       opening1 == minor, hcp >= 6, s == 4, h < 4 -> 1s
       opening1 == 1h, hcp >= 6, h < 3, s >= 4 -> 1s
       deny-opener-support openning ==  major, suit < 3
               or suit < 5
       denom_lt opening1 == 1, hcp >= 11, deny-opener-support, long >= 4 -> new at 2
       denom_lt opening1 == 1, hcp >= 19, deny-opener-support, long > 5 -> new at 2
       hcp in 6..10, deny_opener_support long < 4 -> 1n
       hcp >= 13 -> 2n jacoby_2n
       hcp in 15..17, balanced, suit >= 2 -> 3n

       rebid: support is the suit partner bid previously
       hcp in 13..16, support >= 4 -> +1
       hcp in 17..18, support >= 4 -> +1
       
      '''
class Translate2Tcl:
    def __init__(self, bids, player):
        self.seat = ['north','east','south','west'][player]
        self.player = player
        self.bidState = bids
        
    def go(self, rule):
        f = []
        for r in rule.split(','):
            left,op,right = r.split()
            if left[:7] in ['opening','respons']:
                continue
            if left == 'shape_type':
                if right == 'unbalanced':
                    continue
                f.append('['+right+ ' '+self.seat+']')
                continue
            left = self.get(left)
            right = self.get(right)
            f.append(self.op(left,right,op))
        return ' && '.join(f)

    def get(self, symbol):
       s = self.seat
       if symbol == 'hcp': return '[hcp '+self.seat+']'
       if symbol == 'longest':return self.longest()
       if symbol == 'newsuit':return self.newsuit(self.bidState.currentBid[1])
       if symbol == 'newsuit0': return self.newsuit0(self.bidState.currentBid[1])
       if symbol == 'hcp+shortage':return f'[expr [hcp {s}] + [shortage {s}]]'
       if symbol == 'hcp+shortage+length':f'[expr [hcp {s}] + [shortage {s}]+ [length_points {s}]]'
       if symbol == 'shape_type': return 'shape_type'
       if symbol == 'len_major': return '[len_major '+self.seat+']'
       if symbol == 'len_minor': return '[len_minor '+self.seat+']'
       if symbol == 'suit': symbol = 'cdhs'[self.bidState.getBid('opening1').denom]
       if symbol in 'cdhs':
           return  '['+{'c':'clubs','h':'hearts','d':'diamonds','s':'spades'}[symbol]+' '+self.seat+']'
       if symbol.find('..') > 0:
           minv, maxv = symbol.split('..')
           return (minv, maxv)
       return symbol

    def op(self, left, right, opcode):
      if opcode in ['<','>', '>=', '<=', '==']:
          return ' '.join([left,opcode,right])
      elif opcode == 'in':
          minv,maxv = right
          return ' '.join([left, '>=', minv, '&&', left, '<=', maxv])
      if opcode == 'is': return ' '.join([left, '==', right])
      if opcode == 'isnot': return ' '.join([left, '!=', right])
      print ('unknown op',left,opcode,right)


def dds_solver_api(trump, currentTricks, deal):
   '''deal is N-W,S-E 4x4 list, shdc -> 0123, always at the north point of view
but trump is shdc -> 3210, and currentTricks is list shdc->3210, in play order
   return r[0] suit, r[1] rank, r[3] win trick for north
   '''
   if trump != 4: trump = 3-trump
   #debug(currentTricks)
   #for c in currentTricks: print str(c),
   #print currentTricks, deal
   # the play to solve is always at 0 (North), so last player is always 3(West)
   first = (4 - len(currentTricks)) % 4
   #if first == 2: first = 1
   test = [0,3,1,trump, first]
   # 4x4 cards
   n = []
   for i in PLAYERS:
      n.append('.'.join(deal[i]))
   test.append(':'.join(n))
   # at most 3cards (suit, rank)
   s = []
   r = []
   for c in currentTricks:
      s.append(str(3-c.suit))
      r.append(str(c.rank))
   if len(currentTricks) > 0:   
      test.append(':'.join(['.'.join(s),'.'.join(r)]))
   arg = ' '.join([str(x) for x in test])
   arg = defs.DDS_PATH + '/dds ' + arg
   debug(arg)
   coutput = os.popen(arg).read()
   debug([coutput])
   lines = [x.split() for x in coutput.splitlines()[1:]]
   # win in decrease order, so if winmax changes, we don't need those result
   #winmax = int(lines[0][3])
   r = [lines[0]]
   for line in lines[1:]:
        if line[0] == 'result:':
            return [line]
        
   #print 'suit','shdc'[int(r[1])],'rank',r[2],'win tricks',r[3]
   return r

def o2dstack_hand(hand):
   '''deal stack  has format AK QJ - T98765432, from Spade to Club'''
   def card_sort(card):
        return card.suit * 100 + card.rank
   handnew = hand[:]
   print_hand(handnew)
   handnew.sort(reverse=True, key=card_sort)
   print_hand(handnew)

   h = sbridge.o2pbn_hand(handnew).split('.')
   for i in sbridge.SUITS:
      if h[i] == '': h[i] = '-'
   return ' '.join(h)

def deal2list(s):
    '''input: lines of deal308 output in pbn formats
       output: in list of list (hands) of list (suits)
    '''
    r = []
    for line in s.splitlines()[0::2]:
        newdeal = line.split('"')[1][2:].split()
        #debug(newdeal)
        ddeal = [[],[],[],[]]
        # put estimated deal in 4x4 format
        for i in sbridge.PLAYERS:
           d = newdeal[i].split('.')
           ddeal[i] = [[],[],[],[]]
           for j in sbridge.SUITS:
               ddeal[i][j] = list(d[j])
        r.append(ddeal)
    return r
               
def DealGenerator(ai, player):
    ''' giving knonw hands, biding history, player, guess how many tricks to win, which card to play
     dummy should not be as ai.seat
    '''
    #ai.bidState.generateDealScript()
    tempTcl = str(player)+'temp.tcl'
    open(tempTcl,'w').write(ai.bidState.distributionsScripts)
    
    myseat = ai.seat
    mine = o2dstack_hand(ai.deal.originalHand(myseat))
    cmd = defs.DEAL_PATH + '/deal -i format/pbn -'+sbridge.seat_str(myseat)+' "'+mine+'"'
    others = list(sbridge.PLAYERS[:])
    #print(others)
    others.remove(myseat)
    #print(others)
    if ai.deal.finishBidding():
        seat2 = ai.deal.dummy
        assert seat2 != myseat
        if ai.deal.hands[seat2] is not None:
            hand2 = o2dstack_hand(ai.deal.originalHand(seat2))
            cmd += ' -'+sbridge.seat_str(seat2)+' "'+ hand2 + '"'
            others.remove(seat2)
        # take out played cards
        eargs = []
        for i in others:
           if ai.deal.played_hands[i] != []:
              eargs.append(sbridge.PLAYER_NAMES[i].lower()+' gets')
           for c in ai.deal.played_hands[i]:
              eargs.append(str(c).upper())       
           eargs.append(';')
        cmd +=  ' -e "'+' '.join(eargs)+'"'
    cmd += ' -i '+tempTcl+' 7'
    debug(cmd)

    #TODO popen timeout, means distribuion is not agree with the hand
    print('deal', player, myseat, ai.deal.dummy, cmd)
    deals = deal2list(os.popen(cmd).read())
    #print str(ai.deal.trick)
    #print('deals', deals)
   
    currentTrick = []
    seat = sbridge.seat_prev(player)
    while (len(ai.deal.played_hands[seat]) > len(ai.deal.played_hands[player])):
       currentTrick.insert(0, ai.deal.played_hands[seat][-1])
       seat = sbridge.seat_prev(seat)

    r = []
    for ddeal in deals:
        # remove played cards
        for i in sbridge.PLAYERS:
           seat = sbridge.f2o(i)
           for c in ai.deal.played_hands[seat]:
              s = 3-c.suit
              #print(ddeal[i][s])
              ddeal[i][s].remove(str(c)[0])
              #print(ddeal[i][s])
        tmp = []
        for p in ddeal:
            tmp.append('.'.join([''.join(d) for d in p]))
        #debug('  '.join(tmp))
        solutions = solver(player, ai.deal.contract.denom, currentTrick, ddeal)
        #debug([(str(x),y) for x,y in solutions])
        r += solutions
    flats = [str(c) for (c,w) in r]
    debug([(str(c),w) for (c,w) in r])
    idx = max_freq(flats)
    return r[idx]

def solver(player, trump, currentTrick, deal):
    sdeal = [[],[],[],[]]
    #move my seat to North for solver
    for i in range(4):
       d = deal[sbridge.seat_move(player,i)]
       for j in range(4):
          sdeal[i].append(''.join(d[j]))

    r = dds_solver_api(trump, currentTrick, sdeal)    
    return [(sbridge.Card(3-int(x[1]), int(x[2])),x[3]) for x in r]
          
    
def max_freq(xlist):
    r = xlist
    maxwin = 0
    candi = -1
    counter = {}
    idx = 0
    for c in r:
        if c not in counter: counter[c] = 0
        counter[c] += 1
        if counter[c] > maxwin:
            maxwin = counter[c] 
            candi = idx
        idx += 1
    return candi

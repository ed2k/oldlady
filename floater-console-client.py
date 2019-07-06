from floater_client import *
from sbridge import *
import os

def print_suits(suits):
   ''' print a hand, organized as 4 suit'''
   for i in xrange(4):
      j = 3 - i
      print 'CDHS'[j]+':',
      for c in suits[j]:
         print '0123456789TJQKA'[c],
      print

      
   
class ConsoleState(State):
   def handle_auction(self):
      ''' try use oldlady engine '''
      dealer = (self.hand_id-1) % 4
      ai = sAi.ComputerPlayer(dealer)
      ai.seat = self.own_seat()
      print 'dealer','NESW'[dealer],'my seat','NESW'[ai.seat]

      deal = sbridge.Deal(dealer)
      for p in sbridge.PLAYERS:
         if self.deal.hands[p] is None:
            deal.hands[p] = None
         else: deal.hands[p] = self.deal.hands[p][:]

      ai.deal = deal
      print 'myhand',
      for c in ai.deal.hands[ai.seat]: print c,
      print
      for i in xrange(len(self.bid_status)):
         ai.bid_made(f2o_bid(self.bid_status[i]))
      
      if ai.deal.trick is None:
         bid =  o2f_bid(ai.bid())
         # evaluate hand, provide reasoning, learn/discard human suggestion???
         self.ai = None
         evaluate_deal(ai)
         print 'AI suggest bid', bid
         user = raw_input('>>>> ')
         if user == '': return bid
         return user

      if ai.seat == deal.dummy: return None
      # first lead is over, everybody else see the dummy's hand
      
      for c in self.play_status:
         deal.play_card(f2o_card(c))
         if deal.trick.cards[deal.player] is not None:
            ai.trick_complete()

      if (ai.seat != deal.declarer) and (deal.player != ai.seat): return None
      if (ai.seat == deal.declarer) and (deal.player != deal.dummy) and (deal.player != deal.declarer):
         return None         
      print 'myseat','NESW'[ai.seat],'player','NESW'[deal.player], 'dummy','NESW'[deal.dummy],'declarer','NESW'[deal.declarer]      
      #evaluate_deal(ai)
      # TODO, generate a deal based on bidding, and play history
      # use double dummy solver to find the best play.
      if deal.hands[deal.dummy] is not None:
         guess_deal = DealGenerator(self.deal.hands, self.bid_status, self.play_status, ai)
      # card = solver(guess_deal)      
      card = None
      if (deal.player == deal.dummy) and (deal.declarer == ai.seat):
         card = ai.play_dummy()
      if deal.player == ai.seat: card = ai.play_self()

      print 'Ai suggest play', str(card)
      if self.ai == 'auto': return  o2f_card(card)
      user = raw_input('>>>> ')
      if user == '': return  o2f_card(card)
      if user == 'auto':
         self.ai = 'auto'
         return  o2f_card(card)
      return pbn2f_card(user)
   
if __name__ == "__main__":
   one_client(ConsoleState())




#! /usr/bin/env python

"""
"""

import floater_client
import sAi
import sbridge


PLAY_CARD, CONFIRM_TRICK, CONFIRM_DEAL, CONFIRM_GAME, CONFIRM_RUBBER = range (5)

def _(a):return a


class App:
    def __init__ (self):
        self.ais = [sAi.ComputerPlayer(seat) for seat in sbridge.PLAYERS]
        self.start_next_rubber ()
        self.action = None

    def distribute_deal(self):
        # clone deal to show AI only its own hand        
        for ai in self.ais:
            deal = sbridge.Deal(self.deal.dealer)
            deal.hands[ai.seat] = self.deal.hands[ai.seat][:]
            ai.new_deal(deal)
            
    def start_next_deal (self):
        """
        Prepare for the next deal of cards.
        """

        self.deal = self.rubber.next_deal()
        self.distribute_deal()
        self.messages = []
        # print deal
        print('-'*80)
        print([floater_client.o2pbn_hand(self.deal.hands[s]) for s in sbridge.PLAYERS])

    def start_next_rubber (self):
        """
        Start playing for a new rubber.
        """
        self.rubber = sbridge.Rubber(sbridge.WEST)
        self.start_next_deal()

    def update_scores(self):
        """
        Update the displays of scores and tricks taken.
        """
        print (self.rubber.vulnerable[sbridge.WEST_EAST],
            self.rubber.vulnerable[sbridge.NORTH_SOUTH],
            self.rubber.above[sbridge.WEST_EAST],
            self.rubber.above[sbridge.NORTH_SOUTH],
            self.rubber.below[sbridge.WEST_EAST],
            self.rubber.below[sbridge.NORTH_SOUTH],

            'Tricks WE', self.deal.tricks_taken[sbridge.WEST_EAST],
            'NS',self.deal.tricks_taken[sbridge.NORTH_SOUTH])
        
    def play_for_ais(self):
        """
        Have the AIs make their moves, continuing until it is the human
        player's turn again.  If the human is dummy, he will still need
        to confirm each trick.
        """
        while True:
            # print('ai')
            if self.deal.contract is not None and self.deal.contract.is_pass ():
                self.messages = [_("Deal abandoned; all players passed")]
                self.action = CONFIRM_DEAL
                return
            elif self.deal.trick is None:
                #print("bidding")
                bid = self.ais[self.deal.player].bid()
                for ai in self.ais:
                    ai.bid_made(bid)
                self.deal.bid(bid)
                # check if bidding is over
                if self.deal.finishBidding():
                    # show dummy hand to declarer
                    tm = self.deal
                    self.ais[tm.declarer].deal.hands[tm.dummy] = tm.hands[tm.dummy][:]
                    p = sbridge.seat_prev(tm.declarer)
                    self.ais[p].deal.hands[tm.dummy] = tm.hands[tm.dummy][:]
                    # dummy no need to think
                    self.ais[tm.dummy].deal.hands[tm.dummy] = None
                    p = sbridge.seat_next(tm.declarer)
                    # play frist card
                    card = self.ais[p].play_self()
                    # show dummy to leader
                    self.ais[p].deal.hands[tm.dummy] = tm.hands[tm.dummy][:]
                    # notify all players
                    for ai in self.ais: ai.deal.play_card(card)
                    self.deal.play_card(card)
            else:
                #print('dds play trick')
                #self.update_scores ()
                self.action = CONFIRM_GAME
                return


    def run(self):
        #print('start', self.action)
        if self.action == CONFIRM_DEAL:
            if not self.deal.contract.is_pass():
                self.messages = self.rubber.score_game()
                print('confirm_deal', self.messages)
                self.update_scores()
                if len (self.messages) > 0:
                    self.action = CONFIRM_GAME
                else:
                    self.start_next_deal ()
                    self.action = None
            else:
                self.start_next_deal ()
                self.action = None
        elif self.action == CONFIRM_GAME:
            self.messages = self.rubber.score_rubber()
            #self.update_scores ()
            if len(self.messages) > 0:
                self.action = CONFIRM_RUBBER
            else:
                self.start_next_deal ()
                self.action = None
        elif self.action == CONFIRM_RUBBER:
            self.start_next_rubber ()
            self.action = None

        if self.action is None:
            self.play_for_ais()


if __name__ == "__main__":
    app = App()
    import time
    while True:
        app.run()
        # time.sleep(0.3)
        

#! /usr/bin/env python


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

# 1. test bidding based on pbn library
# 2. play againgst double dummy solver

import floater_client
import sAi
import sbridge
from sbridge import *
import defs

import os


PLAY_CARD, CONFIRM_TRICK, CONFIRM_DEAL, CONFIRM_GAME, CONFIRM_RUBBER = range (5)

def _(a):return a



class App:
    """
    The main application winodw for Old Lady.
    """

    def __init__ (self):
        #self.xml = glade.XML (os.path.join (defs.PKG_DATA_DIR, "oldlady.glade"))
        #self.xml.signal_autoconnect (self)

        #self.show_all_cards = False

        self.ais = [sAi.ComputerPlayer (seat) for seat in sbridge.PLAYERS]
        self.start_next_rubber ()


    def distribute_deal(self):
        # clone deal to show AI only its own hand        
        for ai in self.ais:
            deal = Deal(self.deal.dealer)
            deal.hands[ai.seat] = self.deal.hands[ai.seat][:]
            ai.new_deal(deal)
            
    def start_next_deal (self):
        """
        Prepare for the next deal of cards.
        """

        self.deal = self.rubber.next_deal ()
            
        self.distribute_deal()

        self.messages = []
        # print deal
        print '-'*80       
        print [floater_client.o2pbn_hand(self.deal.hands[s]) for s in sbridge.PLAYERS]

        self.play_for_ais ()
        #self.update_scores ()

    def start_next_rubber (self):
        """
        Start playing for a new rubber.
        """

        self.rubber = sbridge.Rubber (sbridge.WEST)
        self.start_next_deal ()


    def update_scores (self):
        """
        Update the displays of scores and tricks taken.
        """

        print self.rubber.vulnerable[sbridge.WEST_EAST],
        print self.rubber.vulnerable[sbridge.NORTH_SOUTH],

        print self.rubber.above[sbridge.WEST_EAST],
        print self.rubber.above[sbridge.NORTH_SOUTH],

        print self.rubber.below[sbridge.WEST_EAST],
        print self.rubber.below[sbridge.NORTH_SOUTH],

        print'Tricks WE', self.deal.tricks_taken[sbridge.WEST_EAST],
        print 'NS',self.deal.tricks_taken[sbridge.NORTH_SOUTH],
        print
    def play_for_ais (self):
        """
        Have the AIs make their moves, continuing until it is the human
        player's turn again.  If the human is dummy, he will still need
        to confirm each trick.
        """
        while True:
            if self.deal.contract is not None and self.deal.contract.is_pass ():
                self.messages = [_("Deal abandoned; all players passed")]
                self.action = CONFIRM_DEAL
                return
            elif self.deal.trick is None:
                bid = self.ais[self.deal.player].bid ()
                for ai in self.ais:
                    ai.bid_made (bid)
                self.deal.bid (bid)
                # check if bidding is over
                if self.deal.finishBidding():
                    # show dummy hand to declarer
                    tm = self.deal
                    self.ais[tm.declarer].deal.hands[tm.dummy] = tm.hands[tm.dummy][:]
                    p = seat_prev(tm.declarer)
                    self.ais[p].deal.hands[tm.dummy] = tm.hands[tm.dummy][:]
                    # dummy no need to think
                    self.ais[tm.dummy].deal.hands[tm.dummy] = None
                    p = seat_next(tm.declarer)
                    # play frist card
                    card = self.ais[p].play_self()
                    # show dummy to leader
                    self.ais[p].deal.hands[tm.dummy] = tm.hands[tm.dummy][:]
                    # notify all players
                    for ai in self.ais: ai.deal.play_card(card)
                    self.deal.play_card(card)
            else:
                if self.deal.finishTrick():
                    self.action = CONFIRM_TRICK
                    #self.update_scores ()
                    return
                if self.deal.player != self.deal.dummy:
                    card = self.ais[self.deal.player].play_self ()
                    # notify other players
                    for ai in self.ais: ai.deal.play_card(card)
                    self.deal.play_card(card)
                else:
                    card = self.ais[self.deal.declarer].play_dummy ()
                    # notify other players
                    for ai in self.ais: ai.deal.play_card(card)
                    self.deal.play_card(card)
    ##########################################################################
    #
    # Tableau callbacks
    #
    ##########################################################################

    def run (self):
        if self.action == PLAY_CARD:
            if self.deal.trick is not None:
                card = self.hand_renderers[self.deal.player].card_at (event.x, event.y)
                if card is not None and self.deal.legal_card (card):
                    self.deal.play_card (card)
                    if self.deal.trick.cards[self.deal.player] is not None:
                        self.action = CONFIRM_TRICK
                    #self.update_scores ()
                    #tableau.queue_draw ()
        elif self.action == CONFIRM_TRICK:
            for ai in self.ais:
                ai.trick_complete ()
            self.deal.next_trick ()
            if self.deal.trick is None:
                self.messages = self.rubber.score_deal ()
                self.action = CONFIRM_DEAL
            else:
                self.action = PLAY_CARD
            #self.update_scores ()
        elif self.action == CONFIRM_DEAL:
            if not self.deal.contract.is_pass ():
                self.messages = self.rubber.score_game ()
                print self.messages
                self.update_scores ()
                if len (self.messages) > 0:
                    self.action = CONFIRM_GAME
                else:
                    self.start_next_deal ()
                    self.action = None
            else:
                self.start_next_deal ()
                self.action = None
        elif self.action == CONFIRM_GAME:
            self.messages = self.rubber.score_rubber ()
            #self.update_scores ()
            if len (self.messages) > 0:
                self.action = CONFIRM_RUBBER
            else:
                self.start_next_deal ()
                self.action = None
        elif self.action == CONFIRM_RUBBER:
            self.start_next_rubber ()
            self.action = None

        if self.action is None or self.action == PLAY_CARD:
            self.play_for_ais ()



if __name__ == "__main__":
    app = App()
    import time
    while True:
        app.run()
        time.sleep(0.3)
        

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

# 4 robots play in terminal env.
# basic program flow
# 1. App() initialize all visiual components (optional)
# 2. player take seat, sAi.ComputerPlayer(seat)
# 3. start_next_rubber(), setup scoring system
# 3.1 setup dealer, rubber(SOUTH)
# 3.2 dealing cards rubber.next_deal() in start_next_deal()
# 3.3 distribute hand to sAi ai.new_deal(deal)
#   notice, here each AI now can see all four hands for simplicity
# 4. start auction, play_for_ais()
# 4.1 bid in turn, ais[deal.player].bid()
# 4.2 notify ai the current bid ai.bid_made(bid)
# 4.3 record the bid in table, deal.bid(bid)
# 4.4 continue bid (step 4) until, qualify to finish auction
# 5 setup info about declarer, dummy, contract etc prepare_trick_taking()
# 6 start play  play_for_ais() ai.play_self or ai.play_dummy
# 7 one trick is over (4 cards played), wait CONFIRM_TRICK
# 8.0 notify ai trick_complete tableau_button_release_event_cb()
# 8.1 talbe setup for deal.next_trick
# 8.2 play next, PLAY_CARD at bottom of tableau_button_release_event_cb()
# 9  goto step 7 until deal is down CONFIRM_DEAL
# 10 start_next_deal step 3.2 or game over CONFIRM_GAME
# 11 check scroe etc, at tableau_button_release_event_cb()


import sAi
import sbridge
from sbridge import *
import defs

import os


PLAY_CARD, CONFIRM_TRICK, CONFIRM_DEAL, CONFIRM_GAME, CONFIRM_RUBBER = range (5)

def _(a):return a
# This is easy to solve with a simple tiny wrapper:
# class static method
class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable


class glade:
    def XML(a):
        #print 'glade.XML',a
        return glade()
    XML = Callable(XML)
    
    def signal_autoconnect(self,a):
        pass
    def get_widget(self,a):
        #print 'get_widget',a
        return glade()
    def set_label(self,a): pass
        #print 'set_lable',a

class App:
    """
    The main application winodw for Old Lady.
    """

    def __init__ (self):
        self.xml = glade.XML (os.path.join (defs.PKG_DATA_DIR, "oldlady.glade"))
        self.xml.signal_autoconnect (self)

        self.show_all_cards = False

        self.ais = [sAi.ComputerPlayer (seat) for seat in sbridge.PLAYERS]
        self.start_next_rubber ()


    def distribute_deal(self):
        # clone deal to show AI only its own hand
        for ai in self.ais:
            ai.new_deal (self.deal)
            
    def start_next_deal (self):
        """
        Prepare for the next deal of cards.
        """

        self.deal = self.rubber.next_deal ()
        # for debuging biding, use the same deal
        import floater_client
        pbn = "K8652.Q76.KT8.AK T4.843.65.QT9873 AJ.AJT5.J432.J65 Q973.K92.AQ97.42"       
        hands = [x.split('.') for x in pbn.split()]
        s = '''
0 9s Qh Th 2h Kd Jd 7d 6d 5d 3d Ac 5c 3c
1 Js 8s 6s 9h 8h 4h Ad Qd 9d 4d Kc 4c 2c
2 As Ks Qs Ts 2s Ah Kh 3h 8d 2d 9c 8c 6c
3 7s 5s 4s 3s Jh 7h 6h 5h Td Qc Jc Tc 7c


'''
        hands = s.splitlines()[1:5]
        for p in sbridge.PLAYERS:
            h = []
            for c in hands[p].split()[1:]:
                suit = STR2SUIT[c[1].upper()]
                card = Card(suit,floater_client.PBN_HIDX[c[0].lower()]+2)
                h.append(card)
            #self.deal.hands[p] = h
            
        hands = [
['7', 'J987', '64', 'AJ9863'],
['A53', 'AK3', 'K82', 'QT75'],
['KT62', 'QT52', 'JT3', 'K4'],
['QJ984', '64', 'AQ975', '2']]
        for p in sbridge.PLAYERS:
            h = []
            suits = hands[p]
            for s in sbridge.SUITS:
                for c in suits[3-s]:
                    card = Card(s,floater_client.PBN_HIDX[c.lower()]+2)
                    h.append(card)
            #self.deal.hands[p] = h
            
        self.distribute_deal()

        self.messages = []
        # print deal
        print '-'*80
        for s in sbridge.PLAYERS:
            print s,
            for c in self.deal.hands[s]: print c,
            print
        self.play_for_ais ()
        self.update_scores ()

    def start_next_rubber (self):
        """
        Start playing for a new rubber.
        """

        self.rubber = sbridge.Rubber (sbridge.WEST)
        self.start_next_deal ()

    def populate_legal_bids (self):
        """
        Fill in the bidding widget with the currently legal bids.
        """

        self.legal_bids.clear ()
        for legal_bid in self.deal.legal_bids ():
            iter = self.legal_bids.append ()
            self.legal_bids.set (iter, 0, legal_bid)

    def update_scores (self):
        """
        Update the displays of scores and tricks taken.
        """

        self.xml.get_widget ("we-vulnerable").set_label (self.rubber.vulnerable[sbridge.WEST_EAST] and _("Yes") or _("No"))
        self.xml.get_widget ("ns-vulnerable").set_label (self.rubber.vulnerable[sbridge.NORTH_SOUTH] and _("Yes") or _("No"))

        self.xml.get_widget ("we-above").set_label ("%d" % self.rubber.above[sbridge.WEST_EAST])
        self.xml.get_widget ("ns-above").set_label ("%d" % self.rubber.above[sbridge.NORTH_SOUTH])

        self.xml.get_widget ("we-below").set_label ("%d" % self.rubber.below[sbridge.WEST_EAST])
        self.xml.get_widget ("ns-below").set_label ("%d" % self.rubber.below[sbridge.NORTH_SOUTH])

        self.xml.get_widget ("we-tricks").set_label ("%d" % self.deal.tricks_taken[sbridge.WEST_EAST])
        self.xml.get_widget ("ns-tricks").set_label ("%d" % self.deal.tricks_taken[sbridge.NORTH_SOUTH])

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
                if self.deal.trick is not None:
                    # show dummy hand to declarer
                    tm = self.deal
                    self.ais[tm.declarer].deal.hands[tm.dummy] = tm.hands[tm.dummy][:]
                    # dummy no need to think
                    self.ais[tm.dummy].deal.hands[tm.dummy] = None                    
            else:
                if self.deal.trick.cards[self.deal.player] is not None:
                    self.action = CONFIRM_TRICK
                    self.update_scores ()
                    return
                if self.deal.player != self.deal.dummy:
                    card = self.ais[self.deal.player].play_self ()
                    # notify other players
                    for ai in self.ais:
                        ai.deal.play_card(card)
                    self.deal.play_card(card)
                else:
                    card = self.ais[self.deal.declarer].play_dummy ()
                    # notify other players
                    for ai in self.ais:
                        ai.deal.play_card(card)
                    self.deal.play_card(card)
    ##########################################################################
    #
    # Tableau callbacks
    #
    ##########################################################################

    def tableau_button_release_event_cb (self, tableau, event):
        if self.action == PLAY_CARD:
            if self.deal.trick is not None:
                card = self.hand_renderers[self.deal.player].card_at (event.x, event.y)
                if card is not None and self.deal.legal_card (card):
                    self.deal.play_card (card)
                    if self.deal.trick.cards[self.deal.player] is not None:
                        self.action = CONFIRM_TRICK
                    self.update_scores ()
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
            self.update_scores ()
        elif self.action == CONFIRM_DEAL:
            if not self.deal.contract.is_pass ():
                self.messages = self.rubber.score_game ()
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
            self.update_scores ()
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


    ##########################################################################
    #
    # Menu and toolbar callbacks
    #
    ##########################################################################

    def game_new_cb (self, widget):
        self.rubber = sbridge.Rubber (sbridge.SOUTH)
        self.start_next_deal ()
        self.update_scores ()

    def game_quit_cb (self, widget):
        gtk.main_quit ()

    def show_all_toggled_cb (self, widget):
        self.show_all_cards = widget.active
        self.xml.get_widget ("tableau").queue_draw ()

    def help_about_cb (self, widget):
        dialog = self.xml.get_widget ("about")
        dialog.set_name (_("Old Lady"))
        dialog.set_version (oldlady.defs.VERSION)
        dialog.present ()

    ##########################################################################
    #
    # App window callbacks
    #
    ##########################################################################

    def make_bid_cb (self, button):
        choose_bid = self.xml.get_widget ("choose-bid")
        iter = choose_bid.get_active_iter ()
        bid = self.legal_bids.get_value (iter, 0)

        self.deal.bid (bid)
        self.play_for_ais ()

    def delete_event_cb (self, window, event):
        gtk.main_quit ()

    ##########################################################################
    #
    # About dialog callbacks
    #
    ##########################################################################

    def about_delete_event_cb (self, dialog, event):
        dialog.hide ()
        return True

    def about_response_cb (self, dialog, response):
        dialog.hide ()

    ##########################################################################
    #
    # Other callbacks
    #
    ##########################################################################

    def render_bid (self, column, renderer, model, iter, player):
        bid = model.get_value (iter, player)
        renderer.set_property ("text", bid is not None and str (bid) or "")


class HandRenderer:
    """
    Helper class that handles rendering and hit detecting of a single player's
    hand.
    """

    def __init__ (self, app, player):
        self.app = app
        self.player = player
        self.rect = None

    def refresh (self):
        """
        Recompute the bounding rectangle and redraw the hand on the tableau.
        """

        tableau = self.app.xml.get_widget ("tableau")
        size = tableau.window.get_size ()
        hand = self.app.deal.hands[self.player]

        if len (hand) == 0:
            self.rect = None
            return
        self.rect = gdk.Rectangle ()

        if sbridge.team (self.player) == sbridge.WEST_EAST:
            self.rect.width = self.app.card_width
            self.rect.height = self.app.card_height + self.app.card_height * (len (hand) - 1) / 4
            self.rect.y = (size[1] - self.rect.height) / 2
        else:
            self.rect.width = self.app.card_width + self.app.card_width * (len (hand) - 1) / 5
            self.rect.height = self.app.card_height
            self.rect.x = (size[0] - self.rect.width) / 2

        if self.player == sbridge.WEST:
            self.rect.x = 10
        elif self.player == sbridge.NORTH:
            self.rect.y = 10
        elif self.player == sbridge.EAST:
            self.rect.x = size[0] - 10 - self.rect.width
        else:
            self.rect.y = size[1] - 10 - self.rect.height

        dst_x = self.rect.x
        dst_y = self.rect.y
        for card in hand:
            if self.player == sbridge.SOUTH or (self.app.deal.opening_lead and self.player == self.app.deal.dummy) or self.app.show_all_cards:
                src_x = (card.rank != sbridge.ACE) and (card.rank - 1) or 0
                src_y = card.suit
            else:
                src_x = 2
                src_y = 4
            tableau.window.draw_pixbuf (None, self.app.cards,
                                        src_x * self.app.card_width, src_y * self.app.card_height,
                                        dst_x, dst_y,
                                        self.app.card_width, self.app.card_height,
                                        gdk.RGB_DITHER_NONE, 0, 0)
            if sbridge.team (self.player) == sbridge.WEST_EAST:
                dst_y += self.app.card_height / 4
            else:
                dst_x += self.app.card_width / 5

    def card_at (self, x, y):
        """
        Return the card rendered at coordinates (x,y) on the tableau, if any.
        """

        if self.rect is None or \
           x < self.rect.x or x >= self.rect.x + self.rect.width or \
           y < self.rect.y or y >= self.rect.y + self.rect.height:
               return None

        if sbridge.team (self.player) == sbridge.WEST_EAST:
            index = (int (y) - self.rect.y) / (self.app.card_height / 4)
        else:
            index = (int (x) - self.rect.x) / (self.app.card_width / 5)

        hand = self.app.deal.hands[self.player]
        if index < len (hand):
            return hand[index]
        else:
            return hand[-1]

if __name__ == "__main__":
    app = App()
    import time
    while True:
        app.tableau_button_release_event_cb (None, None)
        time.sleep(0.1)
        

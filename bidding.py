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

import sbridge
import defs

#import pyswip

import os
import re
#import pexpect

class Bidding:
    """
    Encapsulates the rules for all known bidding systems.

    Mainly, this wraps around SWI Prolog, which does all the real work
    at interpreting bids and choosing new ones.
    """

    def __init__ (self):
        #self.prolog = pyswip.Prolog ()
        #self.prolog.consult (os.path.join (oldlady.defs.PKG_DATA_DIR, "sayc.pl"))
        #self.prolog = pexpect.spawn(defs.SWI_PROLOG)
        #self.prolog.expect('\?- ')
        #self.prolog.sendline("consult('sayc.pl').")
        #self.prolog.expect('\?- ')
        pass
    def choose_bid (self, hand, history):
        """
        Choose the proper bid to make, given the current bidding history.
        """

        # pyswip doesn't let us dive into functors assigned out output
        # variables, so we have to do this the painful way.

        # ... or is this just a bug with the current SVN of pyswip?

        hand_str = self.stringify_hand (hand)
        hist_str = self.stringify_history (history)

        query = "Hand=%s, Hist=%s, ( choose_bid(Hand, Hist, bid(Level,Denom)) ; choose_bid(Hand, Hist, bid(Action)) )" % \
            (hand_str, hist_str)
        #print "DEBUG: query is '%s'" % query

        pro = self.prolog
        pro.sendline(query+'.')
        pro.expect('Hist')
        pro.sendline('')
        pro.expect('\?- ')
        
        buf = pro.before
        
        idx = buf.rfind('Hist')
        choices = buf[idx:].splitlines()[1:]
        #print choices
        r = {'Action':'n','Level':'n','Denom':'n'}
        for line in choices:
            line = line.replace(',','')
            f = line.split('=')
            if len(f) != 2: continue
            r[f[0].strip() ] = f[1].strip()
        if r['Denom'] != 'n': return self.parse_bid (r)
        #print "DEBUG: no results from query"
        return sbridge.Bid (sbridge.PASS)

    def stringify_hand (self, hand):
        """
        Convert a list of cards into its Prolog string equivalent.
        """

        return "[" + ",".join (self.stringify_card (card) for card in hand) + "]"

    def stringify_card (self, card):
        """
        Convert a single card into its Prolog string equivalent.
        """

        if card.rank > 10:
            rank_str = ["jack", "queen", "king", "ace"][card.rank - sbridge.JACK]
        else:
            rank_str = str (card.rank)

        return "card(" + rank_str + "," + self.stringify_denom (card.suit) + ")"

    def stringify_history (self, history):
        """
        Convert a list of bids into its Prolog string equivalent.
        """

        return "[" + ",".join ([self.stringify_bid (bid) for bid in history]) + "]"

    def stringify_bid (self, bid):
        """
        Convert a single bid into its Prolog string equivalent.
        """

        if bid.is_pass ():
            return "bid(pass)"
        elif bid.is_double ():
            return "bid(double)"
        elif bid.is_redouble ():
            return "bid(redouble)"
        else:
            return "bid(" + str (bid.level) + "," + self.stringify_denom (bid.denom) + ")"

    def stringify_denom (self, denom):
        """
        Convert a denomination into its Prolog string equivalent.
        """

        mapping = {
                sbridge.CLUBS:"clubs",
                sbridge.DIAMONDS:"diamonds",
                sbridge.HEARTS:"hearts",
                sbridge.SPADES:"spades",
                sbridge.NO_TRUMP:"no_trump"
        }
        return mapping[denom]

    def parse_bid (self, bid_vars):
        """
        Convert set of Prolog bid search variables into its Python equivalent.
        """

        #print "DEBUG: parsing Action='%s', Level='%s', Denom='%s'" % (bid_vars["Action"], bid_vars["Level"], bid_vars["Denom"])
        if bid_vars["Action"] == "pass":
            return sbridge.Bid (sbridge.PASS)
        elif bid_vars["Action"] == "double":
            return sbridge.Bid (sbridge.DOUBLE)
        elif bid_vars["Action"] == "redouble":
            return sbridge.Bid (sbridge.REDOUBLE)
        else:
            return sbridge.Bid (int (bid_vars["Level"]), self.parse_denom (bid_vars["Denom"]))

    def parse_denom (self, denom_str):
        """
        Convert a Prolog denomination string into its Python equivalent.
        """

        mapping = {
                "clubs":sbridge.CLUBS,
                "diamonds":sbridge.DIAMONDS,
                "hearts":sbridge.HEARTS,
                "spades":sbridge.SPADES,
                "no_trump":sbridge.NO_TRUMP
        }
        return mapping[denom_str]

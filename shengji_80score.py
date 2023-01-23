import random


BID_PASS = 'p'
SUITS_STR = 'CDHSJ'
TOTAL_CARD_NUM = 108
NUM_BRIDGE_CARD = 52
NUM_OF_PLAYER = 4
SUITE_TRUMP = 4
PLAYERS = range(NUM_OF_PLAYER)
NORTH, EAST, SOUTH, WEST = PLAYERS
RANKS = range(17)
TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING, ACE, LEVEL_OTHER, LEVEL_TRUMP, SMALL_JOKER, BIG_JOKER = RANKS
BID_RANK_STR = '23456789TJQKAuUmM'

def get_suite_rank(bid, card):
    assert bid[0] != BID_PASS
    # bid two char, suite CDHSJ + rank 2-A, small mao, big MAO
    rank = card % 13
    suite = card // 13
    if card >= (2*NUM_BRIDGE_CARD):
        suite = SUITE_TRUMP
        rank = SMALL_JOKER + (card - 2*NUM_BRIDGE_CARD) // 2
    elif card >= (NUM_BRIDGE_CARD):
        suite = (card-NUM_BRIDGE_CARD) // 13
    if bid[0] != SUITS_STR[-1]:
        if bid[0] == SUITS_STR[suite]:
            suite = SUITE_TRUMP
        if bid[1] == BID_RANK_STR[rank]:
          suite = SUITE_TRUMP
          if bid[0] == BID_RANK_STR[rank]:
            rank = LEVEL_TRUMP
          else:
            rank = LEVEL_OTHER
    return (suite, rank)
            
def same_suit(bid, card1, card2):
    if bid[0] == BID_PASS:
        return False
    suite1, rank1 = get_suite_rank(bid, card1)
    suite2, rank2 = get_suite_rank(bid, card2)
    if suite1 == suite2:
        return True
    return False

def shuffle():
    """card numbered 0 - 107, 0-51,52-103,104-107 """
    deck = []
    for card in range(TOTAL_CARD_NUM):
        deck.append(card)
    random.shuffle(deck)
    return deck

class sjc(object):
    PLAYERS = range(NUM_OF_PLAYER)
    NORTH, EAST, SOUTH, WEST = PLAYERS

    @staticmethod
    def seat_next(seat):
        return (seat-1) % NUM_OF_PLAYER
    @staticmethod
    def Deal(dealer):
        class Deal(object):
            """record play process"""
            def __init__(self, dealer):
                self.dealer = dealer
        return Deal(dealer)
    def Rubber(dealer):
        class Rubber(object):
            """record multiple deal"""
            def __init__(self, dealer) -> None:
                self.dealer = dealer
            def next_deal(self):
                return shuffle()
        return Rubber(dealer)
            

class sAi(object):
    @staticmethod
    def ComputerPlayer(seat, level):
        class ComputerPlayer(object):
            deck = []
            remaining_cards = []
            declarer = -1
            current_play = [[]]*NUM_OF_PLAYER
            def __init__(self, seat, level):
                self.seat = seat
                self.level = level
            def new_deal(self, deal):
                self.deal = sjc.Deal(deal.dealer)
                for p in sjc.PLAYERS:
                    if deal.hands[p] is not None:
                        self.deal.hands[p] = deal.hands[p][:]
                    else:
                        self.deal.hands[p] = None
                self.bidState = []
                self.history = []
            def bid(self):
                """
                select trump with given level, find the max number
                """
                for card in self.deck:
                    # set fake bid big MAO to parse card
                    suite, rank = get_suite_rank('JM', card)
                    if rank == self.level:
                        if self.declarer < 0:
                            suite = SUITS_STR[suite]
                            rank = BID_RANK_STR[rank]
                            return f'{suite}{rank}'
                return BID_PASS
            def take(self, card):
                self.deck.append(card)
                self.remaining_cards.append(card)
            def bid_made(self, bid_player, bid):
                self.declarer = bid_player
                self.declarer_bid = bid
            def take_extra(self, deck):
                self.extra_deck = deck
            def play_card(self):
                if any(self.current_play):
                    first = self.first_player()
                    lead_cards = self.current_play[first]
                    # find the same kind
                    return self.find_card(lead_cards)
                # TODO better play
                return [self.remaining_cards[0]]
            def find_card(self, lead_cards):
                assert len(lead_cards) == 1
                card = lead_cards[0]
                for c in self.remaining_cards:
                    if same_suit(self.declarer_bid, card, c):
                        return [c]
                return [self.remaining_cards[0]]
            def pick_small(self, cards):
                assert len(cards) == 1
                if len(cards) < 2:
                    return cards
                # TODO check 2+ and other rule
            def prt(self, cards):
                if len(cards) == 1:
                    suite, rank = get_suite_rank(self.declarer_bid, cards[0])
                    return f'{SUITS_STR[suite]}{BID_RANK_STR[rank]}'
                hands = ['']*len(SUITS_STR)
                for card in cards:
                    suite, rank = get_suite_rank(self.declarer_bid, card)
                    hands[suite] += BID_RANK_STR[rank]

                return ':'.join(hands)
            def remember_play(self, player, cards):
                print(self.seat, player, self.prt(cards), self.prt(self.remaining_cards))
                assert len(cards) == 1
                if player == self.seat:
                    for card in cards:
                        idx = self.remaining_cards.index(card)
                        self.remaining_cards.pop(idx)
                self.current_play[player] = cards
                if all(self.current_play):
                    self.current_play = [[]]*NUM_OF_PLAYER
            def next_player(self, first, table):
                p = first
                winner = first
                cards = table[p]
                for _ in range(NUM_OF_PLAYER-1):
                    p = sjc.seat_next(p)
                    if self.cards_bigger(table[p], cards):
                        cards = table[p]
                        winner = p
                return winner
            def first_player(self):
                p = self.seat
                for _ in range(NUM_OF_PLAYER):
                    if self.current_play[p]:
                        return p
                    p = sjc.seat_next(p)
            def cards_bigger(self, cards1, cards2):
                assert len(cards1) == len(cards2) == 1
                suite1, rank1 = get_suite_rank(self.declarer_bid, cards1[0])
                suite2, rank2 = get_suite_rank(self.declarer_bid, cards2[0])
                if suite1 > suite2:
                    return True
                if suite2 < suite1:
                    return False
                if rank1 > rank2:
                    return True
                return False
        return ComputerPlayer(seat, level)


# ---------------- running loop -------
PLAY_CARD, CONFIRM_TRICK, CONFIRM_DEAL, CONFIRM_GAME, CONFIRM_RUBBER = range(5)

def _(a):return a

class App:
    def __init__ (self):
        self.deal_level = [TWO, TWO]
        self.dealer = sjc.NORTH
        level = self.deal_level[self.dealer % 2]
        self.ais = [sAi.ComputerPlayer(seat, level) for seat in sjc.PLAYERS]
        self.start_next_rubber()

    def distribute_deal(self):
        self.deck = shuffle()
        top_bid = BID_PASS
        player = self.dealer
        for i in range(len(self.deck) - 8):
            card = self.deck[i]
            ai = self.ais[player]
            ai.take(card)
            bid = ai.bid()
            if bid != BID_PASS:
                print(player, 'bid', bid)
                for ai in self.ais:
                    ai.bid_made(player, bid)
            player = sjc.seat_next(player)

        # TODO handle top_bid still pass
        self.ais[self.dealer].take_extra(self.deck[-8:])
            
    def start_next_deal(self):
        self.distribute_deal()
        self.play_for_ais()

    def start_next_rubber(self):
        self.start_next_deal()
        
    def play_for_ais(self):
        """
        Have the AIs make their moves, continuing until it is the human
        player's turn again.  If the human is dummy, he will still need
        to confirm each trick.
        """
        p = self.dealer
        ai = self.ais[p]
        while len(self.ais[p].remaining_cards) > 0:
            tm = [[]]*NUM_OF_PLAYER
            for i in range(NUM_OF_PLAYER):
                cards = ai.play_card()
                n = p
                if i == 0:
                    for _ in range(NUM_OF_PLAYER-1):
                        n = sjc.seat_next(n)
                        cards = self.ais[n].pick_small(cards)
                ai.remember_play(p, cards)
                n = p
                for _ in range(NUM_OF_PLAYER-1-i):
                    n = sjc.seat_next(n)
                    self.ais[n].remember_play(p, cards)
                tm[p] = cards
                print('table', tm)
                p = sjc.seat_next(p)
                ai = self.ais[p]
            p = ai.next_player(p, tm)


if __name__ == "__main__":
    App()

        

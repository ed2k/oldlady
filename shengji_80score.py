import random


BID_PASS = 'p'
SUITS_STR = 'CDHSJ'
SUITS_NO_J = 'CDHS'
TOTAL_CARD_NUM = 108
NUM_BRIDGE_CARD = 52
NUM_OF_PLAYER = 4
SUITE_TRUMP = 4
PLAYERS = range(NUM_OF_PLAYER)
NORTH, EAST, SOUTH, WEST = PLAYERS
BID_RANK_STR = '23456789TJQKAuvwUmM'
RANKS = range(len(BID_RANK_STR))
TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING, ACE, V_TRUMP_u, V_TRUMP_v, V_TRUMP_w, MAIN_TRUMP, SMALL_JOKER, BIG_JOKER = RANKS
VICE_TRUMP_RANKS = [V_TRUMP_u, V_TRUMP_v, V_TRUMP_w]


def str_card(card):
    if card > 105:
        return 'JM'
    if card > 103:
        return 'Jm'
    if card > 51:
        card = card - 52   
    rank = card % 13
    suite = card // 13
    return f'{SUITS_STR[suite]}{BID_RANK_STR[rank]}'
    
def get_suite_rank(bid, card):
    assert bid[0] != BID_PASS
    # bid two char, suite CDHSJ + rank 2-A, 3-vice-trump(uvw same rank), 
    # 1-main-trump U, 1small mao, big MAO
    rank = card % 13
    suite = card // 13
    if card >= (2*NUM_BRIDGE_CARD):
        suite = SUITE_TRUMP
        rank = SMALL_JOKER + (card - 2*NUM_BRIDGE_CARD) // 2
    elif card >= (NUM_BRIDGE_CARD):
        suite = (card-NUM_BRIDGE_CARD) // 13
    if bid[0] != SUITS_STR[-1]: # bid suit
        old_rank, old_suite = rank, suite
        if bid[1] == BID_RANK_STR[old_rank]:
          suite = SUITE_TRUMP
          if bid[0] == SUITS_NO_J[old_suite]:
            rank = MAIN_TRUMP
          else:
            # convert to trump rank based on suit index
            v_trump_rank = list(SUITS_NO_J)
            v_trump_rank.remove(bid[0])
            index = v_trump_rank.index(SUITS_NO_J[old_suite])
            rank = V_TRUMP_u + index
        if bid[0] == SUITS_STR[suite]:
            suite = SUITE_TRUMP
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
            def bid(self, current_bid):
                """
                current_bid contains seat and bid string
                select trump with given level, find the max number
                TODO, handle over bid
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
                """TODO save whole bid history"""
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
                print(self.seat, player, cards, self.prt(cards), self.prt(self.remaining_cards), self.remaining_cards)
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
                """assume cards2 plays first"""
                assert len(cards1) == len(cards2) == 1
                suite1, rank1 = get_suite_rank(self.declarer_bid, cards1[0])
                suite2, rank2 = get_suite_rank(self.declarer_bid, cards2[0])
                if suite1 > suite2:
                    return True
                if suite2 < suite1:
                    return False
                if rank1 in VICE_TRUMP_RANKS and rank2 in VICE_TRUMP_RANKS:
                    return False
                if rank1 > rank2:
                    return True
                return False
        return ComputerPlayer(seat, level)


# ---------------- running loop -------
PLAY_CARD, CONFIRM_TRICK, CONFIRM_DEAL, CONFIRM_GAME, CONFIRM_RUBBER = range(5)

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
            bid = ai.bid(top_bid)
            if bid != BID_PASS:
                print(player, 'bid', bid)
                for ai in self.ais:
                    ai.bid_made(player, bid)
            player = sjc.seat_next(player)

        # TODO handle top_bid still pass
        # TODO in the first round, bid winner take the extra (bottom)
        # TODO following round last round winner take turn in counter clockwise
        self.ais[self.dealer].take_extra(self.deck[-8:])
            
    def start_next_deal(self):
        self.distribute_deal()
        self.play_for_ais()

    def start_next_rubber(self):
        """start from 2, bid winner take the bottom. then winning team member
        in the counter clockwise take the bottom.
        """
        self.start_next_deal()
        
    def play_for_ais(self):
        """
        Have the AIs make their moves, continuing until it is the human
        player's turn again.  If the human is dummy, he will still need
        to confirm each trick.
        """
        player = self.dealer
        while len(self.ais[player].remaining_cards) > 0:
            ai = self.ais[player]
            tm = [[]]*NUM_OF_PLAYER
            for i in range(NUM_OF_PLAYER):
                cards = ai.play_card()
                n = player
                if i == 0: # check if play is valid, if not pick small
                    for _ in range(NUM_OF_PLAYER-1):
                        n = sjc.seat_next(n)
                        cards = self.ais[n].pick_small(cards)
                n = player
                for _ in range(NUM_OF_PLAYER):
                    self.ais[n].remember_play(player, cards)
                    n = sjc.seat_next(n)
                tm[player] = cards
                str_tm = []
                for c in tm:
                    if len(c) == 1:
                        str_tm.append(str_card(c[0]))
                    else:
                        str_tm.append('')                    
                print('table', str_tm)
                player = sjc.seat_next(player)
                ai = self.ais[player]
            # TODO calculate score
            player = ai.next_player(player, tm)


if __name__ == "__main__":
    App()
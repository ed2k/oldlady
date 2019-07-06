% Old Lady
% Copyright (C) 2007 Paul Kuliniewicz <paul@kuliniewicz.org>
%
% This program is free software; you can redistribute it and/or modify
% it under the terms of the GNU General Public License as published by
% the Free Software Foundation; either version 2, or (at your option)
% any later version.
%
% This program is distributed in the hope that it will be useful,
% but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
% GNU General Public License for more details.
%
% You should have received a copy of the GNU General Public License
% along with this program; if not, write to the Free Software
% Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02111-1301, USA.

% Standard American Yellow Card bidding, written for SWI-Prolog.

:- use_module(library('clp/bounds')).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% Basic constraints, independent of the bidding system
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

all_constraints(Hand, AllStats) :-
	AllStats = all_stats(SelfStats, LeftStats, PartnerStats, RightStats),
	hand_constraints(SelfStats),
	hand_constraints(LeftStats),
	hand_constraints(PartnerStats),
	hand_constraints(RightStats),
	deal_constraints(AllStats),
	evaluate_hand(Hand, SelfStats).

hand_constraints(Stats) :-
	Stats = stats(HCP, Spades, Hearts, Diamonds, Clubs),
	HCP in 0 .. 40,
	Spades in 0 .. 13,
	Hearts in 0 .. 13,
	Diamonds in 0 .. 13,
	Clubs in 0 .. 13,
	13 #= Spades + Hearts + Diamonds + Clubs.

deal_constraints(AllStats) :-
	AllStats = all_stats(SelfStats, LeftStats, PartnerStats, RightStats),
	SelfStats = stats(SelfHCP, SelfSpades, SelfHearts, SelfDiamonds, SelfClubs),
	LeftStats = stats(LeftHCP, LeftSpades, LeftHearts, LeftDiamonds, LeftClubs),
	PartnerStats = stats(PartnerHCP, PartnerSpades, PartnerHearts, PartnerDiamonds, PartnerClubs),
	RightStats = stats(RightHCP, RightSpades, RightHearts, RightDiamonds, RightClubs),
	40 #= SelfHCP + LeftHCP + PartnerHCP + RightHCP,
	13 #= SelfSpades + LeftSpades + PartnerSpades + RightSpades,
	13 #= SelfHearts + LeftHearts + PartnerHearts + RightHearts,
	13 #= SelfDiamonds + LeftDiamonds + PartnerDiamonds + RightDiamonds,
	13 #= SelfClubs + LeftClubs + PartnerClubs + RightClubs.

evaluate_hand(Hand, Stats) :-
	Stats = stats(HCP, Spades, Hearts, Diamonds, Clubs),
	hcp(Hand, HCP),
	suit_length(spades, Hand, Spades),
	suit_length(hearts, Hand, Hearts),
	suit_length(diamonds, Hand, Diamonds),
	suit_length(clubs, Hand, Clubs).

hcp(card(ace,_), 4) :- !.
hcp(card(king,_), 3) :- !.
hcp(card(queen,_), 2) :- !.
hcp(card(jack,_), 1) :- !.
hcp(card(_,_), 0) :- !.

hcp(Hand, HCP) :-
	hcp_acc(Hand, 0, HCP).
hcp_acc([], HCP, HCP).
hcp_acc([Card | Hand], Acc, HCP) :-
	hcp(Card, CardHCP),
	NewAcc is Acc + CardHCP,
	hcp_acc(Hand, NewAcc, HCP).

suit_length(Suit, Hand, Length) :-
	suit_length_acc(Suit, Hand, 0, Length).
suit_length_acc(_, [], Length, Length).
suit_length_acc(Suit, [card(_,CardSuit) | Hand], Acc, Length) :-
	( CardSuit = Suit -> NewAcc is Acc + 1 ; NewAcc = Acc ),
	suit_length_acc(Suit, Hand, NewAcc, Length).

denom_lt_imm(clubs, diamonds).
denom_lt_imm(diamonds, hearts).
denom_lt_imm(hearts, spades).
denom_lt_imm(spades, no_trump).
denom_lt(X, Y) :-
	denom_lt_imm(X, Y).
denom_lt(X, Y) :-
	denom_lt_imm(X, Z),
	denom_lt(Z, Y).

minor(clubs).
minor(diamonds).

major(hearts).
major(spades).

game_level(Suit, 5) :-
	minor(Suit).
game_level(Suit, 4) :-
	major(Suit).
game_level(no_trump, 3).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% Abstract interface for reading stats, to allow for additional
% stats to be added without having to rewrite all rules that try
% to look inside them.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

stat_hcp(Stats, HCP) :-
	Stats = stats(HCP, _, _, _, _).

stat_length(spades, Stats, Length) :-
	Stats = stats(_, Length, _, _, _).
stat_length(hearts, Stats, Length) :-
	Stats = stats(_, _, Length, _, _).
stat_length(diamonds, Stats, Length) :-
	Stats = stats(_, _, _, Length, _).
stat_length(clubs, Stats, Length) :-
	Stats = stats(_, _, _, _, Length).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% Generic bid decision and evaluation rules
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

choose_bid(Hand, BidHistory, Bid) :-
	all_constraints(Hand, all_stats(Self, Left, Partner, Right)),
	interpret_history(all_stats(Right, Self, Left, Partner), BidHistory, _, OwnState),
	bid(OwnState, all_stats(Self, Left, Partner, Right), BidHistory, Bid, _),
	legal_bid(Bid, BidHistory).

interpret_history(_, [], opening, opening).
interpret_history(all_stats(Self, Left, Partner, Right), [Bid | PastBids], OwnState, EnemyState) :-
	interpret_history(all_stats(Right, Self, Left, Partner), PastBids, EnemyState, PrevOwnState),
	bid(PrevOwnState, all_stats(Self, Left, Partner, Right), PastBids, Bid, OwnState).

legal_bid(bid(pass), _).
legal_bid(bid(_,_), []).
legal_bid(bid(Level,Denom), [bid(_) | PastBids]) :-
	legal_bid(bid(Level,Denom), PastBids).
legal_bid(bid(Level,_), [bid(OldLevel,_) | _]) :-
	Level > OldLevel.
legal_bid(bid(Level,Denom), [bid(Level,OldDenom) | _]) :-
	denom_lt(OldDenom, Denom).
legal_bid(bid(double), [bid(_,_) | _]).
legal_bid(bid(double), [bid(pass), bid(pass), bid(_,_) | _]).
legal_bid(bid(redouble), [bid(double) | _]).
legal_bid(bid(redouble), [bid(pass), bid(pass), bid(double) | _]).

balanced(SelfStats) :-
	forall(stat_length(_, SelfStats, Length), Length in 2..5).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% SAYC-specific rules
%
% generic format for bid:
%   bid(OldState, AllStats, BidHistory, Bid, NewState)
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% *** Helpers used in multiple rules ***

deny_majors(Threshold, Stats) :-
	stat_length(hearts, Stats, Hearts),
	stat_length(spades, Stats, Spades),
	Hearts #< Threshold,
	Spades #< Threshold.

deny_opener_support(Suit, Stats) :-
	stat_length(Suit, Stats, Length),
	( major(Suit) -> Length #< 3 ; Length #< 5 ).

% *** Opening bids ***

bid(opening, all_stats(SelfStats, _, _, _), _, bid(1,spades), response_1) :-
	stat_hcp(SelfStats, HCP),
	stat_length(spades, SelfStats, Spades),
	stat_length(hearts, SelfStats, Hearts),
	HCP #>= 13,
	Spades #>= 5,
	Spades #> Hearts.

bid(opening, all_stats(SelfStats, _, _, _), _, bid(1,hearts), response_1) :-
	stat_hcp(SelfStats, HCP),
	stat_length(spades, SelfStats, Spades),
	stat_length(hearts, SelfStats, Hearts),
	HCP #>= 13,
	Hearts #>= 5,
	Hearts #>= Spades.

bid(opening, all_stats(SelfStats, _, _, _), _, bid(1,diamonds), response_1) :-
	stat_hcp(SelfStats, HCP),
	stat_length(spades, SelfStats, Spades),
	stat_length(hearts, SelfStats, Hearts),
	stat_length(diamonds, SelfStats, Diamonds),
	stat_length(clubs, SelfStats, Clubs),
	HCP #>= 13,
	Spades #< 5,
	Hearts #< 5,
	Diamonds #>= 3,
	Diamonds #> Clubs.

bid(opening, all_stats(SelfStats, _, _, _), _, bid(1,clubs), response_1) :-
	stat_hcp(SelfStats, HCP),
	stat_length(spades, SelfStats, Spades),
	stat_length(hearts, SelfStats, Hearts),
	stat_length(diamonds, SelfStats, Diamonds),
	stat_length(clubs, SelfStats, Clubs),
	HCP #>= 13,
	Spades #< 5,
	Hearts #< 5,
	Clubs #>= 3,
	Clubs #>= Diamonds.

bid(opening, all_stats(SelfStats, _, _, _), _, bid(pass), opening) :-
	stat_hcp(SelfStats, HCP),
	HCP #< 13.

% *** Responses to a 1 trump opener. ***

% minimal raise: confirm support but minimal HCP
% also denies any 4-card majors if raising a minor
bid(response_1, all_stats(SelfStats, _, _, _), [_, bid(1,Suit) | _], bid(2,Suit), elevate) :-
	major(Suit),
	stat_hcp(SelfStats, HCP),
	stat_length(Suit, SelfStats, Length),
	HCP in 6..10,
	Length #>= 3.
bid(response_1, all_stats(SelfStats, _, _, _), [_, bid(1,Suit) | _], bid(2,Suit), elevate) :-
	minor(Suit),
	stat_hcp(SelfStats, HCP),
	stat_length(Suit, SelfStats, Length),
	HCP in 6..10,
	Length #>= 5,
	deny_majors(4, SelfStats).

% limit raise: confirm support and moderate HCP
% also denies any 4-card majors if raising a minor
bid(response_1, all_stats(SelfStats, _, _, _), [_, bid(1,Suit) | _], bid(3,Suit), elevate) :-
	major(Suit),
	stat_hcp(SelfStats, HCP),
	stat_length(Suit, SelfStats, Length),
	HCP in 11..12,
	Length #>= 3.
bid(response_1, all_stats(SelfStats, _, _, _), [_, bid(1,Suit) | _], bid(3,Suit), elevate) :-
	minor(Suit),
	stat_hcp(SelfStats, HCP),
	stat_length(Suit, SelfStats, Length),
	HCP in 11..12,
	Length #>= 5,
	deny_majors(4, SelfStats).

% strong suit support and a void/singleton but low HCP
% FIXME: could result in other players incorrectly guessing which suit the void/singleton is in
bid(response_1, all_stats(SelfStats, _, _, _), [_, bid(1,Suit) | _], bid(GameLevel,Suit), done) :-
	game_level(Suit, GameLevel),
	stat_hcp(SelfStats, HCP),
	stat_length(Suit, SelfStats, Length),
	stat_length(_, SelfStats, ShortLength),
	HCP #=< 9,
	Length #>= 5,
	ShortLength #=< 1.

% shift at the 1-level to longest suit
% diamonds denies 4-card majors; 4-4 is up the line; 5-5 or 6-6 is down the line
bid(response_1, all_stats(SelfStats, _, _, _), [_, bid(1,clubs) | _], bid(1,diamonds), rebid_1) :-
	stat_hcp(SelfStats, HCP),
	stat_length(clubs, SelfStats, Clubs),
	stat_length(diamonds, SelfStats, Diamonds),
	stat_length(hearts, SelfStats, Hearts),
	stat_length(spades, SelfStats, Spades),
	HCP #>= 6,
	Clubs #< 5,
	Diamonds #>= 4,
	Hearts #< 4,
	Spades #< 4.
bid(response_1, all_stats(SelfStats, _, _, _), [_, bid(1,Minor) | _], bid(1,hearts), rebid_1) :-
	minor(Minor),
	stat_hcp(SelfStats, HCP),
	stat_length(hearts, SelfStats, Hearts),
	stat_length(spades, SelfStats, Spades),
	HCP #>= 6,
	Hearts #>= 4,
	Hearts #>= Spades,
	Hearts #> 4 #=> Hearts #> Spades.
bid(response_1, all_stats(SelfStats, _, _, _), [_, bid(1,Minor) | _], bid(1,spades), rebid_1) :-
	minor(Minor),
	stat_hcp(SelfStats, HCP),
	stat_length(hearts, SelfStats, Hearts),
	stat_length(spades, SelfStats, Spades),
	HCP #>= 6,
	Spades #>= 4,
	Spades #>= Hearts,
	Spades #= 4 #=> Hearts #< 4.
bid(response_1, all_stats(SelfStats, _, _, _), [_, bid(1,hearts) | _], bid(1,spades), rebid_1) :-
	stat_hcp(SelfStats, HCP),
	stat_length(hearts, SelfStats, Hearts),
	stat_length(spades, SelfStats, Spades),
	HCP #>= 6,
	Hearts #< 3,
	Spades #>= 4.

% non-jump shift at 2 level, denying fit
% FIXME: should this also deny 4 cards in any of the skipped suits?
bid(response_1, all_stats(SelfStats, _, _, _), [_, bid(1,PartnerSuit) | _], bid(2,Suit), rebid_2) :-
	denom_lt(Suit, PartnerSuit),
	stat_hcp(SelfStats, HCP),
	stat_length(Suit, SelfStats, SuitLength),
	HCP #>= 11,
	deny_opener_support(PartnerSuit, SelfStats),
	SuitLength #>= 4.

% jump shift at 2 level, denying fit
% FIXME: also check strength/quality of the new suit
% FIXME: should this also deny 4 cards in any of the skipped suits?
% FIXME: verify next state
bid(response_1, all_stats(SelfStats, _, _, _), [_, bid(1,PartnerSuit) | _], bid(2,Suit), rebid_2) :-
	denom_lt(Suit, PartnerSuit),
	stat_hcp(SelfStats, HCP),
	stat_length(Suit, SelfStats, SuitLength),
	HCP #>= 19,
	deny_opener_support(PartnerSuit, SelfStats),
	SuitLength #> 5.

% jump shift at 3 level, denying fit
% FIXME: also check strength/quality of the new suit
% FIXME: should this also deny 4 cards in any of the skipped suits?
% FIXME: verify next state
bid(response_1, all_stats(SelfStats, _, _, _), [_, bid(1,PartnerSuit) | _], bid(3,Suit), rebid_3) :-
	denom_lt(PartnerSuit, Suit),
	stat_hcp(SelfStats, HCP),
	stat_length(Suit, SelfStats, SuitLength),
	HCP #>= 19,
	deny_opener_support(PartnerSuit, SelfStats),
	SuitLength #> 5.

% minimal HCP and no showable suits at the 1 level
bid(response_1, all_stats(SelfStats, _, _, _), [_, bid(1,PartnerSuit) | _], bid(1,no_trump), rebid_1nt) :-
	stat_hcp(SelfStats, HCP),
	HCP in 6..10,
	deny_opener_support(PartnerSuit, SelfStats),
	forall((denom_lt(PartnerSuit, Suit), stat_length(Suit, SelfStats, Length)), Length #< 4).

% Jacoby 2NT, game forcing, asking for short suit
bid(response_1, all_stats(SelfStats, _, _, _), _, bid(2,no_trump), jacoby_2nt) :-
	stat_hcp(SelfStats, HCP),
	HCP #>= 13.

% 15-17 HCP, balanced with two-card support
% FIXME: check for lack of honors in partner's suit and/or lots of J,Q rather than K,A
bid(response_1, all_stats(SelfStats, _, _, _), [_, bid(1,Suit) | _], bid(3,no_trump), done) :-
	stat_hcp(SelfStats, HCP),
	stat_length(Suit, SelfStats, Length),
	HCP in 15..17,
	balanced(SelfStats),
	Length #>= 2.

% absolutely nothing
bid(response_1, all_stats(SelfStats, _, _, _), _, bid(pass), done) :-
	stat_hcp(SelfStats, HCP),
	HCP #< 6.

% *** Opener's rebids after a 1 trump response. ***

% confirm 4-card support for the new suit with minimum HCP
bid(rebid_1, all_stats(SelfStats, _, _, _), [_, bid(1,Suit) | _], bid(2,Suit), elevate) :-
	stat_hcp(SelfStats, HCP),
	stat_length(Suit, SelfStats, Length),
	HCP in 13..16,
	Length #>= 4.

% confirm 4-card support for the new suit with moderate HCP
bid(rebid_1, all_stats(SelfStats, _, _, _), [_, bid(1,Suit) | _], bid(3,Suit), elevate) :-
	stat_hcp(SelfStats, HCP),
	stat_length(Suit, SelfStats, Length),
	HCP in 17..18,
	Length #>= 4.

% confirm 4-card support for the new suit with high HCP
bid(rebid_1, all_stats(SelfStats, _, _, _), [_, bid(1,Suit) | _], bid(GameLevel,Suit), done) :-
	game_level(Suit, GameLevel),
	stat_hcp(SelfStats, HCP),
	stat_length(Suit, SelfStats, Length),
	HCP #>= 19,
	Length #>= 4.

% deny support and shift up-the-line at the 1 level
bid(rebid_1, all_stats(SelfStats, _, _, _), [_, bid(1,PartnerSuit) | _], bid(1,Suit), response_1_again) :-
	denom_lt(PartnerSuit, Suit),
	stat_hcp(SelfStats, HCP),
	stat_length(PartnerSuit, SelfStats, PartnerSuitLength),
	stat_length(Suit, SelfStats, SuitLength),
	HCP in 13..18,
	PartnerSuitLength #< 4,
	SuitLength #>= 4,
	forall((denom_lt(PartnerSuit, SkippedSuit), denom_lt(SkippedSuit, Suit), stat_length(SkippedSuit, SelfStats, SkippedLength)),
	       SkippedLength #< 4).

% deny support and jump shift up-the-line at the 2 level
bid(rebid_1, all_stats(SelfStats, _, _, _), [_, bid(1,PartnerSuit) | _], bid(2,Suit), response_2_again) :-
	denom_lt(PartnerSuit, Suit),
	stat_hcp(SelfStats, HCP),
	stat_length(PartnerSuit, SelfStats, PartnerSuitLength),
	stat_length(Suit, SelfStats, SuitLength),
	HCP #>= 19,
	PartnerSuitLength #< 4,
	SuitLength #>= 4,
	forall((denom_lt(PartnerSuit, SkippedSuit), denom_lt(SkippedSuit, Suit), stat_length(SkippedSuit, SelfStats, SkippedLength)),
	       SkippedLength #< 4).

% deny support and non-reverse shift at the 2 level
bid(rebid_1, all_stats(SelfStats, _, _, _), [_, bid(1,PartnerSuit), _, bid(1,PreviousSuit) | _], bid(2,Suit), response_2_again) :-
	denom_lt(Suit, PreviousSuit),
	stat_hcp(SelfStats, HCP),
	stat_length(PartnerSuit, SelfStats, PartnerSuitLength),
	stat_length(Suit, SelfStats, SuitLength),
	HCP in 13..16,
	PartnerSuitLength #< 4,
	SuitLength #>= 4,
	forall((denom_lt(PartnerSuit, SkippedSuit), stat_length(SkippedSuit, SelfStats, SkippedLength)),
	       SkippedLength #< 4),
	forall((denom_lt(SkippedSuit, Suit), stat_length(SkippedSuit, SelfStats, SkippedLength)),
	       SkippedLength #< 4).

% deny support and reverse shift at the 2 level
bid(rebid_1, all_stats(SelfStats, _, _, _), [_, bid(1,PartnerSuit), _, bid(1,PreviousSuit) | _], bid(2,Suit), response_2_again) :-
	denom_lt(PreviousSuit, Suit),
	denom_lt(Suit, PartnerSuit),
	stat_hcp(SelfStats, HCP),
	stat_length(PreviousSuit, SelfStats, PreviousSuitLength),
	stat_length(PartnerSuit, SelfStats, PartnerSuitLength),
	stat_length(Suit, SelfStats, SuitLength),
	HCP in 17..18,
	PreviousSuitLength #>= 5,
	PartnerSuitLength #< 4,
	SuitLength #>= 4.

% deny support and rebid original suit to show extra length
bid(rebid_1, all_stats(SelfStats, _, _, _), [_, bid(1,PartnerSuit), _, bid(1,PreviousSuit) | _], bid(2,PreviousSuit), unknown) :-
	stat_hcp(SelfStats, HCP),
	stat_length(PartnerSuit, SelfStats, PartnerSuitLength),
	stat_length(PreviousSuit, SelfStats, PreviousSuitLength),
	HCP in 13..16,
	PartnerSuitLength #< 4,
	PreviousSuitLength #>= 6.

% deny support and jump rebid original suit to show extra length and maximum HCP
bid(rebid_1, all_stats(SelfStats, _, _, _), [_, bid(1,PartnerSuit), _, bid(1,PreviousSuit) | _], bid(3,PreviousSuit), unknown) :-
	stat_hcp(SelfStats, HCP),
	stat_length(PartnerSuit, SelfStats, PartnerSuitLength),
	stat_length(PreviousSuit, SelfStats, PreviousSuitLength),
	HCP #>= 19,
	PartnerSuitLength #< 4,
	PreviousSuitLength #>= 6.

% deny support and any other 4-card suits with minimal HCP
bid(rebid_1, all_stats(SelfStats, _, _, _), [_, bid(1,PartnerSuit) | _], bid(1,no_trump), unknown) :-
	stat_hcp(SelfStats, HCP),
	stat_length(PartnerSuit, SelfStats, PartnerSuitLength),
	HCP in 13..16,
	PartnerSuitLength #< 4,
	forall((denom_lt(PartnerSuit, SkippedSuit), stat_length(SkippedSuit, SelfStats, SkippedLength)),
	       SkippedLength #< 4).

% deny support and any other 4-card suits with maximal HCP
bid(rebid_1, all_stats(SelfStats, _, _, _), [_, bid(1,PartnerSuit) | _], bid(2,no_trump), unknown) :-
	stat_hcp(SelfStats, HCP),
	stat_length(PartnerSuit, SelfStats, PartnerSuitLength),
	HCP #>= 19,
	PartnerSuitLength #< 4,
	forall((denom_lt(PartnerSuit, SkippedSuit), stat_length(SkippedSuit, SelfStats, SkippedLength)),
	       SkippedLength #< 4).

% *** Miscellaneous ***

bid(done, _, _, bid(pass), done).

% vim: ft=prolog

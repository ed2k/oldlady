"""
bid system 
name_state variables
TODO, get all blue team clubs conventions in code
ex: controls A=2 K=1, canape, distribution
inteference of opening1
"""

btc2k_opening1= [
    ['1n','hcp in 15..17, shape_type is balanced'],  # TODO 5422 solid doubleton in the majors
    ['1s','hcp in 12..16, s > h, s >= 5'],
    ['1h','hcp in 12..16, h >= 5,h >= s'],
    ['1d','hcp in 12..16, s < 5,h < 5,d >= 3, d > c'],
    ['1c','hcp >= 17'], # TODO how to express forcing
    ['2n','hcp in 22..24, shape_type is balanced'],
    ['3n','hcp in 25..27, shape_type is balanced'],
    ['2c','hcp in 12..16, c > 5'], # TODO 2 top honors, possible 4 cards in a side suit major
    ['2d','hcp in 12..16, d > 5'],
    ['2h','hcp in 8..12, h == 6'], # TODO good suit, 3rd 4th quite weak hands
    ['2s','hcp in 8..12, s == 6'],
    ['3c','hcp < 13, c == 7'],
    ['3d','hcp < 13, d == 7'],
    ['3h','hcp < 13, h == 7'],
    ['3s','hcp < 13, s == 7'],               
    ['rule of two and three','hcp < 13, longest >= 7'],
    ['game in hand', 'hcp+shortage+length >= 26'],
    ]
btc2k_opening2=[
    [' x','hcp >= 16'],
    [' x','opening1_type is 1major','hcp >= 12, suit < 4'],
    [' x','opening1_type is 1minor','hcp >= 12, suit < 4'],
    ['new0','hcp in 9..16, newsuit0 >= 5'],
    ['new','hcp in 11..16, newsuit >= 5'],
    ['jumpshift', 'opening1_type isnot nt, hcp in 6..10, newsuit >= 6'],
]
""" short means the length of shortest suit, long means the lenght of longest suit
      suit the one in opening bid
      newsuit0 means if bid only in same level (c -> dhs, d -> hs)
for easy implementation to find bidding from rule, branch rules are from bidding history,
not from hand distribution
      """
btc2k_respons1= [
    ['opening1_type is 1major',
     ['+1','hcp+shortage in 6..10, suit >= 3'],
     ['+2','hcp+shortage >= 13,suit >= 3'],
     ['1n','hcp in 6..10'],
     ['2c','hcp in 6..18, c >= 4'],
     ['2d','hcp in 6..18, d >= 4'],
     ['2h','opening1 is 1s, hcp in 11..18, h >= 5'],
     ['1s','opening1 is 1h, hcp in 6..18, s >= 4'],
     ['+3','hcp+shortage in 6..10, suit >= 4, shape_type is unbalanced'],
     ['jumpshift','hcp >= 19'],
     ['new','hcp in 11..12'],
     ],
    ['opening1_type is 1minor',
     ['1d','opening1 is 1c, hcp < 7, controls <= 2'],
     ['1h','opening1 is 1c, hcp >= 7, controls <= 2'], # TODO GF
     ['1s','opening1 is 1c, controls in 3..3'],
     ['1n','opening1 is 1c, controls in 4..4'],
     ['2c','opening1 is 1c, controls in 5..5'],
     ['2d','opening1 is 1c, controls in 6..6'],
     ['1h','opening1 is 1d, hcp in 6..18, h >= 4'],
     ['1s','opening1 is 1d, hcp in 6..18, s >= 4'],
     ['2n','opening1_type is 1minor, hcp in 13..15, shape_type is balanced'],
     ['3n','opening1_type is 1minor, hcp in 16..18, shape_type is balanced'],          
     ['2d','opening1 is 1d, hcp in 6..10, d >= 4'],
     ['2d','opening1 is 1d, hcp >= 13, d >= 4'],
     ['new','hcp in 11..12'],
     ['jumpshift','hcp >= 19'],     
     ],
    ['opening1 is 1n', 'refer respons1_1n'],
    ['opening1 is 2c',
     ['2d','hcp <= 7'] , ['2n','hcp >= 8, s < 5, h < 5, d < 5, c < 5'],
     ['2s' , 'hcp >= 8, s >= 5'], ['2h' ,'hcp >= 8, h >=  5'],
     ['3c' , 'hcp >= 8, c >= 5'], ['3d' ,'hcp >= 8, d >=  5']],
    ['opening1_type is 2d',
     ['3d', 'hcp < 10, d >= 3']],
    ['opening1_type is 2major',
     ['2n', 'hcp > 10']],
    ['opening1_type is 3minor',
     ['+2', 'hcp in 13..15'], ['+3', 'hcp in 16..20'], ['+4', 'hcp > 20']],
    ['opening1_type is 3major',
     ['+1', 'hcp in 13..15'], ['+3', 'hcp in 16..20'], ['+4', 'hcp > 20']],
    ]
btc2k_respons1_1n = [
    ['shape_type is balanced',
     [' p','hcp <= 7'],
     ['2n', 'hcp in 8..9'],
     ['3n', 'hcp in 10..14'],
     ['4n', 'hcp in 15..16'],
     ['6n', 'hcp in 17..19'],
     ['7n', 'hcp >= 20']],
    # ['shape_type is semibalanced',
    #  [' p','hcp <= 7'],
    #  ['2n', 'hcp in 8..9'],
    #  ['3n', 'hcp in 10..14'],
    #  ['4n', 'hcp in 15..16'],
    #  ['6n', 'hcp in 17..19'],
    #  ['7n', 'hcp >= 20']],
    ['shape_type is unbalanced',
     ['2s', 'hcp <= 7, s >= 5'],
     ['2h', 'hcp <= 7, h >= 5'],
     ['2d', 'hcp <= 8, d >= 5'],
     ['2d','hcp <= 8, c >= 5'],
     ['2c', 'hcp >= 8, len_major >= 4'],
     ['3_', 'hcp >= 9, longest >= 5'],
     ['6_', 'hcp in 17..19, longest >= 6'],
     ['7_', 'hcp >= 21, longest >= 6'],
     ['game', 'hcp >= 9, longest >= 6']],
    ['len_major >= 5', 'case 1'],
    ['len_minor >= 5', 'case 0'],
    ]
btc2k_respons2 = [['new','hcp > 20']]
btc2k_openerNextBid = [
    ['opening1_type is 1major, respons1_type is 2major',
     ['+1','respons1_type is +1, hcp+shortage in 16..18'],
     ['+2','respons1_type is +1, hcp+shortage in 19..21']],
    ['opening1_type is 1major, respons1_type is 3s',
     ['+1','respons1_type is +2, hcp+shortage in 13..15'],
     ['+2','respons1_type is +2, hcp+shortage in 16..18'],
     ['+3','respons1_type is +2, hcp+shortage in 19..21']],
    ['opening1_type is 1major, respons1 is 1n',
     ['new','hcp in 13..15, shape_type is unbalanced'],
     ['2n','hcp in 16..18'],
     ['3_','hcp+shortage in 16..18'],
     ['3n','hcp in 19..21'],
     ['4_','hcp+shortage in 19..21']],
    ['opening1_type is 1major, respons1 is 2n',
     ['3n','hcp in 13..17'],
     ['4_','hcp+shortage in 13..18'],  
     ['5n','hcp in 18..19'],
     ['6n','hcp in 20..21'],
     ['6_','hcp+shortage in 19..21']],
    ['opening1_type is 1major, respons1 is 3n',
     ['5n','hcp in 15..16'],
     ['4_','hcp+shortage in 13..15'],  
     ['5n','hcp in 18..19'],
     ['6n','hcp in 20..21'],
     ['6_','hcp+shortage in 19..21']],
    ['opening1_type is 1minor, respons1_type is 2major',
     ['+1','respons1_type is +1, hcp+shortage in 16..18'],
     ['+2','respons1_type is +1, hcp+shortage in 19..21']],
    ['opening1_type is 1major, respons1_type is 3s',
     ['+1','respons1_type is +2, hcp+shortage in 13..15'],
     ['+2','respons1_type is +2, hcp+shortage in 16..18'],
     ['+3','respons1_type is +2, hcp+shortage in 19..21']],
    ['opening1_type is 1major, respons1 is 1n',
     ['new','hcp in 13..15, shape_type is unbalanced'],
     ['2n','hcp in 16..18'],
     ['3_','hcp+shortage in 16..18'],
     ['3n','hcp in 19..21'],
     ['4_','hcp+shortage in 19..21']],
    ['opening1_type is 1major, respons1 is 2n',
     ['3n','hcp in 13..17'],
     ['4_','hcp+shortage in 13..18'],  
     ['5n','hcp in 18..19'],
     ['6n','hcp in 20..21'],
     ['6_','hcp+shortage in 19..21']],
    ['opening1_type is 1major, respons1 is 3n',
     ['5n','hcp in 15..16'],
     ['4_','hcp+shortage in 13..15'],  
     ['5n','hcp in 18..19'],
     ['6n','hcp in 20..21'],
     ['6_','hcp+shortage in 19..21']],
    ['opening1 is 1c, respons1 is 1d',
     ['1h','h >= s, h >= 4, s >= 4, shape_type is balanced, hcp in 18..20'], # TODO better_than
     ['1h','h >= s, h >= 4, shape_type is balanced, hcp in 21..22'], # TODO better_than
     ['1s','s >= h, s >= 4, shape_type is balanced, hcp in 21..22'], # TODO better_than
     ['1s','s >= h, h >= 4, s >= 4, shape_type is balanced, hcp in 18..20'], # TODO better_than
     ['1n','len_major <= 4, shape_type is balanced, hcp in 18..20'],
     ['2c','shape_type is balanced, hcp >= 25, Forcing1'],
     ['2c','c >= 5, forcing1'],
     ['2d','d >= 5, forcing1'],
     ['2d','c == 1, forcing1'],
     ['2h','h >= 5, suiter, forcing_game'], # TODO one/two suiter
     ['2h','shape_type is balanced, hcp in 23..24, forcing_game'],
     ['2s','s >= 5, suiter, forcing_game'], # TODO one/two suiter
     ['2n','shape_type is balanced, hcp in 21..22, major < 4, minor < 5'],
     ['3c','c >= 5, d >= 5 , hcp in 17..20'], # TODO minimum hand
     ['3d','c >= 5, d >= 5, hcp > 20'], # TODO maximum hand
     ['3h','h tricks 9'], # nine tricks playing in the suit, one-suiter
     ['3s','s tricks 9'], # nine tricks playing in the suit, one-suiter
    ],
    ['opening1 is 1c, respons1 is 1h', []],
    ['opening1 is 1c, respons1 is 1s', []],
    ['opening1 is 1c, respons1 is 1n', []],
    ['opening1 is 1c, respons1 is 2major', []],
    ['opening1 is 1c, respons1 is 2n', []],
    ['opening1 is 1c, respons1 is 3n', []],
    ['opening1 is 1d, respons1 is 1h', []],
    ['opening1 is 1d, respons1 is 1s', []],
    ['opening1 is 1d, respons1 is 1n', []],
    ['opening1 is 1d, respons1 is 2major', []],
    ['opening1 is 1d, respons1 is 2n', []],
    ['opening1 is 1d, respons1 is 3n', []],
    ['opening1 is 1h, respons1 is 1s', []],
    ['opening1 is 1h, respons1 is 1n', []],
    ['opening1 is 1h, respons1 is 2c', []],
    ['opening1 is 1h, respons1 is 2d', []],
    ['opening1 is 1h, respons1 is 2h', []],
    ['opening1 is 1h, respons1 is 2s', []],
    ['opening1 is 1s, respons1 is 1n', []],
    ['opening1 is 1s, respons1 is 2c', []],
    ['opening1 is 1s, respons1 is 2d', []],
    ['opening1 is 1s, respons1 is 2h', []],
    ['opening1 is 1s, respons1 is 2s', []],
    ['opening1 is 1s, respons1 is 2n', []],
    ['opening1 is 1n, respons1 is 2c', []],
    ['opening1 is 1n, respons1 is 2d', []],
    ['opening1 is 1n, respons1 is 2h', []],
    ['opening1 is 1n, respons1 is 2s', []],
    ['opening1 is 1n, respons1 is 2n', []],
    ['opening1 is 2c, respons1 is 2n', []],
    ['opening1 is 2d, respons1 is 2h', []],
    ['opening1 is 2d, respons1 is 2s', []],
    ['opening1 is 2d, respons1 is 2n', []],
    ['opening1 is 2d, respons1 is 3c', []],
    ]

btc2k_after = [

]
"""
1h-1s-1n-2c-2d=not 3 spades
1h-1s-1n-2c-2d-2h=GI with a 3 heart raise
1h-1s-1n-2c-2d-2s=GI with a 5 great spades
1h-1s-1n-2c-2d-2s=GI with a 6 bad spades
1h-1s-1n-2c-2d-2n=GF not 3 hearts, not 5 spades
1h-1s-1n-2c-2d-3c=to play
1h-1s-1n-2c-2d-3d=SI, asking openers to cue-bid, strong single-suiter, non-solid suit
1h-1s-1n-2c-2d-3d=SI, asking openers to cue-bid, balanced
1h-1s-1n-2c-2d-3h=strong balanced, 3 hearts, GF
1h-1s-1n-2c-2d-3s=s == 6, GF
1h-1s-1n-2c-2d-3n=to play
1h-1s-1n-2c-2d-4c=cue-bid, h >= 4, top-honors < 2
1h-1s-1n-2c-2h=h == 5, s == 3
1h-1s-1n-2c-2h-2s=invitational
1h-1s-1n-2c-2h-2n=invitational
1h-1s-1n-2c-2h-3c=to play
1h-1s-1n-2c-2h-3d=SI, asking opener to cue-bid
1h-1s-1n-2c-2h-3h=h == 3, invitational
1h-1s-1n-2c-2h-3s=GF, s >= 5
1h-1s-1n-2c-2h-4c=cue-bid, h fit, top-honors < 2, c
1h-1s-1n-2c-2h-4d=cue-bid, h fit, top-honors < 2, d
1h-1s-1n-2c-2h-4h=cue-bid, h fit, top-honors < 2, h
1h-1s-1n-2c-2s=s == 3, h < 5, minimum
1h-1s-1n-2c-2s-2n=GF, inviting opener to bid another 4 card suit
1h-1s-1n-2c-2s-3s=to play
1h-1s-1n-2c-2s-3d=SI, asking opener to cue-bid
1h-1s-1n-2c-2s-3h=GF+, h
1h-1s-1n-2c-2s-3s=GF+, s
1h-1s-1n-2c-2n=s == 3, h < 5, maximum
1h-1s-1n-2c-3c=min, 1=4=4=4 minimum (if max, bid 2n earlier)

1h-1s-2c-2d=asking_relay
1h-1s-2d-2n=asking_relay
1h-1n-2c-2s=asking_relay for 3h
1h-1n-2d-2s=asking_relay for 3h
1h-1n-2c-2n=non_forcing_relay shows game interest without 3h, passable by minimum canape
1h-1n-2d-2n=non_forcing_relay shows game interest without 3h, passable by minimum canape
1s-1n-2c-2n=asking_relay
1s-1n-2d-2n=asking_relay
"""
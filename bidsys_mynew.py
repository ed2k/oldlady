"""
bid system 
name_state variables
TODO, get all blue team clubs conventions in code
ex: controls
"""

mynew_opening1= [
    ['1n','hcp in 16..18, shape_type is balanced'],
    ['1s','hcp in 13..21, s > h, s >= 5'],
    ['1h','hcp in 13..21, h >= 5,h >= s'],
    ['1d','hcp in 13..21, s < 5,h < 5,d >= 3, d > c'],
    ['1c','hcp in 13..21, s < 5,h < 5,c >= 3, c >= d'],
    ['2n','hcp in 22..24, shape_type is balanced'],
    ['3n','hcp in 25..27, shape_type is balanced'],
    ['2c','hcp >= 22'],
    ['2d','hcp in 6..10, d == 6'],
    ['2h','hcp in 6..10, h == 6'],
    ['2s','hcp in 6..10, s == 6'],
    ['3c','hcp < 13, c == 7'],
    ['3d','hcp < 13, d == 7'],
    ['3h','hcp < 13, h == 7'],
    ['3s','hcp < 13, s == 7'],               
    ['rule of two and three','hcp < 13, longest >= 7'],
    ['game in hand', 'hcp+shortage+length >= 26'],
    ]
mynew_opening2=[
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
mynew_respons1= [
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
     ['+1','hcp+shortage in 6..10, suit >= 5, len_major < 4'],
     ['+2','hcp+shortage in 11..12, suit >= 5, len_major < 4'],     
     ['1d','opening1 is 1c, hcp in 6..18, d >= 4'],
     ['1h','opening1 is 1c, hcp in 6..18, h >= 4'],
     ['1s','opening1 is 1c, hcp in 6..18, s >= 4'],
     ['1h','opening1 is 1d, hcp in 6..18, h >= 4'],
     ['1s','opening1 is 1d, hcp in 6..18, s >= 4'],
     ['1n','hcp in 6..10'],   
     ['2n','opening1_type is 1minor, hcp in 13..15, shape_type is balanced'],
     ['3n','opening1_type is 1minor, hcp in 16..18, shape_type is balanced'],          
     ['2d','opening1 is 1d, hcp in 6..10, d >= 4'],
     ['2c','opening1 is 1c, hcp in 6..10, c >= 5'],
     ['2d','opening1 is 1d, hcp >= 13, d >= 4'],
     ['2c','opening1 is 1c, hcp >= 13, c >= 5'],
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
mynew_respons1_1n = [
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
mynew_respons2 = [['new','hcp > 20']]
mynew_openerNextBid = [
    ['opening1_type is 1major, respons1_type is 2major',
     ['+1','respons1_type is +1, hcp+shortage in 16..18'],
     ['+2','respons1_type is +1, hcp+shortage in 19..21']],
    ['opening1_type is 1major, respons1_type is 3s',
     ['+1','respons1_type is +2, hcp+shortage in 13..15'],
     ['+2','respons1_type is +2, hcp+shortage in 16..18'],
     ['+3','respons1_type is +2, hcp+shortage in 19..21']],
    ['opening1_type is 1major, respons1 is 1n',
     ['new','hcp in 13..15, shape is unbalanced'],
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
     ['new','hcp in 13..15, shape is unbalanced'],
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
    ]

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
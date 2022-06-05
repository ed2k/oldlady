from operator import le
import re

from numpy import spacing


def format_bid(levels, bid, line):
    if len(levels) > 0:
        print('e', levels)
    leading_space = 0
    if line[0] not in '1234567':
        while leading_space < len(line):
            if line[leading_space] not in '- \t':
                break
            leading_space += 1
        if leading_space == 0 or line[leading_space] not in 'P1234567':
            return [], '', line
        f = line[leading_space:].split()
        remainder = ' '.join(f[1:])
        if remainder and remainder[0] != '=':
            remainder = '=' + remainder
        print('f', levels)
        if len(levels) == 0 or leading_space > levels[-1]:
            levels.append(leading_space)
            bid = f'{bid} {f[0]}'
        elif leading_space < levels[-1]:
            print(leading_space, line)
            back_steps = 0
            while levels[-1] != leading_space:
                levels.pop()
                back_steps -= 1
            bid_prev = bid.split(' ')[:back_steps]
            b = ' '.join(bid_prev)
            bid = f'{b} {f[0]}'
        else:
            bid_prev = bid.split(' ')[:-1]
            b = ' '.join(bid_prev)
            bid = f'{b} {f[0]}'

        print('r', levels, [bid], line)
        return levels, bid, '-'.join(bid) + remainder
        
    if not re.compile('^[- ]*[1-7][CDHSN]').match(line):
        return [], '', line

    # find the start of non bid
    i = 0
    while i < len(line) - 1:
        c = line[i]
        if c not in 'X1234567CDHSNT- ;/':
            break        
        if c in '1234567':
            suit = line[i+1]
            if suit not in 'CDHSN':
                break
            elif suit in 'N' and line[i+2] != 'T':
                break
            elif suit in 'N':
                i += 1
            i += 1
        elif c in '/':
            if line[i+1] not in 'CDHS':
                break
            i += 1
        elif c in 'X':
            pass
        elif c not in '- ;':
            break
        i += 1
    remainder = ''
    if i < len(line) and i > 4:
        remainder = line[i:]
        if remainder[0] != '=':
            remainder = '=' + remainder
        line = line[:i]
    if i > 4:
        line = line.replace(';', ' ').replace('-', ' ')
        if leading_space == 0:
            levels = []
        print(leading_space, levels, line, ':', remainder)
        return (levels, line, '-'.join(line.split()) + remainder)
    return ([], '', line)


lines = []
paragraph = []
bid = ''
levels = []
with open('BTC2000_gmeier.txt', 'r') as f:
    for line in f:
        line = line.rstrip()
        test = line.replace(' ', '').replace('-', '')
        test = test.replace('\t', '')
        if len(test) == 0:
            line = ''
        if len(line) > 0:
            if len(paragraph) > 0:
                for i in paragraph:
                    lines.append(i)
            levels, bid, line = format_bid(levels, bid, line)
            paragraph = [line]            
        elif paragraph[0][0] != '-':
            paragraph.append(line)

if len(paragraph) > 0:
    for i in paragraph:
        lines.append(i)

with open('BTC2000_gmeier2.txt', 'w') as f:
    for line in lines:
        f.write(line)
        f.write('\n')


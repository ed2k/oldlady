import re


def format_bid(bid, line):
    leading_space = 0
    if line[0] not in '1234567':
        while leading_space < len(line):
            if line[leading_space] not in '- \t':
                break
            leading_space += 1
        if leading_space == 0 or line[leading_space] not in '1234567':
            return '', line
        #line = line[leading_space:]
        print(leading_space, line[leading_space:])
        return '', line
        
    if not re.compile('^[- ]*[1-7][CDHSN]').match(line):
        return '', line

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
        line = line.replace(';',' ').replace('-',' ')
        print(leading_space, line, remainder)
        return (line, '-'.join(line.split()) + remainder)
    return ('', line)


lines = []
paragraph = []
bid = ''
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
            bid, line = format_bid(bid, line)
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



def format_bid(line):
    if line[0] not in '1234567':
        return line

    for c in line:
        if c not in '1234567CDHSNT- ;':
            return line
    
    line = line.replace(';',' ').replace('-',' ')
    return '-'.join(line.split())


lines = []
paragraph = []
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
            line = format_bid(line)
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


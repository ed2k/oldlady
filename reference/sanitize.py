lines = []
with open('BTC2000_gmeier.txt', 'r') as f:
    for line in f:
        line = line.rstrip()
        test = line.replace(' ', '').replace('-', '')
        test = test.replace('\t', '')
        if len(test) == 0:
            line = ''
        lines.append(line)


with open('BTC2000_gmeier2.txt', 'w') as f:
    for line in lines:
        f.write(line)
        f.write('\n')


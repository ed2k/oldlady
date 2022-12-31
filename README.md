# oldlady
# setup webcgi
```
assume oldlady at Downloads/oldlady
cp cgiserve.py ..
at Downloads> python cgiserve.py

visit localhost:8000/cn.bridge/bridge.html
```

# test dds, seems only argv 4,5,6,7 are used
```
FIXME first one failed,
ddsprogs/dds 0 3 1 0 2 KJ7.982.AKT.J532:QT63.J654.92.T7:A942.AQT7..AK96:85.K3.Q76543.Q84 2.2:8.11
ddsprogs/dds 0 3 1 0 1 73.QJT.AQ54.T752:QT6.876.KJ9.AQ8:5.A95432.7632.K6:AKJ9842.K.T8.J93 3:4
'S', "N:QJ6.K652.J85.T98 873.J97.AT764.Q4 K5.T83.KQ9.A7652 AT942.AQ4.32.KJ3", 'xxxxxx'
ddsprogs/dds a a a 3 0 QJ6.K652.J85.T98:873.J97.AT764.Q4:K5.T83.KQ9.A7652:AT942.AQ4.32.KJ3
ddsprogs/ddspy3 a a a 3 0 QJ6.K652.J85.T98:873.J97.AT764.Q4:K5.T83.KQ9.A7652:AT942.AQ4.32.KJ3
./redealdds QJ6.K652.J85.T98:873.J97.AT764.Q4:K5.T83.KQ9.A7652:AT942.AQ4.32.KJ3
result: lead strain suit rank opponent (4 leads x 5 strains = 20 rows)
result: N S D 5 -1
./redealdds 'N:QJ6.K652.J85.T98 873.J97.AT764.Q4 5.T83.KQ93.76532 AKT942.AQ4.2.AKJ'
{'N': [5, 'C', 'S3'], 'E': [11, 'S', 'H3'], 'S': [5, 'C', 'SA'], 'W': [12, 'S', 'D5']}
```

# test bidding, play
```
oldlays/deal319> python3 ../demo_bidding.py
oldlays/deal319> python3 ../demo_bidding_play.py
```
# floater
```
assume deal319, ddsprog and oldlady directories are the same level
oldlady> python3 floader_server.py
deal319> python3 ../oldlady/floater-multi-clients.py
deal319> python ../oldlady/floater_client.py
```

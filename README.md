# oldlady
# setup webcgi
assume oldlady at Downloads/oldlady
cp cgiserve.py ..
at Downloads> python cgiserve.py

visit localhost:8000/cn.bridge/bridge.html


# test dds, seems only argv 4,5,6,7 are used
FIXME first one failed,
ddsprogs/dds 0 3 1 0 2 KJ7.982.AKT.J532:QT63.J654.92.T7:A942.AQT7..AK96:85.K3.Q76543.Q84 2.2:8.11
ddsprogs/dds 0 3 1 0 1 73.QJT.AQ54.T752:QT6.876.KJ9.AQ8:5.A95432.7632.K6:AKJ9842.K.T8.J93 3:4
'S', "N:QJ6.K652.J85.T98 873.J97.AT764.Q4 K5.T83.KQ9.A7652 AT942.AQ4.32.KJ3", 'xxxxxx'
ddsprogs/dds a a a 3 0 QJ6.K652.J85.T98:873.J97.AT764.Q4:K5.T83.KQ9.A7652:AT942.AQ4.32.KJ3
ddsprogs/ddspy3 a a a 3 0 QJ6.K652.J85.T98:873.J97.AT764.Q4:K5.T83.KQ9.A7652:AT942.AQ4.32.KJ3
./redealdds QJ6.K652.J85.T98:873.J97.AT764.Q4:K5.T83.KQ9.A7652:AT942.AQ4.32.KJ3

oldlays/deal319> python3 ../demo_bidding_play.py

# floater
assume deal319, ddsprog and oldlady directories are the same level
oldlady> python3 floader_server.py
deal319> python3 ../oldlady/floater-multi-clients.py
deal319 python ../oldlady/floater_client.py


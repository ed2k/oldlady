import sys, random,time
import defs


import sbridge, sAi
from sbridge import *

   
   
def card_cmp(trump, c1, c2):
   if trump == 'n':
      if c1/13 != c1/13: return 1
      if (c1 % 13) > (c2 % 13): return 1
      return -1
   if c1/13 == c2/13:
      if (c1 % 13) > (c2 % 13): return 1
      return -1
   if 'cdhs'[c1/13] == trump: return 1
   if 'cdhs'[c2/13] == trump: return -1
   return 1
 
def card52_kn(idx):
   ''' convert 0-51 indexing of card to 2 char kind number representation
   such as c2, cj, '''
   i = idx
   return 'cdhs'[ i/13]+'23456789tjqka'[ i % 13]
def cardkn_52(card):
   return KIDX[card[0].lower()] * 13 + PBN_HIDX[card[1].lower()]
def convert_str2play(line):
   '''a string of c7h3sa to a list of number'''
   played = []
   for i in xrange(len(line)/2):
      idx = i*2
      played.append(cardkn_52(line[idx:idx+2]))
   return played
def convert_play2str(play):
   if play is None: return ''
   return ''.join([card52_kn(x) for x in play])

def pbn2f_hand(pbn):
   '''AKQ.J.T.98765432 to a list of number 0-51'''
   rtn = []
   s = 3
   for suit in pbn.split('.'):
      idx = s*13
      for card in suit:
         x = idx + PBN_HIDX[card.lower()]
         rtn.append(x)
      s = s -1
   return rtn
      
class BidStatus:
   data = None
   def __init__(self, str): self.data = str
   def __str__(self): return self.data
   def __len__(self): return len(self.data)/2
   def __getitem__(self, idx):
      if idx >=0:
         i = idx *2
      else:
         i = len(self.data) + idx*2
      return self.data[i:i+2]
         
   def __getslice__(self,i,j):
      r = []
      for idx in range(self.__len__())[i:j]:
         r.append(self.__getitem__(idx))
      return r
   
class State:   
   clients_conn = [] # list of clients sockets
   current_sock = None # current client we are handling message from
   deal = None # for table manager to monitor progress
   rubber = None
   ai = None
   
   hand_id = 0 # start from 1 to work with floater
   client_holding = []
   bid_status = BidStatus('')
   play_status = []
   #NESW -> 0123
   table_seated = ['']*4
   seat_sock = ['']*4
   def __init__(self):
      intid = random.randint(1,9999)
      self.clientname = 'name_'+str(intid)+'_'
      self.hostname = '127.0.0.1!localhost'
      self.portstr = str(10101+intid)
      self.message_seq = 1
      self.rubber = sbridge.Rubber(sbridge.NORTH)
   def send_new_hand(self):
      ''' play only get its own hand and plus dummy hand if first one is played
      hname has to be something 6Jan08IMP1, last "1" after IMP is handid
      '''
      i = str(self.hand_id)
      p = convert_play2str(self.play_status)
      b = str(self.bid_status)
      msg = []
      for seat in xrange(4):
         h = str(seat)+' '+o2pbn_hand(self.deal.hands[f2o(seat)])
         if  len(self.play_status) >= 1:
            h2 = str(o2f(self.deal.dummy))+' '+o2pbn_hand(self.deal.hands[self.deal.dummy])
            h += '|'+ h2
         msg.append([seat, self.encode_message('new_hand',[i,'6Jan08IMP'+i,h,b,p])])
      return msg
         
   def client_seated(self,seat,name):
      if name in self.table_seated:         
      #avoid one client sit on multiple seats
         if seat == self.table_seated.index(name): return True
         return False
      if self.table_seated[seat] != '':
         print seat,name,'seat taken by',self.table_seated[seat]
         return False
      print seat, name, 'seated',self.current_sock
      self.seat_sock[seat] = self.current_sock
      self.table_seated[seat] = name
      return True
   def remove_client(self,sock):      
      self.clients_conn.remove(sock)
      #also remove the client name on the seat if exist
      try:
         seat = self.seat_sock.index(sock)
         self.seat_sock[seat] = ''
         self.table_seated[seat] = ''
      except ValueError: pass
   def all_seated(self):
      for v in self.table_seated:
         if v == '': return False
      return True
   def own_seat(self): return self.where_is_my_seat()
   def get_deal(self, handid, suit, bids, plays):
      seat = self.where_is_my_seat()
      assert seat is not None
      self.hand_id = int(handid)

      self.bid_status = BidStatus(bids)
      self.play_status = convert_str2play(plays)
      self.deal = sbridge.Deal((self.hand_id-1) % 4)
      for x in xrange(4): self.deal.hands[x] = None
      if suit[1] == ' ':
         for s in suit.split('|'):
            self.deal.hands[int(s[0])] = f2o_hand(pbn2f_hand(s[2:]))
         self.client_holding = pbn2f_hand(suit.split('|')[0][2:])
         return
      # special case for floater server
      line = file(defs.FL_DATA).read()
      s = line.split()
      x = seat*13
      self.client_holding = [int(x) for x in s[x:x+13]]
      print self.hand_id, self.client_holding
      for i in xrange(4):
         idx = i * 13
         self.deal.hands[i] = f2o_hand([int(x) for x in s[idx:idx+13]])
   def first_lead(self):
      auc = self.bid_status
      handid = self.hand_id
      steps = len(auc)
      nums = steps + handid -1
      kind = auc[-4][1]
      odd = steps % 2

      # find out who is first one bid the same kind
      for i in xrange(steps/2):
         if auc[i*2+odd][1] == kind:
            r = (i*2+odd+handid -1) 
            return (r+1) % 4

   def handle_auction(self):
      ''' try use oldlady engine '''
      dealer = self.deal.dealer

      ai = sAi.ComputerPlayer(f2o(self.own_seat()))
      print 'dealer','NESW'[dealer],'my seat','NESW'[ai.seat]
         
      ai.new_deal(self.deal)
      print 'myhand',
      for c in ai.deal.hands[ai.seat]: print c,
      print
      for i in xrange(len(self.bid_status)):
         ai.bid_made(f2o_bid(self.bid_status[i]))
      
      if ai.deal.trick is None:
         bid = ai.bid()
         return o2f_bid(bid)
      deal = ai.deal
      if ai.seat == deal.dummy: return None
      # first lead is over, everybody else see the dummy's hand
      
      for c in self.play_status:
         #print 'play',deal.player,f2o_card(c)
         deal.play_card(f2o_card(c))
         if deal.trick.cards[deal.player] is not None:
            ai.trick_complete()

      if (ai.seat != deal.declarer) and (deal.player != ai.seat): return None
      if (ai.seat == deal.declarer) and (deal.player != deal.dummy) and (deal.player != deal.declarer):
         return None         
      print 'myseat','NESW'[ai.seat],'player','NESW'[deal.player], 'dummy','NESW'[deal.dummy],'declarer','NESW'[deal.declarer]      
      card = None
      if (deal.player == deal.dummy) and (deal.declarer == ai.seat):
         card = ai.play_dummy()
      if deal.player == ai.seat: card = ai.play_self()
      del ai
      return o2f_card(card)
   
   def where_is_my_seat(self):
      try:
         return self.table_seated.index(self.clientname)
      except ValueError:
         return None
      
   def encode_message(self,cmd, seqs):
      self.message_seq += 1
      fromid = encode_args([self.clientname,str(self.message_seq)])
      def packmsg(op,args=[]):         
         argc = f_op2argc[op]
         if args == []:
            args = ['']*argc
         return op+str(argc)+'\\'+fromid+encode_args(args)

      if cmd == 'J':
         version, capacity = seqs
         args = [version,self.clientname,self.hostname,self.portstr,capacity]
         return 'J5\\'+fromid+encode_args(args)
      elif cmd == 'request_seat':
         seat = seqs[0]
         seat = name_dict[seat]
         args = [self.clientname,seat,self.hostname,self.portstr]
         return 'S4\\'+fromid+encode_args(args)
      elif cmd == 'seated':
         return packmsg('s',seqs)
      elif cmd == 'C':
         return 'C1\\'+fromid+encode_args([self.clientname])
      elif cmd == 'seen':
         seat = name_dict[seqs[0]]
         tmp = seqs[1]
         return 'e3\\'+fromid+encode_args([seat,tmp,''])
      elif cmd == 'auction_status':
         return 'a2\\'+fromid+encode_args(seqs)
      elif cmd == 'play':
         return 'p2\\'+fromid+encode_args(seqs)
      elif cmd == 'accepted_join':
         return 'Y3\\'+fromid+encode_args(['K']+seqs)
      elif cmd == 'new_hand':
         return '*8\\'+fromid+encode_args(seqs+['','0',''])
      elif cmd == 'announce_table':
         return packmsg('T')
      return ''

  
def handle_auction(state):
   auc = state.bid_status
   #if auc is None: return None
   if auc.data == ' p'*4: return None
   if len(auc) > 3 and auc[-3:] == [' p']*3:
      a = state.handle_auction()
      # not my turn yet
      if a is None: return None
      state.play_status += [a]
      a = convert_play2str(state.play_status)
      return state.encode_message('play',[str(state.hand_id), a])

   r = (len(auc) + state.hand_id -1) % 4
   seat = state.where_is_my_seat()
   if r != seat: return None
   state.bid_status.data += state.handle_auction()
   return state.encode_message('auction_status',[str(state.hand_id),str(state.bid_status)])
   


def sit_at_availabe_seat(table):
   ava = []
   for s in xrange(4):
      if table[s] == '' : ava.append(s)
   if len(ava) == 0: return None
   seat = ava[random.randint(0,len(ava)-1)]
   return seat 

def encode_args(seqs):
   len_seqs = [str(len(x)) for x in seqs]
   return '\\'.join(len_seqs) + '\\'+''.join(seqs)

def handleData(state, data):
   rmsg = []
   for line in data.split('\r\n')[:-1]:
      if line[:9] == "Floater '":
         rmsg.append("Floater 'shake")
         rmsg.append(state.encode_message('J',['8z','K']))
         continue
      elif line[:7] == '*alive*' or line[:6] == 'alive*':
         # could be the trigger to do self inspection
         rmsg.append('*alive*')
         continue      
      message = decode_message(line)
      if message[0] != 'T': print state.clientname,message
      if message[0] == 's':
         #todo, handle unseat info
         name,seat = message[3:5]
         state.table_seated[IDX[seat[0]]] = name
         #if name == clientname:
         # ai seated, let's begin
      elif message[0] == 'Y':
         rmsg.append(state.encode_message('C',[]))
      elif message[0] == 'C': pass
      elif message[0] == 'T':         
         if state.where_is_my_seat() is None:
            print 'T',state.table_seated
            seat = sit_at_availabe_seat(state.table_seated)
            rmsg.append(state.encode_message('request_seat',[seat]))
         if state.client_holding != []: rmsg.append(handle_auction(state))
         #todo some self inspection
      elif message[0] == 'd':
         seat = state.where_is_my_seat()
         if seat is None:
            pass
         else:
            rmsg.append(state.encode_message('seen',[seat,'0']))
            rmsg.append(state.encode_message('seen',[seat,'1']))
      elif message[0] == '*':
         state.get_deal(message[3],message[5],message[6],message[7])
      elif message[0] == 'a':
         # assume hand_id is the same
         m = message[4].replace('+',' ')
         state.bid_status = BidStatus(m)
         #rmsg.append(handle_auction(state))
      elif message[0] == 'p':
         state.play_status = convert_str2play(message[4])
         #rmsg.append(handle_auction(state))
   return rmsg

def decode_message(line):
    message_name = line[0]
    f = line.split('\\')
    num_of_args = int(f[0][1:])

    len_pfrom = int(f[1])
    len_pid = int(f[2])
    #avoid extra \\ inside message to be treated as seperator
    reline = '\\'.join(f[3:])

    pfrom = reline[:len_pfrom]
    tmp = reline[len_pfrom:]
    pid = tmp[:len_pid]

    if num_of_args == 0: return [message_name, pfrom, pid]
    tmp = tmp[len_pid:]
    f = tmp.split('\\')

    len_args = []
    for x in range(num_of_args):
        len_args.append( int(f[x]) )

    args = []
    tmp = '\\'.join(f[num_of_args:])
    for x in len_args:
        args.append(tmp[:x] )
        tmp = tmp[x:]
    return [message_name, pfrom, pid]+args       


def one_client(st=State()):
   import socket   
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.connect(('localhost', 10100)) # connect to server on the port

   while True:
      data = s.recv(10240)                 # receive up to 1K bytes
      if len(data) == 0: break
      #print 'r----------',[data]
      messages = handleData(st,data)
      if messages is None: continue
      for m in messages:
         if m is None: continue
         if m != '*alive*': print st.clientname,'s',m
         s.send(m+'\r\n')
      time.sleep(random.random())
   
if __name__ == "__main__":
   one_client()


from floater_client import *

def get_current_seated_msg(state):
   msg = []
   for seat in xrange(4):
      name = state.table_seated[seat]
      if name == '': continue
      m = state.encode_message('seated',[name,name_dict[seat],'ip','port'])
      msg.append(m)
   return msg   

def next_step(state):
   print state.table_seated,state.deal
   if state.all_seated() and state.deal is None:
      # deal new hand
      state.hand_id += 1
      state.deal = state.rubber.next_deal()
      return state.send_new_hand()
   return [state.encode_message('announce_table',[])]
   
def table_handle(state,data):
   rmsg = []
   for line in data.split('\r\n')[:-1]:
      if line[:9] == "Floater '":
         continue
      elif line[:7] == '*alive*' or line[:6] == 'alive*':
         # could be the trigger to do self inspection
         continue
      message = decode_message(line)
      mname,mfrom,mid = message[:3]
      args = message[3:]
      if mname == 'J':
         username = args[1]
         rmsg.append(state.encode_message('accepted_join',['IP','port']))
         rmsg += get_current_seated_msg(state)
      elif mname == 'S':
         username,seat,ip,port = args
         if state.client_seated(IDX[seat[0]], username):
            # new player seated
            rmsg += get_current_seated_msg(state)
            if state.deal is not None:# update game status.
               rmsg += state.send_new_hand()
      elif mname == 'C':
         rmsg.append(line)
      elif mname == 'a':
         print args
         state.bid_status = BidStatus(args[1])
         #TODO check if it is the right bidder
         state.deal.bid(f2o_bid(state.bid_status[-1]))
         rmsg.append(line)
         print [state.bid_status.data]
         if state.bid_status.data == ' p'*4:
            print 'all pass'
            state.deal = None
            state.bid_status = BidStatus('')
      elif mname == 'p':
         state.play_status = convert_str2play(args[1])
         rmsg.append(line)
         if len(state.play_status) == 1:
            rmsg += state.send_new_hand()
         if len(state.play_status) == 52:
            state.deal = None
            state.play_status = []
            state.bid_status = BidStatus('')
      return rmsg

def send_messages(state,mm):
   if mm is None: return
   #print mm
   for m in mm:
      if m is None: continue
      if len(m) == 2: # single client message
        conn = state.seat_sock[m[0]]
        if conn != '':
           print 'p2p',m[0],m[1]
           conn.send(m[1]+'\r\n')
      else:
         if m != '*alive*' and m[0] != 'T': print 's',m
         for conn in state.clients_conn: conn.send(m+'\r\n')

TODO = """  work on a server that take care of table manager and 3 player
 a client can use request/response mode to play bridge, instead of polling data.
 use cases, request/response from client/server
 1. seated at North/hand id, client cards, hand id
 2. hand id, bid/hand id bid history, ...
 3. hand id, pass/hand id bid history, leading play, dummy (assume client is not leader)
 4. hand id, play/hand id, play history
 5. hand id, play/hand id, play history, new hand, score ...
"""
if __name__ == "__main__":
   
   import socket, select  
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.bind(('0.0.0.0',10100))
   s.listen(5)
   timeout = 5
   st = State()
   st.clientname = "tableserver"
   while True:
      infd = [s]+ st.clients_conn
      fds = select.select(infd,[],[],timeout)
      if timeout and len(fds[0] + fds[1]) == 0:
         #print 'timeout'
         m = next_step(st)
         send_messages(st,m)
         continue
      for i in fds[0] + fds[1]:
         if i == s:
            conn, addr = s.accept()
            conn.send("Floater 'shake\r\n")
            st.clients_conn.append(conn)
         elif i in st.clients_conn:
            st.current_sock = i
            data = ''
            try: data = i.recv(10240)                 # receive up to 1K bytes
            except socket.error: pass
            if len(data) == 0: # receive nothing, close it
               i.close()
               st.remove_client(i)
               continue
            #print 'r',[data]
            messages = table_handle(st,data)
            send_messages(st, messages)

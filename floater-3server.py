from floater_client import *
from sAi import *
from sbridge import *

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urllib

MANAGERNAME = "tableserver"
st = State()
st.clientname = MANAGERNAME
ais = [ComputerPlayer(seat) for seat in PLAYERS]
# working as a live table, don't use st.deal as it is used to save original cards


def nextStep(action, state, comps):
    rmsg = []
    if action == 'confirm_deal':
        state.hand_id += 1
        state.bid_status = BidStatus('')
        state.play_status = []
        state.deal = state.rubber.next_deal()
        for ai in ais: ai.new_deal(state.deal)
        for ai in ais: print_hand(ai.deal.hands[ai.seat])
        rmsg.append(state.send_new_hand()[NORTH])
        if state.deal.dealer != NORTH: 
            bid = ais[state.deal.player].bid()
            state.bid_status.data += o2f_bid(bid)
            rmsg.append(state.encode_message('auction_status',[str(state.hand_id),str(state.bid_status)]))
    return rmsg

def httpResponse(msg):
    return "Content-type: text\n\n"+msg    
class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        start = len('/postit.yaws?flproxyB=')
        data = urllib.unquote(self.path[start:])
        print 'r',[data]
        rsp = []
        while data != '\r\n':
            messages = table_handle(st,data)
            selfdata = []
            print 'messages',messages
            if messages is None:
                print 'message should not be none'
                break; # why??? fixme
            for m in messages:
                if m is None: continue
                if len(m) == 2: # single client message
                    print 'p2p',m[0],m[1]
                    rsp.append(m[1])
                    selfdata.append(m[1])
                else:
                    print 's>',m
                    rsp.append(m)
                    selfdata.append(m)
            data = '\r\n'.join(selfdata)+'\r\n'
        self.wfile.write(httpResponse('\r\n'.join(rsp)+'\r\n'))

def table_handle(state,data):
   rmsg = []
   for line in data.split('\r\n')[:-1]:
      message = decode_message(line)
      mname,mfrom,mid = message[:3]
      args = message[3:]
      if mname == 'S':
         username,seat,ip,port = args
         if state.deal is None: return nextStep('confirm_deal', state, ais)
         # assume client always north or south if north is dummy 
         if ais[NORTH].deal.dummy == NORTH: rmsg.append( state.send_new_hand()[SOUTH])
         else:rmsg.append( state.send_new_hand()[NORTH])
      elif mname == 'a':
         print 'bids',args
         # reused as table manager deal recorder
         tbdeal = ais[NORTH].deal
         if mfrom != MANAGERNAME and tbdeal.trick is not None: return rmsg
         if mfrom != MANAGERNAME and tbdeal.player != NORTH: return rmsg
         #TODO check if it is the right bidder, and follow rule
         state.bid_status = BidStatus(args[1].replace('+',' '))
         bid = f2o_bid(state.bid_status[-1])
         for ai in ais: ai.bid_made(bid)
         state.deal.bid(bid)
         
         print [state.bid_status.data]

         if tbdeal.contract is not None and tbdeal.contract.is_pass():
             rmsg += nextStep('confirm_deal', state, ais)
         elif tbdeal.trick is None:
             if tbdeal.player == NORTH: continue
             bid = ais[tbdeal.player].bid ()
             state.bid_status.data += o2f_bid(bid)
             rmsg.append(state.encode_message('auction_status',[str(state.hand_id),str(state.bid_status)]))
         else: # only lead play is possible here
             # if NORTH is dummy, user takes control of SOUTH 
             if tbdeal.player == NORTH : continue

             card = ais[tbdeal.player].play_self ()
             a = o2f_card(card)
             print tbdeal.player,'lead play',card
             for ai in ais: print ai.seat,ai.deal.player,
             state.play_status += [a]
             rmsg.append(state.encode_message('play',[str(state.hand_id), convert_play2str(state.play_status)]))
      elif mname == 'p':
          tbdeal = ais[NORTH].deal
          dummy = tbdeal.dummy
          if tbdeal.trick is None: continue
          if mfrom != MANAGERNAME:
              if dummy == SOUTH:
                  if tbdeal.player == WEST or tbdeal.player == EAST: continue
              elif dummy == NORTH:
                  if tbdeal.player != NORTH and tbdeal.player != SOUTH: continue
              elif tbdeal.player != NORTH: continue
              print dummy, 'is dummy, NORTH turn',tbdeal.player
          # todo, consider NORTH is dummy to exchange with SOUTH
          state.play_status = convert_str2play(args[1])

          if len(state.play_status) == 1:
              if dummy == NORTH: rmsg.append( state.send_new_hand()[SOUTH])
              else:rmsg.append( state.send_new_hand()[NORTH])
              for ai in ais:
                  ai.deal.hands[dummy] = state.deal.hands[dummy][:]
          elif len(state.play_status) == 52:
              return nextStep('confirm_deal', state, ais)

          card = f2o_card(state.play_status[-1])
          player = tbdeal.player
          for ai in ais: ai.deal.play_card(card)
          if tbdeal.trickCompleted():
              for ai in ais:
                  ai.trick_complete()                      
          print 'whose turn',tbdeal.player
          # palyer take SOUTH also if dummy is NORTH
          if dummy == NORTH and tbdeal.player == SOUTH: continue
          if tbdeal.player == NORTH: continue

          if tbdeal.player != dummy:
              card = ais[tbdeal.player].play_self ()
          else:
              card = ais[tbdeal.declarer].play_dummy()
          a = o2f_card(card)
          print 'playing',card
          state.play_status += [a]
          rmsg.append(state.encode_message('play',[str(state.hand_id), convert_play2str(state.play_status)]))
          
   return rmsg


        
TODO = """ a web server that take care of table manager and 3 player
 a client can use request/response mode to play bridge, instead of polling data.
 use cases, request/response from client/server
 1. seated at North/hand id, client cards, hand id
 2. hand id, bid/hand id bid history, ...
 3. hand id, pass/hand id bid history, leading play, dummy (assume client is not leader)
 4. hand id, play/hand id, play history
 5. hand id, play/hand id, play history, new hand, score ...

 plus, possible a cgi interface, that process each request then return result, save its
 status then quit
 now, only takes http get, return data not follow http standard
 TODO: fix response so that erlang http:request can parst it
"""
if __name__ == "__main__":
   
   import socket, select
   try:
        server = HTTPServer(('', 10101), MyHandler)
        print 'started httpserver...'
        server.serve_forever()
   except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()



from floater_client import *
import random
__doc__ = '''
work with website as message buffer, each client send message to website
then table manager pickup the message in the same way
'''
if __name__ == "__main__":
   website = '142.133.118.94:4080'
   if len(sys.argv) > 1: website = sys.argv[1]
   import urllib,time
   url = 'http://'+website+'/postit.yaws?flproxyB='
   st = State()
   st.clientname = 'mfrom'
   while True:
      # check message
      data = urllib.urlopen(url).read()
      if data.find("Internal error") >= 0:
         print [data]
         time.sleep(1)
         continue
      data = data[:-4]
      if data != 'nothing': print 'r',[data]
      messages = handleData(st,data)
      if messages is None: continue
      for m in messages:
         if m is None: continue
         if m != '*alive*': print 's',m
         # send message
         urllib.urlopen(url+urllib.quote(m+'\r\n')).read()
         time.sleep(1+random.random())
      time.sleep(1+random.random())

# python 3
import urllib.request
from lib_socks_proxy_2013_10_03 import monkey_patch as socks_proxy_monkey_patch
from lib_socks_proxy_2013_10_03 import socks_proxy_context
# python 2.7
#import urllib2
import json
import time
import datetime

starttime = datetime.datetime.now()

apikey = open('D2_API_KEY', 'r').read().strip()

stopseqnum = 2115522031 # stop at this index

socks_proxy_monkey_patch.monkey_patch()
opener = urllib.request.build_opener()

def accessMatchHistory(lastseqnum):
    succeed = False
    while not succeed:
        try:
            with socks_proxy_context.socks_proxy_context(proxy_address=('127.0.0.1', 1080)):
                res = opener.open("https://api.steampowered.com/IDOTA2Match_570/GetMatchHistoryBySequenceNum/V001/?key=" + apikey + "&start_at_match_seq_num=" + str(lastseqnum))
                matchHist = json.loads(res.read().decode('utf-8'))
                succeed = True
            # matchHist = json.loads(urllib.request.urlopen("https://api.steampowered.com/IDOTA2Match_570/GetMatchHistoryBySequenceNum/V001/?key=" + apikey + "&start_at_match_seq_num=" + str(lastseqnum)).read().decode("utf-8"))
            # succeed = True
        except urllib.error.HTTPError:
            print("WOAH")
            time.sleep(30)
        except:
            print("Some other error has occured")
            time.sleep(30)
    return matchHist

def fetch():
    recordfile = open('record.dat', 'r')
    lastseqnum = recordfile.read().strip()
    recordfile.close()
    matches = open('./collection/data.csv', 'a')
    data = accessMatchHistory(lastseqnum)
    for i in range(100):
        curmatch = data['result']['matches'][i]
        match_id = curmatch['match_id']
        lastseqnum = curmatch['match_seq_num']
        print(str(i + 1) + "/100 " + str(match_id))
        if 'picks_bans' in curmatch:
            print(str(match_id) + " captain's mode")
            matches.write(str(match_id) + ",")
            matches.write(str(curmatch['radiant_win']) + ",")
            matches.write(str(curmatch['duration']))
            picklist = curmatch['picks_bans']
            for i in range(len(picklist)):
                matches.write("," + str(picklist[i]['is_pick']) + "," + str(picklist[i]['team']) + "," + str(picklist[i]['hero_id']))
            matches.write("\n")
    matches.close()
    # if any error occured before this point it must have occured at "lastseqnum"

    recordfile = open('record.dat', 'w')
    # thus we can safely start at the next one up...
    recordfile.write(str(lastseqnum + 1))
    recordfile.close()
    print("CYCLE FINISHED: " + str(stopseqnum - lastseqnum))
    if lastseqnum >= stopseqnum:
        return False
    else:
        return True

processFlag = True
while processFlag:
    processFlag = fetch()
    time.sleep(1)

endtime = datetime.datetime.now()

print("Started at " + starttime.isoformat() + "\nEnded at: " + endtime.isoformat())

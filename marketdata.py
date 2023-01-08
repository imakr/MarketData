"""
    Created on Sunday Jan 9 2023

    @author: Arunkumar

"""
from SmartApi.smartConnect import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import threading
import time
import win32pipe, win32file, pywintypes
import pyotp
import sys
import json

global handle
global obj
global authtoken
global feedToken
global refreshToken

username = sys.argv[1]
password = sys.argv[2]
apikey = sys.argv[3]
tkey = sys.argv[4]

def sendresponse(msgtype,reply):
    x = '{ "msgtype":"undefined", "reply":"undefined"}'
    y = json.loads(x)
    y["msgtype"]=msgtype;
    y["reply"] = reply
    x = json.dumps(y)
    print(x,flush=True)
    
def connect_angelone():
    # create object of call
    global obj
    global authtoken
    global feedToken
    global refreshToken
    obj = SmartConnect(api_key=apikey)
    totp = pyotp.TOTP(tkey)
    totp = totp.now()
    #print("New TOTP : ", totp)
    attempts = 5
    while attempts > 0:
        attempts = attempts - 1
        data = obj.generateSession(username, password, totp)
        #print(data)
        if data['status']:
            break
        time.sleep(2)
    feedToken = obj.getfeedToken()
    refreshToken = data['data']['refreshToken']
    authtoken = data['data']['jwtToken']
    sendresponse("login",data)
    #print("refreshToken : ", refreshToken,flush=True)
    #print("authtoken : ", authtoken,flush=True)
    #print("feedToken : ", feedToken,flush=True)
    
def terminate_session():
    global obj    
    data = obj.terminateSession(username)
    #print("terminate session : '{}'".format(data),flush=True)
    sendresponse("logout",data);
     
def get_feed(tokenid):
    global obj
    global authtoken
    global feedToken
    global refreshToken
    global sws
    #print("********** Trying new SOCKET**********",flush=True)
    correlation_id = "arun_123_qwerty"
    action = 1
    mode = 1

    API_KEY = apikey
    CLIENT_CODE = username
    AUTH_TOKEN = authtoken
    FEED_TOKEN = feedToken
    
    #if(tokenid == 1):
     #   tokenlist = [{"exchangeType": 5, "tokens": ["247476"]}]
    #elif (tokenid == 2):
     #   tokenlist = [{"exchangeType": 5, "tokens": ["247477","247476"]}]
    #print(" current thread id: " + str(threading.get_ident()))

    newtoken = json.loads(tokenid)
    tokenlist = list(newtoken)
    
    #tokenstring = json.dumps(newtoken) + ";";
    #tokenlist = []
    #tokenlist = list(tokenid)
    #tokenlist = tokenlist[:-1]

    #tokenlist = [{"exchangeType": 5, "tokens": ["247477","247476"]}]
     
    #print(type(tokenlist))
    #print(tokenlist)
    #print(len(tokenlist))
    sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)

    def on_data(wsapp, message):
        #print("Ticks : {}".format(message))
        writepipe(str(message))


    def on_open(wsapp):
        openpipe()
        writepipe("PIPE:OPENED")
        
        sws.subscribe(correlation_id, mode, tokenlist)


    def on_error(wsapp, error):
        writepipe(str(error))


    def on_close(wsapp):
        writepipe("PIPE:CLOSED")
        sws.close_connection()
        closepipe()

    # Assign the callbacks.
    sws.on_open = on_open
    sws.on_data = on_data
    sws.on_error = on_error
    sws.on_close = on_close

    sws.connect()
    #print("********** Exiting get feed**********",flush=True)


def stop_feed():
    global sws
    #print("********** Try Closing the SOCKET**********",flush=True)
    sws.on_close(None)
    #print("********** Close-Completed-for-the-SOCKET**********",flush=True)

def openpipe():
    global handle
    # Open the named pipe
    handle = win32file.CreateFile(r'\\.\pipe\ABC',win32file.GENERIC_READ | win32file.GENERIC_WRITE, 
                0, None, win32file.OPEN_EXISTING, win32file.FILE_ATTRIBUTE_NORMAL, None)
    # Set the read or blocking mode of the named pipe
    #res = win32pipe.SetNamedPipeHandleState(handle, win32pipe.PIPE_READMODE_MESSAGE, None, None)
    #if res == 0:
        #print(f"SetNamedPipeHandleState Return Code: {res}")   # if function fails, the return value will be zero
    

def writepipe(message):
    global handle
    some_data = str.encode(message, encoding="ascii")
    err,bytes_written = win32file.WriteFile(handle,some_data)
    #print(f"WriteFile Return Code: {err}, Number of Bytes Written: {bytes_written}")

def closepipe():
    global handle
    handle.Close()
    
if __name__ == '__main__':
    #print("Executing marketwatch",flush=True)
    sendresponse("status","starting")
    sendresponse("status","opensession")
    connect_angelone()
    option = -1
    while option != 0:
        #print("Please enter an option : ",flush=True)
        sendresponse("status","ready")
        input_str = input()
        #print(input_str,flush=True);
        input_args = input_str.split(";");
        #print(input_args,flush=True);
        option = int(input_args[0])
        #print("You entered : ", option,flush=True)
        if option == 1:
            sendresponse("status","executing-subscribe")
            token_input = input_args[1]
            #print(token_input,flush=True);
            token_param = str(token_input)
            #print(token_param,flush=True);
            token1 = str(token_param)
            mythread = threading.Thread(target=get_feed,args=[token1])
            mythread.start()
            #get_feed(token1)
        elif option == 2:
            sendresponse("status","executing-unsubscribe")
            stop_feed()
            mythread.do_run = False            
        elif option == 3:
            sendresponse("status","executing-resubscribe")
            stop_feed()
            mythread.do_run = False
            mythread.join()
            token_input = input_args[1]
            #print(token_input,flush=True);
            token_param = str(token_input)
            #print(token_param,flush=True);
            token2 = str(token_param)
            mythread = threading.Thread(target=get_feed,args=[token2])
            mythread.start()
        elif option == 4:
            sendresponse("status","executing-stopfeed")            
            stop_feed()
            mythread.do_run = False
            option = 0
    sendresponse("status","closesession")
    terminate_session()
    #print("Exiting While Loop , option =",option)
    sendresponse("status","exiting")

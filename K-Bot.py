from ttapi import Bot
from pprint import pprint
from time import sleep
from collections import deque
import json
myUserID = '517aeb2baaa5cd0177339e81'
ownerID =  '513101bbaaa5cd316ba3a24e'
bot = Bot('rTQTtZTmpPzzeQWbooUNspgw', myUserID, '516802feaaa5cd0a793a1353')


# Todo: Implement a DJ queue
# COmmand for the bot to reload the help files
# Commannd to make the bot leave & re-enter the room
# Make it more python-y: remove all of the 'if len(<list>) == 0:' and replace with 'if <list>:'


# Define callbacks
def roomChanged(data): 
    global theUsersList
    global theBopList
    global curSongID
    global curDjID
    global theOpList
    roomInfo = data['room']
    roomMeta = roomInfo['metadata']
    curDjID = roomMeta['current_dj']
    songLog = roomMeta['songlog']
    curSongID = songLog[0]['_id']
    roomMods = roomMeta['moderator_id']
    roomDJs = roomMeta['djs']

    #print 'curDjID: {}'.format(curDjID)
    #print 'curSongID: {}'.format(curSongID)
    #print 'roomMods: {}'.format(roomMods)

    # Reset the users list
    theUsersList = {}
    
    #Reset the bop List
    theBopList = {}

    #Populate the Users
    users = data['users']
    for user in users:
        theUsersList[user['userid']] = user

    #Run through the room mods. Just make every mod in the room an op
    for roomMod in roomMods:
        #print 'Checking to see if {} is an op'.format(roomMod)
        if theOpList.get(roomMod) == None:
            #print '{} is not an op. Promoting'.format(roomMod)
            theOpList[roomMod] = 0
        #else:
            #print '{} is already an op. Moving on'.format(roomMod)

    bot.modifyLaptop('linux')
    print 'The bot has changed room.', roomInfo['created']

    if not roomDJs:
        bot.addDj()
    
def roomInfo(data):
    global roomDJs
    global curDjID
    global curSongID
    roomInfo = data['room']
    roomMeta = roomInfo['metadata']
    curDjID = roomMeta['current_dj']
    songLog = roomMeta['songlog']
    curSongID = songLog[0]['_id']
    #roomMods = roomMeta['moderator_id']
    roomDJs = roomMeta['djs']

def speak(data):
    name = data['name']
    text = data['text']
    userID = data['userid']

    # This is a debugging line
    #print 'Debug:', data
    print '{} just said {}'.format(name, text)

    #Don't think I need this now that I've added in the DJ events.
    #bot.roomInfo(roomInfo)

    #print 'Got some room info:', roomInfo

    if text == '!hello':
        bot.speak('Hey! How are you {}?'.format(name))

    if text == '!suck it':
        bot.speak('Whoa there. Just go ahead and settle down {}!'.fornat(name))

    if text == '!user count':
        bot.speak('There are {} people jamming in here'.format(str(len(theUsersList))))

    if text == '!help':
        giveHelp(userID)

    if text == '!status':
        if theOpList.has_key(userID):
            bot.pm('You are currently an operator',userID)
        else:
            bot.pm('You, {}, are a valued member of this room'.format(name),userID)

    if text == '!ql':
        checkDjQueue()

    if text == '!q+':
        addToDJQueue(userID=userID,name=name)

def checkDjQueue():
    if len(djQueue) == 0 or djQueue == None:
        bot.speak('The DJ queue is currently empty')
    else:
        queueMsg = ''
        queuePos = 0
        for dj in djQueue:
            queueMsg += '[{}]::{}'.format(queuePos+1,djQueue[queuePos]['name'])
            queuePos += 1
        bot.speak('Here is the current DJ queue: {}'.format(queueMsg))
    #if len(roomDJs) < 5:
        #print 'RoomDJs:', roomDJs
        # Putting a little delay in here to make sure that the messages come through in order
        # and to ensure that the roomInfo() call has had time to full process
        #sleep(0.5)
        #bot.speak('In fact there are {} empty DJ spots right now!'.format(5-len(roomDJs)))
    
def addToDJQueue(userID, name):
    #Normally this should be set to 5, but for testing, we are going to set it to 1
    print roomDJs
    if len(roomDJs) == maxDjCount:
        djQueue.append({'userID':userID,'name':name})
        #Need to figure out the position in the deque object
        bot.speak('Added {} to the DJ queue'.format(name))
        print 'djQueue:', djQueue
    else:
        checkDjQueue()



def calculateAwesome(voteType=None, voterUid=None):
    # Debugging
    print 'Debugging'
    print 'Stepped into calculateAwesome: voteType = {} and voterUid = {} and the current song is {}'.format(voteType, voterUid, curSongID)

    #Here we got a vote event from a user, and need to process it
    if voteType == 'up':
        print 'Got an upvote'
        if theBopList.has_key(curSongID):
            print "Found the song id key for this song"
        else:
            print "Could not find the key for this song"
            theBopList[curSongID] = []
        #print theBopList
        theBopList[curSongID].append(voterUid)
        print 'Right now we have {} votes for this song'.format(len(theBopList[curSongID]))

    #otherwise, we probably called this from a different place to see if we should change the bots voting behavior

    if len(theBopList[curSongID]) == len(theUsersList)/2:
        bot.vote('up')
        bot.speak('This song is awesome')

    if len(theBopList[curSongID]) == len(theUsersList):
        bot.speak('With all {} people jamming, maybe we should turn up the lights'.format(str(len(theBopList[curSongID]))))


def updateVotes(data):
    room = data['room']
    #curSongID = data['current_song']['_id']
    roomMeta = room['metadata']
    voteLog = roomMeta['votelog'][0] 
    voterUid = voteLog[0]
    voteType = voteLog[1]
    print 'Someone has voted.',        data
    calculateAwesome(voteType, voterUid)
    #bot.roomInfo(roomInfo)


def registered(data):  
    global theUsersList
    user = data['user'][0]
    theUsersList[user['userid']] = user
    #print 'Someone registered.',       data
    bot.speak('Hello @{}. I\'m the WalMart greeter of this room. Type !help to see what I can do'.format(user['name']))
    calculateAwesome()
    #bot.roomInfo(roomInfo)

def deregistered(data):
    global theUsersList
    user = data['user'][0]
    del theUsersList[user['userid']]
    #print 'Someone deregistered', data
    bot.speak('Bummer that {} left.'.format(user['name']))
    calculateAwesome()
    if djQueue:
        djInfo = {'userID':user['userid'], 'name':user['name']}
        print djInfo
        if djInfo in djQueue:
            djQueue.remove(djInfo)
            print 'Removed {} from the djQueue'.format(djInfo)
        else:
            print '{} was not in the djQueue'.format(user['name'])
    else:
        print 'No djQueue'

    
    #bot.roomInfo(roomInfo)

   
def newSong(data):
    global curSongID
    global curDjID
    room = data['room']
    room_metadata = room['metadata']
    curSong = room_metadata['current_song']
    curSongID = curSong['_id']
    curDjID = curSong['djid']
    #print 'song_id:', curSongID
    #print 'roomNow:', bot.roomNow()
    #print 'curSong:', curSong
    #print 'metadata:', room_metadata

    #create the bopList key
    theBopList[curSongID] = []

    bot.roomInfo(roomInfo)

    saveState()

def djSteppedUp(data):
    global roomDJs
    #print 'a DJ stepped up', data
    
    user = data['user'][0]
    #print 'user:',user
    
    name = user['name']
    #print 'name:',name

    userID = user['userid']
    #print 'userID',userID

    roomDJs = data['djs']
    #print 'DJs:', roomDJs
    #print 'The new DJ is {}'.format(newDjID)


    # If we have a queue
    if djQueue:
        # If the new DJ was first in the queue
        if userID == djQueue[0]['userID']:
            djQueue.popleft()
            print djQueue
        else:
            bot.speak('It would appear that {} took the DJ spot that was reserved for {}.'.format(name, djQueue[0]['name']))


def djSteppedDown(data):
    global roomDJs
    roomDJs = data['djs']
    print 'DJs:', roomDJs
    print 'a DJ stepped down', data

    #If we haven't maxed out the DJ spots
    if len(roomDJs) < maxDjCount and djQueue:
        bot.speak('A DJ spot has opened up. {} is next in line.'.format(djQueue[0]['name']))


def djEscorted(data):
    global roomDJs
    escortedUser = data['user']
    escortedUserID = escortedUser['userid']
    print 'DJs:', roomDJs
    print 'a DJ was escorted offstage', data
    roomDJs.remove(escortedUserID)
    print 'DJs:', roomDJs

def endSong(data):
    print 'endsong:'#, data

def noSong(data):
    bot.addDj()
    #print 'nosong:', data

def PlaylistToPM(data):
    print 'playlist:', data
    
def privateMessage(data):
    global curSongID
    userID = data['senderid']
    message = data['text']
    print 'Current song is {}'.format(curSongID)
    #print 'room info:', bot.roomInfo()
    #bot.pm('The current song is %s' % curSongID, user)

    # If the person sending the PMs is an Op ....
    if theOpList.has_key(userID):
    #if user == '513101bbaaa5cd316ba3a24e':
        if message == 'bop':
            bot.bop()

        if message == 'snag':
            bot.pm('adding {} to my default playlist'.format(curSongID),userID)
            bot.playlistAdd(curSongID)
            bot.snag()

        if message == 'step up':
            bot.addDj()

        if message == 'skip':
            bot.skip()

        if message == 'step down':
            bot.remDj(myUserID)

        if message == 'playlist':
            bot.playlistAll(PlaylistToPM)

        if message == 'help':
            giveHelp(userID)

    # If the person sending the PM is not an OP, then be a parrot
    else:
        bot.pm(message, userID)

def saveState():
    #json.dump(theOpList,'theOpList.json',sort_keys=True,indent=4)
    with open('theOpList.json','w') as f:
        f.write(json.dumps(theOpList,sort_keys=True,indent=4))
    with open('theBotPlaylist.json','w') as f:
        f.write(bot.playlistAll(json.dumps))

def giveHelp(userID):
    #print 'Offering some help to {}'.format(userID)
    for line in helpMsg:
        bot.pm(line.rstrip(),userID)
        sleep(0.5)
        #print line.rstrip()

    if theOpList.has_key(userID):
        for line in opHelpMsg:
            bot.pm(line.rstrip(),userID)
            sleep(0.5)
            #print line.rstrip()
    
def initializeVars():
    # Initialize some variables here, mostly things that we need from the get go
    global helpMsg
    global opHelpMsg
    global theOpList
    global djQueue
    global roomDJs
    global maxDjCount
    with open('theHelpFile.txt','r') as helpFile:
        helpMsg = helpFile.readlines()
    with open('theOpHelpFile.txt','r') as opHelpFile:
        opHelpMsg = opHelpFile.readlines()

    #empty out the op list
    theOpList = {}

    #Initialize the op list
    with open('theOpList.json','r') as f:
        theOpList = json.load(f)
    if len(theOpList) == 0:
        print 'Loading the default Op List'
        theOpList = {ownerID:0}
        print 'Success'

    # Reset the users list
    theUsersList = {}
    
    #Reset the bop List
    theBopList = {}

    #Initialize the current song ID & DJ ID
    curSongID = '0'
    curDjID = '0'

    #Initialize the DJ Queue
    djQueue = deque([])
    roomDJs = []
    maxDjCount = 1



initializeVars()

# Bind listeners
bot.on('roomChanged',   roomChanged)
bot.on('speak',         speak      )
bot.on('update_votes',  updateVotes)
bot.on('registered',    registered )
bot.on('deregistered',  deregistered)
bot.on('newsong',       newSong)
bot.on('endsong',       endSong)
bot.on('nosong',        noSong)
bot.on('pmmed',         privateMessage)
bot.on('add_dj',        djSteppedUp)
bot.on('rem_dj',        djSteppedDown)
bot.on('escort',        djEscorted)


# Start the bot
bot.start()
from ttapi import Bot
from pprint import pprint
from time import sleep
from collections import deque
from myConfig import *
from BotDB import *
from sys import exit
import json
import re
import sqlite3 as sql

# There should be a file in the same directory as the bot
# that is named myConfig.py. This file shold contain some
# variables that we need to connect to tt.fm
# For example:
# myUserID      = 'XXXXXX'
# myAuthKet     = 'XXXXXX'
# defaultRoom   = 'XXXXXX'
# ownerID       = 'XXXXXX'
# dbFile        = '<BotName>.sqlite'

bot = Bot(myAuthKey, myUserID, defaultRoom)

# Define callbacks
def roomChanged(data): 
    global theUsersList
    global theBopList
    global curSongID
    global curDjID
    global theOpList
    global maxDjCount
    global roomDJs
    global roomOwner
    roomInfo = data['room']
    roomMeta = roomInfo['metadata']
    curDjID = roomMeta['current_dj']
    songLog = roomMeta['songlog']
    curSongID = songLog[0]['_id']
    roomMods = roomMeta['moderator_id']
    maxDjCount = roomMeta['max_djs']
    roomOwnerID = roomMeta['creator']['userid']

    # Reset the users list
    theUsersList = {}
    
    #Reset the bop List
    theBopList = {}

    buildRoomDjsList(roomMeta['djs'])


    #Populate the Users
    users = data['users']
    for user in users:
        theUsersList[user['userid']] = user

    buildOpList(roomMods)

    bot.modifyLaptop('linux')
    #print 'The bot has changed room.'
    #print 'The new room is {} and it allows {} max DJs'.format(roomInfo['name'],maxDjCount)
    #print 'There are currently {} DJs'.format(roomDJs)

    checkIfBotShouldDJ()

def buildOpList(roomMods):
    #Run through the room mods. Just make every mod in the room an op
    for roomMod in roomMods:
        if not roomMod in theOpList:
            theOpList.append(roomMod)

def updateUser(data):
    print 'Update User: ',data
    
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

    #Fill in the DJs
    buildRoomDjsList(roomMeta['djs'])

def speak(data):
    name = data['name']
    text = data['text']
    userID = data['userid']

    print '{} just said \"{}\"'.format(name, text)

    if re.match('^[!+/]',text):
        print 'Received a command: \"{}\"'.format(text[1:])
        processCommand(command=text[1:],userID=userID)

def processCommand(command,userID):
    userName = theUsersList[userID]['name']

    # Catch the /me commands to the room and move on.
    if re.match('^me ',command):
        pass

    elif command == 'hello':
        bot.speak('Hey! How are you {}?'.format(userName))

    elif command == 'suck it':
        bot.speak('Whoa there. Just go ahead and settle down {}!'.format(userName))

    elif command == 'user count':
        bot.speak('There are {} people jamming in here'.format(str(len(theUsersList))))

    elif command == 'help':
        giveHelp(userID)

    elif command == 'status':
        if userID in theOpList:
            bot.pm('You are currently an operator',userID)
        else:
            bot.pm('You, {}, are a valued member of this room'.format(userName),userID)

    elif command == 'ql' or command == 'queue list':
        checkDjQueue()

    elif command == 'q+' or command == 'add' or command == 'queue add':
        addToDJQueue(userID=userID,name=userName)

    elif command == 'q-' or command == 'remove' or command == 'queue remove':
        removeFromDJQueue(userID=userID,name=userName)

    elif command == 'theme':
        if roomTheme == None:
            bot.speak('There\'s no theme right now. Anything goes!')
        else:
            bot.speak('The theme right now is \"{}\"'.format(roomTheme))

    elif re.match('^top [0-9]+ (artists|songs|albums|DJs|djs)$',command):
        commandInts = [int(s) for s in command.split() if s.isdigit()]
        queryMap = {'albums':'songAlbum', 'artists':'songArtist', 'songs':'songName', 'DJs':'userID', 'djs':'userID'}
        query = command.split()[2]
        #print 'Got a command to look for the top {} {}'.format(commandInts[0], query)
        results = getMostSongData(con=dbConn, cnt=commandInts[0], songItem=queryMap[query])

        if results:
            print 'SQL returned these results: {}'.format(results)
            speakResults(cnt=commandInts[0], item=query, recs=results)
        else:
            bot.speak('Strange, I don\'t seem t have any data on the top {}'.format(query))

    elif re.match('^seen .*$',command):
        # Account for names with spaces in them
        # We need to drop off the first word. Split()[1:] will return a list with the rest of the words
        seekNames = command.split()[1:]
        # Now we need to join that list back into a single string
        seekName = ' '.join(seekNames)
        print 'Looking up history for {}'.format(seekName)
        seekID = getUserIDByName(con=dbConn, uname=seekName)
        print 'Found ID {}'.format(seekID)
        history = getLastUserHistoryByID(con=dbConn, uid=seekID)
        print 'Got the following history:',history
        if history:
            msg = '{} was last seen doing \"{}\" on {}'.format(seekName,history[0],history[1])
        else:
            msg = 'I don\'t seem to have any data on {}'.format(seekName)
        bot.speak(msg)
        if history[2] != seekName:
            bot.speak('{} seems to have changed their name to {}'.format(seekName,history[2]))

    elif command == 'top lamer':
        results = getTopVoter(con=dbConn, voteType='down')
        print results
        # results is a list of tuples: [(count, userid)]
        if results:
            userName = theUsersList[results[0][1]]['name']
            bot.speak('It would appear that {} is the biggest lamer with {} lames'.format(userName, results[0][0]))
        else:
            bot.speak('Apparently no one has ever hit the lame button in here!')

    elif command == 'top awesomer':
        results = getTopVoter(con=dbConn, voteType='up')
        #print results
        # results is a list of tuples: [(count, userid)]
        if results:
            userName = theUsersList[results[0][1]]['name']
            bot.speak('It would appear that {} is the biggest awesomer with {} awesomes'.format(userName, results[0][0]))
        else:
            bot.speak('Apparently no one has ever hit the awesome button in here!')

    elif command == 'awesome DJ' or command == 'awesome dj':
        results = getTopDJVoted(con=dbConn,voteType='up')
        if results:
            userName = theUsersList[results[0][1]]['name']
            bot.speak('It looks like {} is the most awesomest DJ, having played songs for a total of {} awesome votes'.format(userName, results[0][0]))
        else:
            bot.speak('Does anyone ever vote in here?')

    elif command == 'lame DJ' or command == 'lame dj':
        results = getTopDJVoted(con=dbConn,voteType='down')
        if results:
            userName = theUsersList[results[0][1]]['name']
            bot.speak('It looks like {} is the most lamest DJ, having played songs for a total of {} lame votes'.format(userName, results[0][0]))
        else:
            bot.speak('Does anyone ever lame songs in here?')
    else:
        bot.speak('I\'m sorry, I don\'t understand the {} command'.format(command))

def speakResults(cnt, item, recs):
    print 'Got these recs:'.format(recs)
    bot.speak('Here are the top {} {}'.format(cnt, item))
    sleep(0.25)
    for rec in recs:
        thing = rec[1]
        if item == 'DJs':
            thing = theUsersList[rec[1]]['name']
        bot.speak('{} {}'.format(rec[0], thing))
        sleep(0.25)

def checkDjQueue():
    # This function sucks. Need to be more clear about what is happening.
    if djQueue:
        # We have a queue. Spit it out
        speakDjQueue()
    elif len(roomDJs) < maxDjCount:
        # We don't have enough DJs
        bot.speak('There are only {} DJs. No need for a queue'.format(len(roomDJs)))
    elif len(roomDJs) == maxDjCount:
        bot.speak('There is no queue. Type !add to claim your spot now.')
    else:
        bot.speak('I should not be here. :poop:')

def speakDjQueue():
    queuePos = 0
    for dj in djQueue:
        djName = theUsersList[djQueue[queuePos]]['name']
        bot.speak('Q: [{}]{}'.format(queuePos+1,djName))
        queuePos += 1
        sleep(0.25)

def checkIsQualifiedToQueue(userID):
    userName = theUsersList[userID]['name']
    djInfo = {'userID':userID, 'name':userName}
    
    if userID in roomDJs     or userID in djQueue:
        #This user is disqualified
        return False
    else:
        return True
    
def checkIsQueueNeeded():
    if djQueue:
        return True
    elif not djQueue and len(roomDJs) == maxDjCount:
        return True
    else:
        return False

def addToDJQueue(userID, name):
    userName = theUsersList[userID]['name']
    djInfo = {'userID':userID, 'name':userName}
    
    # In order to add to the queue, the person should not be on stage or in the queue already
    # Start by checking qualfications
    if checkIsQualifiedToQueue(userID) and checkIsQueueNeeded():
        print 'Adding {} to the queue'.format(userName)
        djQueue.append(userID)
    elif not checkIsQualifiedToQueue(userID):
        bot.speak('@{}, you are not qualified to get in the queue right now'.format(userName))
    elif not checkIsQueueNeeded():
        checkDjQueue()
    else:
        bot.speak('How did I get here? What the :poop:')

    speakDjQueue()

def removeFromDJQueue(userID, name=None, botOp=None):
    if not name:
        name = theUsersList[userID]['name']
    djInfo = {'userID':userID, 'name':name}
    if djQueue.count(userID) >= 1:
        djQueue.remove(userID)
        if not botOp:
            bot.speak('{} has been removed from the DJ queue'.format(name))
        else:
            bot.pm('{} has been removed from the DJ queue'.format(name),botOp)
    else:
        if not botOp:
            bot.speak('{} doesn\'t seem to be in the queue'.format(name))
        else:
            bot.pm('{} is not in the queue'.format(name),botOp)

def buildRoomDjsList(djData):
    global roomDJs
    #Fill in the DJs
    if type(djData) == dict:
        roomDJs = djData
    elif type(djData) == list:
        pos = 0
        for dj in djData:
            roomDJs[str(pos)] = dj
            pos += 1


def checkIfBotShouldDJ():
    # If I am already a DJ ....
    if myUserID in roomDJs.values():
        # If there at least 2 other DJs, then I should step down
        if len(roomDJs) >= 3 and curDjID != myUserID:
            bot.remDj(myUserID)
    else:
        #If we have 0 or 1 DJs, then step up
        if len(roomDJs) <= 1 and not djQueue:
            bot.addDj()


def calculateAwesome(voteType=None, voterUid=None):
    if voteType == 'up':
        print 'Got an upvote'
        if not theBopList.has_key(curSongID):
            print 'Emptying the bopList for this song'
            theBopList[curSongID] = []
        theBopList[curSongID].append(voterUid)
        print 'Appended this vote to the bop list'

    if len(theBopList[curSongID]) == (len(theUsersList))/3 and (voteType == 'up' or not voteType):
        print 'Bop it!'
        bot.bop()
        bot.speak('This song is awesome')

    #if len(theBopList[curSongID]) == len(theUsersList) and len(theUsersList) >= 5:
    #    bot.snag()
    #    bot.speak('I :yellow_heart: this song')
    #    bot.playlistAdd(curSongID)
    #    bot.becomeFan(curDjID)


def updateVotes(data):
    room = data['room']
    roomMeta = room['metadata']
    print 'updateVoes data: ', data
    voteLog = roomMeta['votelog'][0] 
    voterUid = voteLog[0]
    voteType = voteLog[1]
    print 'Got a {} vote from {}'.format(voteType, theUsersList[voterUid]['name'])
    calculateAwesome(voteType, voterUid)
    addVotingHistory(con=dbConn, vtype=voteType, uid=voterUid, sid=curSongID, djID=curDjID)
    addUserHistory(con=dbConn, uid=voterUid, uname=theUsersList[voterUid]['name'],action='Voted {}'.format(voteType))

def registered(data):  
    global theUsersList
    user = data['user'][0]
    theUsersList[user['userid']] = user
    greeting = getEntersRoomSaying(con=dbConn)
    bot.speak(greeting.format(user['name']))
    if roomTheme:
        processCommand('theme',myUserID)
    calculateAwesome()
    addUserHistory(con=dbConn, uid=user['userid'], uname=user['name'],action='Entered')

def deregistered(data):
    global theUsersList
    user = data['user'][0]
    del theUsersList[user['userid']]
    bot.speak('Bummer that {} left.'.format(user['name'])) 
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
    calculateAwesome() 
    addUserHistory(con=dbConn, uid=user['userid'], uname=user['name'],action='Exited')

def newSong(data):
    global curSongID
    global curDjID
    room = data['room']
    room_metadata = room['metadata']
    curSong = room_metadata['current_song']
    curSongID = curSong['_id']
    curDjID = curSong['djid']

    #create the bopList key
    theBopList[curSongID] = []

    bot.roomInfo(roomInfo)

    checkIfBotShouldDJ()

    addUserHistory(con=dbConn, uid=curDjID, uname=theUsersList[curDjID]['name'],action='Played a song')
    addSongHistory(con=dbConn, sid=curSongID, uid=curDjID, length=curSong['metadata']['length'], artist=curSong['metadata']['artist'], name=curSong['metadata']['song'], album=curSong['metadata']['album'])

def djSteppedUp(data):
    global roomDJs
    user = data['user'][0]
    name = user['name']
    userID = user['userid']
    buildRoomDjsList(data['djs'])
    print 'DJs:', roomDJs


    # If we have a queue
    if djQueue:
        firstInQueueName = theUsersList[djQueue[0]]['name']
        # If the new DJ was first in the queue
        if userID == djQueue[0]:
            djQueue.popleft()
            print djQueue
        else:
            bot.speak('It would appear that @{} took the DJ spot that was reserved for @{}.'.format(name, firstInQueueName))
            bot.remDj(userID)
    checkIfBotShouldDJ()
    addUserHistory(con=dbConn, uid=userID, uname=name,action='Hopped on stage')

def djSteppedDown(data):
    global roomDJs

    buildRoomDjsList(data['djs'])

    #If we haven't maxed out the DJ spots
    if len(roomDJs) < maxDjCount and djQueue:
        bot.speak('A DJ spot has opened up. @{} is next in line.'.format(theUsersList[djQueue[0]]['name']))
        #nextDjTimer()

    addUserHistory(con=dbConn, uid=data['user'][0]['userid'], uname=data['user'][0]['name'],action='Left the stage')

def nextDjTimer():
    nextDjID = djQueue[0]
    nextDjName = theUsersList[nextDjID]['name']
    bot.speak('A DJ spot has opened up. @{} has 15 seconds to step up'.format(nextDjName))
    #isleep(15)
    #if not nextDjID in roomDJs.values():
    #    removeFromDJQueue(userID=nextDjID)
    #    if djQueue:
    #        nextDjTimer()
    #    else:
    #        checkDjQueue()

    checkIfBotShouldDJ()

def djEscorted(data):
    global roomDJs
    escortedUser = data['user']
    escortedUserID = escortedUser['userid']
    print 'DJs:', roomDJs
    print 'a DJ was escorted offstage', data
    #roomDJs.remove(escortedUserID)
    print 'DJs:', roomDJs

    checkIfBotShouldDJ()
    addUserHistory(con=dbConn, uid=escortedUserID, uname=escortedUser['name'],action='Yanked off stage')
    addUserHistory(con=dbConn, uid=data['modid'], uname=theUsersList[data['modid']]['name'],action='Escorted someone from stage')

def endSong(data):
    #print 'endsong:', roomDJs
    #print 'pos 0 in the DJ queue: {}'.format(roomDJs['0'])
    if djQueue:
        #bot.speak('Since we have a DJ queue, it\'s time for @{} to step down.'.format(theUsersList[roomDJs['0']]['name']))
        bot.remDj(roomDJs['0'])

    checkIfBotShouldDJ()

def noSong(data):
    checkIfBotShouldDJ()

def PlaylistToPM(data):
    print 'playlist:', data
    
def privateMessage(data):
    global curSongID
    global roomTheme
    userID = data['senderid']
    userName = theUsersList[userID]['name']
    message = data['text']
    print 'Got a PM from {}: "{}"'.format(userName,message)

    # If the person sending the PMs is an Op ....
    if userID in theOpList:
        if message == 'bop':
            bot.bop()

        elif message == 'snag':
            bot.pm('adding {} to my default playlist'.format(curSongID),userID)
            bot.playlistAdd(curSongID)
            bot.snag()

        elif message == 'step up':
            bot.addDj()

        elif message == 'skip':
            bot.skip()

        elif message == 'step down':
            bot.remDj(myUserID)

        elif message == 'playlist':
            bot.playlistAll(PlaylistToPM)

        elif message == 'help':
            giveHelp(userID)

        elif message == 'die' and (userID == ownerID or userID == roomOwnerID):
            exitGracefully()

        elif re.match('^theme = ', message):
            roomTheme = message[8:]
            addThemeHistory(con=dbConn, uid=userID, theme=roomTheme)
            bot.speak('{} has set the theme for this room to \"{}\"'.format(userName,roomTheme))

        elif message == 'pop':
            bot.speak('Removing {} from the queue since {} asked me to'.format(theUsersList[djQueue[0]['userID']]['name'],userName))
            djQueue.popleft()
            checkDjQueue()

        elif re.match('^dq [0-9]*$',message):
            popPos = int(message[3:])-1
            dqUserId = djQueue[popPos]['userID']
            print 'Attmepting to remove {} from q{}'.format(dqUserId,popPos)
            bot.speak('Yanking {} from the queue. {} made me do it!'.format(theUsersList[dqUserId]['name'],userName))
            removeFromDJQueue(userID=dqUserId,botOp=userID)
            checkDjQueue()

        else:
            bot.pm('Exsqueeze me? Baking powder?',userID)


    # If the person sending the PM is not an OP, then be a parrot
    else:
        bot.pm(message, userID)

def exitGracefully():
    saveState()
    if dbConn:
        dbConn.close()
    exit()

def saveState():
    print 'Saving state'
    with open('theOpList.json','w') as f:
        f.write(json.dumps(theOpList))


def loadState():
    global helpMsg
    global opHelpMsg
    global theOpList

    try:
        with open('theHelpFile.txt','r') as helpFile:
            helpMsg = helpFile.readlines()
    except IOError:
        print 'The file theHelpFile.txt was not found. Help may not work.'

    try:
        with open('theOpHelpFile.txt','r') as opHelpFile:
            opHelpMsg = opHelpFile.readlines()
    except IOError:
        print 'The file theOpHelpFile.txt was not found. Help may not work'

    #Initialize the op list
    try:
        with open('theOpList.json','r') as f:
            theOpList = json.load(f)
    except IOError:
    #if not theOpList:
        print 'Loading the default Op List'
        theOpList.append(ownerID)
        print 'The Op List: {}'.format(theOpList)
        #print 'Success'

def giveHelp(userID):
    #print 'Offering some help to {}'.format(userID)
    for line in helpMsg:
        bot.pm(line.rstrip(),userID)
        sleep(0.5)
        #print line.rstrip()

    if userID in theOpList:
        for line in opHelpMsg:
            bot.pm(line.rstrip(),userID)
            sleep(0.5)
            #print line.rstrip()

def songSnagged(data):
    print 'Song snagged: ', data
    command = data['command'] #This should always = snagged
    userID = data['userid'] #This will be set to the user who snagged the file
    addUserHistory(con=dbConn, uid=userID, uname=theUsersList[userID]['name'],action='Snagged a song')
    addSnagHistory(con=dbConn, uid=userID, sid=curSongID)

def newModerator(data):
    global theOpList
    theOpList.append(data['userid'])

def remModerator(data):
    global theOpList
    theOpList = list(filter((data['userid']).__ne__,theOpList))

def initializeVars():
    # Initialize some variables here, mostly things that we need from the get go
    global helpMsg
    global opHelpMsg
    global theOpList
    global djQueue
    global roomDJs
    global maxDjCount
    global roomTheme
    global dbConn

    #empty out the op list
    theOpList = []
    
    loadState()

    # Reset the users list
    theUsersList = {}
    
    #Reset the bop List
    theBopList = {}

    #Initialize the current song ID & DJ ID
    curSongID = '0'
    curDjID = '0'

    #Initialize the DJ Queue
    djQueue = deque([])
    roomDJs = {}
    maxDjCount = 1

    #Set the theme to empty
    roomTheme = None

    #Create the database connection
    dbConn = checkDatabaseVersion(dbFile)


initializeVars()

# Bind listeners
bot.on('roomChanged',   roomChanged)
bot.on('speak',         speak)
bot.on('update_votes',  updateVotes)
bot.on('registered',    registered)
bot.on('deregistered',  deregistered)
bot.on('newsong',       newSong)
bot.on('endsong',       endSong)
bot.on('nosong',        noSong)
bot.on('pmmed',         privateMessage)
bot.on('add_dj',        djSteppedUp)
bot.on('rem_dj',        djSteppedDown)
bot.on('escort',        djEscorted)
bot.on('update_user',   updateUser)
bot.on('snagged',       songSnagged)
bot.on('new_moderator', newModerator)
bot.on('rem_moderator', remModerator)

# Start the bot
bot.start()
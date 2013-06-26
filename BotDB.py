import sqlite3 as sql
from random import randint
from myConfig import *

def checkDatabaseVersion(dbFile):
	conn = sql.connect(dbFile)
	cur = conn.cursor()

	#Set the default version. The SQL below should override this
	dbVersion = 0
	try:
		cur.execute('SELECT version FROM BotDbVersion')
		row = cur.fetchone()
		dbVersion = row[0]
		print 'The database is at version {}'.format(dbVersion)


	except sql.Error, e:
		# If we don't have a Version table, then we need will recreate the entire schema
		# Set the dbVersion back to the beginning
		dbVersion = 0
	finally:
		upgradeDatabase(conn,dbVersion)
		return conn

def upgradeDatabase(con,ver):
	# This function should walk through the different versions, and if it is done properly,
	# Upgrade the database from and given point to the most recent.
	# This will consist of a series of
	# if ver == x:
	#	ver += 1
	#	do stuff
	# if ver == y:
	#	ver += 1
	#	do stuff
	# if ver == z:
	#	ver += 1
	#	pass

	#Initial state
	if ver == 0:
		print 'Upgrading database to version {}'.format(ver)
		with con:
			try:
				cur = con.cursor()
				cur.executescript("""
					DROP TABLE IF EXISTS BotDbVersion;
					DROP TABLE IF EXISTS SongHistory;
					DROP TABLE IF EXISTS UserHistory;
					DROP TABLE IF EXISTS VotingHistory;
					DROP TABLE IF EXISTS SnagHistory;
					DROP TABLE IF EXISTS BotOperators;
					DROP TABLE IF EXISTS DjQueue;
					CREATE TABLE BotDbVersion (versionId INTEGER PRIMARY KEY, version INTEGER);
					CREATE TABLE SongHistory (songHistoryId INTEGER PRIMARY KEY, songID TEXT, songPlayDateTime TEXT, userID TEXT, songLength INT, songArtist TEXT, songName TEXT, songAlbum TEXT);
					CREATE TABLE UserHistory (UserHistoryId INTEGER PRIMARY KEY, userID TEXT, seenDateTime TEXT, userName TEXT, action TEXT);
					CREATE TABLE VotingHistory (VotingHistoryId INTEGER PRIMARY KEY, voteType TEXT, userID TEXT, songID TEXT, voteDateTime TEXT, djID TEXT);
					CREATE TABLE SnagHistory (SnagHistoryID INTEGER PRIMARY KEY, userID TEXT, songID TEXT, snagDateTime TEXT);
					CREATE TABLE ThemeHistory (ThemeHistoryID INTEGER PRIMARY KEY, themeText TEXT, userID TEXT, themeSetDateTime TEXT);
					CREATE TABLE BotOperators (BotOperatorID INTEGER PRIMARY KEY, userID TEXT);
					CREATE TABLE DjQueue (DjQueueID INTEGER PRIMARY KEY, userID TEXT);
					INSERT INTO BotDbVersion (version) VALUES (0);
				""")
				con.commit()
			except sql.Error, e:
				print 'Caught a SQLite Exception: {}'.format(e)
		ver += 1

	if ver == 1:
		print 'Upgrading database to version {}'.format(ver)
		with con:
			cur = con.cursor()
			cur.executescript("""
				CREATE TABLE StuffToSayWhenTheBotLikesASong (SayingID INTEGER PRIMARY KEY, Saying TEXT);
				CREATE TABLE StuffToSayWhenSomeoneEntersTheRoom (SayingID INTEGER PRIMARY KEY, Saying TEXT);
			""")
			cur.executemany("INSERT INTO StuffToSayWhenTheBotLikesASong (Saying) VALUES (?)", [('This song is aweomse',),('This song rocks',),(':yellow_heart:',),('Oh yeah!',),(':fire:',),(':clap:',)])
			cur.executemany("INSERT INTO StuffToSayWhenSomeoneEntersTheRoom (Saying) VALUES(?)", [('Welcome @{}! I\'m the Wal-Mart greeter for this room.',),('Hey there @{}, I\'m your friendly neighborhood bot.',),('@{}, I am your father.',),('@{}!!!!!!!!!!!!!!!!',)])
			cur.execute("UPDATE BotDBVersion SET version = ? WHERE version = ?",(ver+1,ver))
		ver += 1

	if ver == 2:
		print "Upgrading database to version {}".format(ver)
		with con:
			try:
				cur = con.cursor()
				cur.executescript("""
					ALTER TABLE SongHistory ADD songRoomID TEXT;
					ALTER TABLE UserHistory ADD userRoomID TEXT;
					ALTER TABLE VotingHistory ADD voteRoomID TEXT;
					ALTER TABLE SnagHistory ADD SnagRoomID TEXT;
					ALTER TABLE ThemeHistory ADD ThemeRoomID TEXT;
					ALTER TABLE BotOperators ADD BotOpRoomID TEXT;
					ALTER TABLE DjQueue ADD DjQueueRoomID TEXT;
				""")
				print 'Updated all of the table structures.'
				cur.execute("UPDATE SongHistory SET songRoomID = ? WHERE songRoomID IS NULL",(defaultRoom,))
				cur.execute("UPDATE UserHistory SET userRoomID = ? WHERE userRoomID IS NULL",(defaultRoom,))
				cur.execute("UPDATE VotingHistory SET voteRoomID = ? WHERE VotingHistoryId IS NULL",(defaultRoom,))
				cur.execute("UPDATE SnagHistory SET SnagRoomID = ? WHERE SnagRoomID is NULL",(defaultRoom,))
				cur.execute("UPDATE ThemeHistory SET ThemeRoomID = ? WHERE ThemeRoomID IS NULL",(defaultRoom,))
				cur.execute("UPDATE BotOperators SET BotOpRoomID = ? WHERE BotOpRoomID IS NULL",(defaultRoom,))
				cur.execute("UPDATE DjQueue SET DjQueueRoomID = ? WHERE DjQueueRoomID IS NULL",(defaultRoom,))
				print "Updated all of the data"
				cur.execute("UPDATE BotDBVersion SET version = ? WHERE version = ?",(ver+1,ver))
				print "Updated the version to {}".format(ver+1)
			except sql.Error, e:
				print "Caught a SQLite Exception: {}".format(e)
		# This is the most recent version, nothing to do here, for now
		print 'Database is up to date.'
		ver +=1



def addSongHistory(con, sid, uid, length, artist, name, album):
	print "Adding song history: sid = {}, uid = {}, length = {}, artist = {}, name = {}, album = {}, songRoomID = {}".format(sid, uid, length, artist, name, album,defaultRoom)
	with con:
		cur = con.cursor()
		cur.execute("INSERT INTO SongHistory (songID, songPlayDateTime, userID, songLength, songArtist, songName, songAlbum, songRoomID) VALUES (?,datetime(\'now\',\'localtime\'),?,?,?,?,?,?)", (sid,uid,length, artist, name, album, defaultRoom))
		con.commit()

def addUserHistory(con, uid, uname, action):
	with con:
		cur = con.cursor()
		cur.execute("INSERT INTO UserHistory (userID, seenDateTime, userName, action, userRoomID) VALUES (?,datetime(\'now\',\'localtime\'),?,?,?)", (uid,uname,action,defaultRoom))
		con.commit()

def addVotingHistory(con, vtype, uid, sid, djID):
	with con:
		cur = con.cursor()
		print "INSERT INTO VotingHistory (voteType, userID, songID, djID, voteDateTime, voteRoomID) VALUES ({},{},{},{},datetime(\'now\',\'localtime\'),{})".format(vtype,uid,sid,djID,defaultRoom)
		cur.execute("INSERT INTO VotingHistory (voteType, userID, songID, djID, voteDateTime, voteRoomID) VALUES (?,?,?,?,datetime(\'now\',\'localtime\'),?)", (vtype,uid,sid,djID,defaultRoom))
		con.commit()

def addSnagHistory(con, uid, sid):
	with con:
		cur = con.cursor()
		cur.execute("INSERT INTO SnagHistory (userID, songID, snagDateTime, SnagRoomID) VALUES (?,?,datetime(\'now\',\'localtime\'),?)", (uid,sid,defaultRoom))
		con.commit()

def addThemeHistory(con, uid, theme):
	with con:
		cur = con.cursor()
		cur.execute("INSERT INTO ThemeHistory (userID, themeText, themeSetDateTime, ThemeRoomID) VALUES (?,?,date(\'now\',\'localtime\'),?)", (uid,theme,defaultRoom))
		con.commit()

# This theme proposal system needs more thought
#def addThemeProposal(con, theme, uid):
#	with con:
#		cur = con.cursor()
#		cur.execute("INSERT INTO ThemeProposals (ThemeText, ProposedBy, ProposedDate) VALUES (?, ?, date(\'now\',\'localtime\'))", (theme, uid))
#		con.commit()

#def addThemeVote(con, theme, uid):
#	with con:
#		cur = con.cursor()
#		cur.execute("SELECT ThemeProposalID FROM ThemeProposals WHERE ThemeText = ? AND ProposedDate"

#def checkThemeVoteOK(cur, uid):
#	with con:
#		cur = con.cursor()
#		cur.execute("SELECT ThemeVoteUser FROM ThemeVoting WHERE ThemeVoteUser = ? AND ThemeVoteDate = date(\'now\',\'localtime\')", (uid))
#		row = cur.fetchone()
#		return row

#def checkThemeProposalExists(con, theme):
#	with con:
#		cur = con.cursor()
#		cur.execute("SELECT ProposedBy, ProposedDate from ThemeProposals WHERE Theme=? ORDER BY ThemeProposalID DESC LIMIT 1",(theme))
#		row = cur.fetchone()
#		return row

def saveBotOperators(con, BotOps):
	with con:
		cur = con.cursor()
		cur.execute("DELETE FROM BotOperators")
		cur.executemany("INSERT INTO BotOperators (userID) VALUES (?)",(BotOps))
		cur.commit()

def saveDjQueue(con, djQueue):
	with con:
		cur = con.cursor()
		cur.execute("DELETE FROM DjQueue")
		cur.executemany("INSERT INTO DjQueue (userID) VALUES (?)",(djQueue))
		cur.commit()

def getMostSongData(con, cnt, songItem, ignoreID):
	with con:
		cur = con.cursor()
		qText="SELECT COUNT(1), {} FROM SongHistory WHERE userID != ? AND songRoomID = ? GROUP BY {} ORDER BY 1 DESC LIMIT {}".format(songItem,songItem,str(cnt))
		#print qText
		cur.execute(qText,(ignoreID,defaultRoom))
		rows = cur.fetchall()
	return rows

def getMostVoteData(con, cnt, voteItem, voteType=None):
	with con:
		cur = con.cursor()
		qText="SELECT COUNT(1), {} FROM VotingHistory WHERE voteRoomID = ? ".format(voteItem)
		if voteType:
			qText += "AND voteType = ? "
		qText += "GROUP BY {} ORDER BY 1 DESC LIMIT ?".format(voteItem)
		print qText
		cur.execute(qText,(defaultRoom,voteType,str(cnt)))
		#cur.execute("SELECT COUNT(*), userID FROM VotingHistory WHERE voteType = ? GROUP BY userID ORDER BY 1 DESC LIMIT ?", (voteType,str(cnt)))

		rows = cur.fetchall()
		print "SQL Returned:".format(rows)
	return rows

def getTopVoter(con, voteType, ignoreID):
	print 'Finding the top awesomer'
	with con:
		cur = con.cursor()
		cur.execute("SELECT COUNT(1), userID FROM VotingHistory WHERE VoteType = ? AND userID != ? AND voteRoomID = ? GROUP BY userID ORDER BY 1 DESC LIMIT 1",(voteType,ignoreID,defaultRoom))
		rows = cur.fetchall()
		print rows
	return rows

def getTopDJVoted(con, voteType, ignoreID):
	with con:
		cur = con.cursor()
		cur.execute("SELECT COUNT(1), DjID FROM VotingHistory WHERE VoteType = ? AND DjID != ? AND voteRoomID = ? GROUP BY DjID ORDER BY 1 DESC LIMIT 1",(voteType,ignoreID,defaultRoom))
		rows = cur.fetchall()
	return rows

def getUserNameByID(con, uid):
	with con:
		cur = con.cursor()
		cur.execute("SELECT userName FROM UserHistory WHERE userID = ? AND userRoomID = ? ORDER BY UserHistoryId DESC LIMIT 1",(str(uid),defaultRoom))
		row = cur.fetchone()
		print row
		print 'Found {} for ID {}'.format(row[0],uid)
	return row[0]

def getUserIDByName(con, uname):
	print 'Looking up {}'.format(uname)
	with con:
		cur = con.cursor()
		try:
			cur.execute("SELECT userID FROM UserHistory WHERE userName = ? AND userRoomID = ? ORDER BY UserHistoryId DESC LIMIT 1",(uname,defaultRoom))
		except:
			print 'SQL Exception', sys.exc_info()[0]
		finally:
			row = cur.fetchone()
			print row
	return row[0]

def getLastUserHistoryByID(con, uid):
	with con:
		cur = con.cursor()
		cur.execute("SELECT action, seenDateTime, userName FROM UserHistory WHERE userID = ? AND userRoomID = ? ORDER BY UserHistoryId DESC LIMIT 1",(str(uid),defaultRoom))
		row = cur.fetchone()
	return row

def getLikeSongSaying(con):
	with con:
		cur = con.cursor()
		cur.execute("SELECT count(1) FROM StuffToSayWhenTheBotLikesASong")
		cnt = cur.fetchone()
		cur.execute("SELECT Saying FROM StuffToSayWhenTheBotLikesASong WHERE SayingID = ?",(randint(1,cnt[0]),))
		row = cur.fetchone()
		#rows is now a list of tuples [()]
		# So the next line will shuffle the tuples, and return the data from one of them
	return row[0]

def getEntersRoomSaying(con):
	with con:
		cur = con.cursor()
		cur.execute("SELECT count(1) FROM StuffToSayWhenSomeoneEntersTheRoom")
		cnt = cur.fetchone()
		cur.execute("SELECT Saying FROM StuffToSayWhenSomeoneEntersTheRoom WHERE SayingID = ?",(randint(1,cnt[0]),))
		row = cur.fetchone()
	return row[0]
    
def getSongSeedData(con, songID):
    with con:
        print "Looking up song {}".format(songID)
        result = {}
        cur = con.cursor()
        cur.execute("SELECT songPlayDateTime, userID FROM SongHistory WHERE songID = ? AND songRoomID = ? ORDER BY songHistoryId ASC LIMIT 1",(songID,defaultRoom))
        #row should be DateTime & userID
        row = cur.fetchone()
        
        #print "Seed result query 1:",row
        if row:
            result['firstPlayDate'] = row[0]
            result['userID'] = row[1]
        
            #Convert UserID to Name
            cur.execute("SELECT userName FROM UserHistory WHERE userID = ? AND userRoomID = ? ORDER BY userHistoryID DESC LIMIT 1",(result["userID"],defaultRoom))
            row = cur.fetchone()
            
            if row:
            	print "Got row: ",row
                result['userName'] = row[0]
            else:
            	print "Lost it at Convert UserID to Name"
                result['userName'] = 'Unknown'
        
            #Get total plays
            cur.execute("SELECT COUNT(1) FROM SongHistory WHERE songID = ? AND songRoomID = ?",(songID,defaultRoom))
            row = cur.fetchone()
            if row:
            	print "Got row: ",row
                result['totalPlays'] = row[0]
            else:
            	print "Lost it at Get total plays"
                result['totalPlays'] = 0
        
            #Get total likes
            cur.execute("SELECT COUNT(1) FROM VotingHistory WHERE songID = ? AND voteType = ? AND voteRoomID = ?",(songID,'up',defaultRoom))
            row = cur.fetchone()
            if row:
            	print "Got row: ",row            	
                result['totalLikes'] = row[0]
            else:
            	print "Lost it at Get total likes"
                result['totalLikes'] = 0

            #Get total snags
            cur.execute("SELECT COUNT(1) FROM SnagHistory WHERE songID = ? AND snagRoomID = ?",(songID,defaultRoom))
            row = cur.fetchone()
            if row:        
            	print "Got row: ",row
                result['totalSnags'] = row[0]
            else:
            	print "Lost it at Get total songs"
                result['totalSnags'] = 0
        else:
            result = None
        
    print result
    return result
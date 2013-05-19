import sqlite3 as sql

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
			cur.execute("UPDATE BotDBVersion SET version = ? WHERE version = ?",(ver,ver-1))
		# This is the most recent version, nothing to do here, for now
		print 'Database is up to date.'
		ver += 1

def addSongHistory(con, sid, uid, length, artist, name, album):
	with con:
		cur = con.cursor()
		cur.execute("INSERT INTO SongHistory (songID, songPlayDateTime, userID, songLength, songArtist, songName, songAlbum) VALUES (?,datetime(\'now\'),?,?,?,?,?)", (sid,uid,length, artist, name, album))
		con.commit()

def addUserHistory(con, uid, uname, action):
	with con:
		cur = con.cursor()
		cur.execute("INSERT INTO UserHistory (userID, seenDateTime, userName, action) VALUES (?,datetime(\'now\'),?,?)", (uid,uname,action))
		con.commit()

def addVotingHistory(con, vtype, uid, sid, djID):
	with con:
		cur = con.cursor()
		print "INSERT INTO VotingHistory (voteType, userID, songID, djID, voteDateTime) VALUES ({},{},{},{},datetime(\'now\'))".format(vtype,uid,sid,djID)
		cur.execute("INSERT INTO VotingHistory (voteType, userID, songID, djID, voteDateTime) VALUES (?,?,?,?,datetime(\'now\'))", (vtype,uid,sid,djID))
		con.commit()

def addSnagHistory(con, uid, sid):
	with con:
		cur = con.cursor()
		cur.execute("INSERT INTO SnagHistory (userID, songID, snagDateTime) VALUES (?,?,datetime(\'now\'))", (uid,sid))
		con.commit()

def addThemeHistory(con, uid, theme):
	with con:
		cur = con.cursor()
		cur.execute("INSERT INTO ThemeHistory (userID, themeText, themeSetDateTime) VALUES (?,?,datetime(\'now\'))", (uid,theme))
		con.commit()

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

def getMostSongData(con, cnt, songItem):
	with con:
		cur = con.cursor()
		qText="SELECT COUNT(*), {} FROM SongHistory GROUP BY {} ORDER BY 1 DESC LIMIT {}".format(songItem,songItem,str(cnt))
		cur.execute(qText)
		rows = cur.fetchall()
	return rows

def getMostVoteData(con, cnt, voteItem, voteType=None):
	with con:
		cur = con.cursor()
		qText="SELECT COUNT(*), {} FROM VotingHistory ".format(voteItem)
		if voteType:
			qText += "WHERE voteType = ? "
		qText += "GROUP BY {} ORDER BY 1 DESC LIMIT ?".format(voteItem)
		print qText
		cur.execute(qText,(voteType,str(cnt)))
		#cur.execute("SELECT COUNT(*), userID FROM VotingHistory WHERE voteType = ? GROUP BY userID ORDER BY 1 DESC LIMIT ?", (voteType,str(cnt)))

		rows = cur.fetchall()
		print "SQL Returned:".format(rows)
	return rows

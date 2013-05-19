import sqlite3 as sql

def checkDatabaseVersion(dbFile):
	conn = sql.connect(dbFile)
	cur = conn.cursor()

	#Set the default version. The SQL below should override this
	dbVersion = 0
	try:
		cur.execute('SELECT version FROM BotDbVersion')
		row = cur.fetchone()
		dbVersion = row['version']


	except sql.Error, e:
		# If we don't have a Version table, then we need to create the entire schema
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
		""")

		conn.commit()
		dbVersion = 0
	finally:
		upgradeDatabase(conn,dbVersion)
		return conn

def upgradeDatabase(con,ver):
	if ver == 0:
		with con:
			try:
				cur = con.cursor()
				cur.execute('INSERT INTO BotDbVersion(version) VALUES (1)')
				con.commit()
			except sql.Error, e:
				print 'Caught a SQLite Exception: {}'.format(e)

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
		cur.executemany("INSERT INTO BotOperators (userID) VALUES (?)",BotOps)
		cur.commit()

def saveDjQueue(con, djQueue):
	with con:
		cur = con.cursor()
		cur.execute("DELETE FROM DjQueue")
		cur.executemany("INSERT INTO DjQueue (userID) VALUES (?)",djQueue)
		cur.commit()

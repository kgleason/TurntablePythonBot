#TurntablePythonBot

A [Turntable.fm](http://turntable.fm) bot written in Python using [ttapi from alaingilbert](https://github.com/alaingilbert/Turntable-API)

I've seen a few different TT bots, and I wanted to take the opportunity to write my own and use some of what I've been learning as I've been learning Python.

Feel free to borrow anything that you find helpful, even though I don't think there is anything too terribly original in here. 

Eventually I intended to clean up some of the patterns and make this less procedural, but that will depend upon my progress with the Python learning. For now, it seems to be doing what I want it do.

## Public commands

Here is a list of the commands that this bot will accept from the public chat. In these examples, all of the commands are prefixed with `!`, but in reality, `!`, `+`. or `/` can be used to prefix any command.

+ `!hello` : Have it say hello to you
+ `!suck it` : See what happens if you offend it
+ `!crowd` : Get it to announce how many people are in here
+ `!help` : Presumably you already figured this one out
+ `!queue list` : Show the current DJ queue. Alias: `!ql`
+ `!queue add` : Get yourself added to the queue. Aliases: `!q+` or `!add`
+ `!queue remove` : Remove yourself from the queue. Aliases: `!q-` or `!remove`
+ `!next` : Get the next song in the bot playlist
+ `!status` : Get your current status.
+ `!theme` : Get the theme for today.
+ `!seen <djname>` :  Get the last recorded activity for \<djname\>
+ `!top awesomer` : Get the name of the person who has cast the most Awesome votes.
+ `!awesome DJ` : Get the name of the DJ that has received the most awesome votes.
+ `!lame DJ` : Get the name of the DJ that has received the most lame votes.
+ `!top X [artists|songs|albums|djs]` :  Get some stats. For example `!top 5 djs` will return the names of the DJs that have played the most songs.

## Private commands

If the `!status` command tells you that you are a bot operator, then the following commands are also available via Private Message with the bot. The Private Message commands do not require any sort of command prefix.

+ `bop` : make the bot give the current song an awesome, regardless of the state of the room.
+ `snag` : I'll add the current song to my playlist
+ `step up` : Make me a DJ
+ `step down` : Get me off the stage
+ `dq <Position#>` : remove the person at <Position#> from the DJ Queue
+ `pop` : remove the person in first place in the DJ Queue. The same as `dq 1`
+ `theme = <room theme>` : set & announce the theme for the room
+ `delete next` : the next next song in the Bot's queue. This will cause the bot to update it's profile.

## Running your own

If you want to start your own copy of my bot, then make sure that you have SQLite3 or better installed. Also python version 2.7.3 or higher. I haven't done extensive version testing, but I know that it will run on python 2.7.3 and 2.7.4. After you clone the repository, feel free to rename 'K-Bot.py' to whatever you want. Lastly create a file called myConfig.py that looks like this:

```python
myUserID 	= 'UUUUUUUUUUUUUUUUUUUUUUUU'	# The user ID of your account
myAuthKey 	= 'AAAAAAAAAAAAAAAAAAAAAAAA'	# Your AuthKey
ownerID 	= 'OOOOOOOOOOOOOOOOOOOOOOOO'	# The user ID of the bots owner. There are a couple of special owner commands.
defaultRoom	= 'RRRRRRRRRRRRRRRRRRRRRRRR'	# The TurnTable ID of the room that you want your bot to join. As of right now, this is the only way to get a bot into a room.
dbFile		= 'BotDB.sqlite'				# The name of the database file to use for the bot. This will be created if it doesn't exist. You can leave this as it, or rename it.
helpURL		= 'https://github.com/kgleason/TurntablePythonBot'	# A URL to print out when users ask for help. The default is to show this page. Change it as you wish.
```

If you don't know how to find all of those IDs, then please have a look at [this bookmarklet](http://alaingilbert.github.com/Turntable-API/bookmarklet.html)
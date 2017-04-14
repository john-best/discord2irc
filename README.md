# discord2irc
A Discord <--> IRC channel relay bot in Python 3.
Note that this relay bot was made for me to learn asnycio and string handling. There may be some issues.

## Requirements
* asyncio
* [discord.py](https://github.com/Rapptz/discord.py/) by Rapptz (more requirements)

## Configuration
Modify settings.conf to your liking. An example of a successfully edited config would be

```
[settings]

[irc]
network = irc.gamesurge.net
port = 6667

nick = TF2RJ_Relay
altnick = TF2RJ_Relay2
realname = TF2RJ Discord to IRC Relay bot

channel = #tfjumpers

[discord]
channel = 111111111111
token = q1w2E3r4XyZ10whatever

[irc_perform]
run1 = command1
run2 = command2 
# note the variable name doesn't matter just make sure it's not a duplicate
```

## Running
```python3 relay.py```

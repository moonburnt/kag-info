##Script that prints info about active King Arthur's Gold servers into terminal. Inspired by bot used on official kag's discord, except it doesnt require discord to function

##TODO: sort output by amount of players
##TODO: fix printed server's descriptions to dont contain info about used mods (disabled them altogether by now, blame kag api for the way they looked)

import requests
import json

kagprefix = "kag://"

##Functions
def kag_servers():
    '''Gets json with list of servers from kag api. Returns python dictionary'''
    servers = requests.get("https://api.kag2d.com/v1/game/1/servers", timeout = 30)
    #return servers
    pydic = json.loads(servers.text)
    return pydic

def alive_servers(servers):
    '''Expects to receive dictionary of currently running servers (a.k.a kag_servers() response). Returns list, consisting only of servers playerList featuring entries'''
    mylist = []
    for x in servers["serverList"]:
        #if x['currentPlayers'] != 0: #this wont do - there are loads of dead servers with currentPlayers == 1. Blame kag api for that
        if len(x['playerList']) != 0:
            mylist.append(x)
    return mylist

def player_amount(servers):
    '''Expects to receive dictionary of active servers (a.k.a response of alive_servers()). Returns int amount of players on servers'''
    players = 0
    # for x in servers["serverList"]:
        # if len(x['playerList']) > 0:
    for x in servers:
        players += len(x['playerList'])
    return players

def server_info(server):
    '''Expects to receive dictionary featuring server's info. Prints interesting entries out of it'''
    name = server['name']
    description = server['description'] #this one is kinda messy, coz it also contains info about used mods, and its all over the place
    ip = server['IPv4Address']
    port = server['port']
    kaglink = kagprefix+str(ip)+":"+str(port)
    gamemode = server['gameMode']
    players = len(server['playerList'])
    #nicknames = server['playerList'] #this one is messy either, coz for now Im printing list as list, without pretty formatting
    nicknames = ', '.join(server['playerList'])

    print("Name: {}\nAddress: {}\nGamemode: {}\nAmount of players: {} \nPlayers: {}\n".format(name, kaglink, gamemode, players, nicknames))

##Usage
if __name__ == "__main__":
    print("Awaiting response from kag api...")
    servers = kag_servers()
    active_servers = alive_servers(servers)

    online = len(active_servers)
    players = player_amount(active_servers)

    print("There are currently {} active servers with {} players".format(online, players))

    print("Servers info:")
    for x in active_servers:
        server_info(x)

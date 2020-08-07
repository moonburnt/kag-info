##Script that prints info about active King Arthur's Gold servers into terminal. Inspired by bot used on official kag's discord, except it doesnt require discord to function

##Imports
import requests #to get json with data from kag's api
import json #to turn json into python's dictionary
import re #to remove MODS USED part from description of modded servers
import argparse #for launch arguments used to do various shenanigans with output

kagprefix = "kag://"

##Functions
def kag_servers():
    '''Gets json with list of servers from kag api. Returns python dictionary'''
    servers = requests.get("https://api.kag2d.com/v1/game/1/servers", timeout = 30)
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
    for x in servers:
        players += len(x['playerList'])
    return players

def server_info(server):
    '''Expects to receive dictionary featuring server's info. Prints interesting entries out of it'''
    name = server['name']
    raw_description = server['description'] #this one is kinda messy, coz it also contains info about used mods, and its all over the place. Blame kag api for that
    description = re.sub("\n\n.*", "", raw_description) #because of reason above, Im cleaning it up. MODS USED usually go after two empty lines, so I delet them and everything after
    ip = server['IPv4Address']
    port = server['port']
    password_protected = server['password']
    kaglink = kagprefix+str(ip)+":"+str(port)
    gamemode = server['gameMode']
    using_mods = server['usingMods']
    players = len(server['playerList'])
    maxplayers = server['maxPlayers']
    player_amount = str(players)+"/"+str(maxplayers)
    spectators = server['spectatorPlayers']
    nicknames = ', '.join(server['playerList'])

    print("\nName: {}\nDescription: {}\nAddress: {}\nRequires Password: {}\nGamemode: {}\nUsing Mods: {}\nPlayers: {} \nSpectators: {} \nCurrently Playing: {}".format(name, description, kaglink, password_protected, gamemode, using_mods, player_amount, spectators, nicknames))

def players_amount(x):
    '''Receives dictionary entry with server's info. Returns amount of players on server'''
    return len(x.get('playerList'))

##Usage
if __name__ == "__main__":
    #argparse shenanigans
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-ni", "--nointro", help="Doesnt show info message about connecting to api", action="store_true")
    argparser.add_argument("-nd", "--nodetails", help="Only shows global online statistics, without detailed info about active servers", action="store_true")
    argparser.add_argument("-sm", "--skip_modded", help="Shows only vanilla (non-modded) servers", action="store_true")
    argparser.add_argument("-sv", "--skip_vanilla", help="Shows only modded servers", action="store_true")
    argparser.add_argument("-spr", "--skip_private", help="Shows only public servers", action="store_true")
    argparser.add_argument("-spu", "--skip_public", help="Shows only password-protected servers", action="store_true")
    argparser.add_argument("-sf", "--skip_full", help="Shows only servers that have free space", action="store_true")
    argparser.parse_args()

    args = argparser.parse_args()

    if not args.nointro:
        print("Awaiting response from kag api...")

    servers = kag_servers()
    active_servers = alive_servers(servers)
    #Sort list of active servers by amount of players on them. More on beginning, less on the end
    active_servers.sort(key = players_amount, reverse = True)

    online = len(active_servers)
    players = player_amount(active_servers)

    print("There are currently {} active servers with {} players".format(online, players))

    if not args.nodetails:
        print("-------------\nServers info:")
        for x in active_servers:
            if args.skip_modded and x['usingMods']:
                continue
            if args.skip_vanilla and not x['usingMods']:
                continue
            if args.skip_private and x['password']:
                continue
            if args.skip_public and not x['password']:
                continue
            if args.skip_full and (len(x['playerList']) >= int(x['maxPlayers'])):
                continue
            server_info(x)

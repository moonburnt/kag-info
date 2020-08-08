##Script that prints info about active King Arthur's Gold servers into terminal. Inspired by bot used on official kag's discord, except it doesnt require discord to function

##Imports
import requests #to get json with data from kag's api
import json #to turn json into python's dictionary
import argparse #for launch arguments used to do various shenanigans with output
from re import sub as replace #to fix server's description and filter ping's output
from platform import system as os_name #to apply os-specific flag in server_ms
from subprocess import check_output #to get output of system's ping command in server_ms

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

def server_country(ip):
    '''Receives server IP (str), returns server's country (str) based on geojs.io data'''
    link = "https://get.geojs.io/v1/ip/country/"+ip+".json"
    response = requests.get(link, timeout = 30)
    pydic = json.loads(response.text)
    country = pydic["name"]
    return country

def server_ms(address):
    '''Receives server IP (str), returns ms to that server (str)'''
    #You have no idea how much salt did that crappy function produce
    if os_name() == 'Windows':
        flag = '-n'
    else:
        flag = '-c'

    command = "ping", flag, "1", address
    raw_answer = check_output(command) #calling system's ping command and getting output into variable
    x = replace('^.*time=', "", str(raw_answer)) #cutting output's intro before 'time='
    answer = replace(' ms.*', "", str(x)) #cutting everything after response time's int
    return answer

def players_amount(x):
    '''Receives dictionary entry with server's info. Returns amount of players on server'''
    return len(x.get('playerList'))

##Usage
if __name__ == "__main__":
    #argparse shenanigans
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-ni", "--nointro", help="Doesnt show info message about connecting to api", action="store_true")
    argparser.add_argument("-nd", "--nodetails", help="Only shows global online statistics, without detailed info about active servers", action="store_true")
    argparser.add_argument("-sm", "--skip_modded", help="Show only vanilla (non-modded) servers", action="store_true")
    argparser.add_argument("-sv", "--skip_vanilla", help="Show only modded servers", action="store_true")
    argparser.add_argument("-spr", "--skip_private", help="Show only public servers", action="store_true")
    argparser.add_argument("-spu", "--skip_public", help="Show only password-protected servers", action="store_true")
    argparser.add_argument("-sf", "--skip_full", help="Show only servers that have free space", action="store_true")
    argparser.add_argument("-hc", "--hide_country", help="Hide server's country", action="store_true")
    argparser.add_argument("-hn", "--hide_names", help="Hide list of players playing on server", action="store_true")
    argparser.add_argument("-hs", "--hide_spectators", help="Hide amount of spectators on server", action="store_true")
    argparser.add_argument("-hg", "--hide_gamemode", help="Hide server's game mode", action="store_true")
    argparser.add_argument("-hd", "--hide_description", help="Hide server's description", action="store_true")
    argparser.add_argument("-hp", "--hide_protection", help="Hide state of server's password protection", action="store_true")
    argparser.add_argument("-hm", "--hide_mods", help="Hide state of server's mods usage", action="store_true")
    argparser.add_argument("-hpi", "--hide_ping", help="Hide ping to server", action="store_true")
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
        for server in active_servers:
            name = server['name']
            raw_description = server['description'] #this one is kinda messy, coz it also contains info about used mods, and its all over the place. Blame kag api for that
            description = replace("\n\n.*", "", raw_description) #because of reason above, Im cleaning it up. MODS USED usually go after two empty lines, so I delet them and everything after
            ip = server['IPv4Address']
            if not args.hide_country: #I made it this way, because its request to third party server that may consume some time
                country = server_country(ip)
            if not args.hide_ping: #same as above
                ping = server_ms(ip)
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

            if args.skip_modded and using_mods:
                continue
            if args.skip_vanilla and not using_mods:
                continue
            if args.skip_private and password_protected:
                continue
            if args.skip_public and not password_protected:
                continue
            if args.skip_full and (players >= maxplayers):
                continue

            #Dis ugly as hell coz I found no other way to apply flags
            print("\nName: {}".format(name))
            if not args.hide_description:
                print("Description: {}".format(description))
            if not args.hide_country:
                print("Country: {}".format(country))
            print("Address: {}".format(kaglink))
            if not args.hide_ping:
                print("Ping: {} ms".format(ping))
            if not args.hide_protection:
                print("Requires Password: {}".format(password_protected))
            if not args.hide_gamemode:
                print("Gamemode: {}".format(gamemode))
            if not args.hide_mods:
                print("Using Mods: {}".format(using_mods))
            print("Players: {}".format(player_amount))
            if not args.hide_spectators:
                print("Spectators: {}".format(spectators))
            if not args.hide_names:
                print("Currently Playing: {}".format(nicknames))

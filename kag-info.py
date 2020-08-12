##Script that prints info about active King Arthur's Gold servers into terminal. Inspired by bot used on official kag's discord, except it doesnt require discord to function

##Imports
import requests #to get json with data from kag's api
import json #to turn json into python's dictionary
from re import sub as replace #to fix server's description and filter ping's output
from platform import system as os_name #to apply os-specific flag in server_ms
from subprocess import check_output #for server_ms

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

def total_player_amount(servers):
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

##Usage a.k.a "stuff that wont be imported by other scripts, if someone will decide to use this one as library"
if __name__ == "__main__":
    import argparse #for launch arguments used to do various shenanigans with output
    from time import sleep #for autoupdate
    from subprocess import call #for clean_terminal

    kagprefix = "kag://"

    ##Functions that serve no purpose outside of this script
    def clean_terminal():
        '''Cleans up terminal's output'''
        if os_name() == 'Windows':
            command = 'cls'
        else:
            command = 'clear'
        call(command)

    def players_amount(x):
        '''Receives dictionary entry with server's info. Returns amount of players on server'''
        return len(x.get('playerList'))

    def infomaker(serverlist):
        '''Receives list of servers, returns list of lists of descriptions based on argparse flags'''
        detailed_info = []
        for server in serverlist:
            server_info = []

            name = server['name']
            ip = server['IPv4Address']
            port = server['port']
            kaglink = kagprefix+str(ip)+":"+str(port)
            players = len(server['playerList'])
            maxplayers = server['maxPlayers']
            player_amount = str(players)+"/"+str(maxplayers)

            server_info.append("\nName: {}".format(name))
            if not args.hide_description:
                raw_description = server['description'] #this one is kinda messy, coz it also contains info about used mods, and its all over the place. Blame kag api for that
                description = replace("\n\n.*", "", raw_description) #because of reason above, Im cleaning it up. MODS USED usually go after two empty lines, so I delet them and everything after
                server_info.append("Description: {}".format(description))
            if not args.hide_country:
                country = server_country(ip)
                server_info.append("Country: {}".format(country))
            server_info.append("Address: {}".format(kaglink))
            if not args.hide_ping:
                ping = server_ms(ip)
                server_info.append("Ping: {} ms".format(ping))
            if not args.hide_protection:
                password_protected = server['password']
                server_info.append("Requires Password: {}".format(password_protected))
            if not args.hide_gamemode:
                gamemode = server['gameMode']
                server_info.append("Gamemode: {}".format(gamemode))
            if not args.hide_mods:
                using_mods = server['usingMods']
                server_info.append("Using Mods: {}".format(using_mods))
            server_info.append("Players: {}".format(player_amount))
            if not args.hide_spectators:
                spectators = server['spectatorPlayers']
                server_info.append("Spectators: {}".format(spectators))
            if not args.hide_names:
                nicknames = ', '.join(server['playerList'])
                server_info.append("Currently Playing: {}".format(nicknames))
            detailed_info.append(server_info)

        return detailed_info

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
    argparser.add_argument("-au", "--autoupdate", help="Autoupdate server list each 30 secs", action="store_true")
    args = argparser.parse_args()

    if not args.nointro:
        print("Awaiting response from kag api...")

    try:
        while True:
            servers = kag_servers()
            active_servers = alive_servers(servers)

            online = len(active_servers)
            players = total_player_amount(active_servers)

            if args.autoupdate:
                clean_terminal()

            if not args.nodetails:
                #filtering servers by flags
                filtered_servers = active_servers.copy()
                for server in active_servers:
                    if args.skip_modded and server['usingMods']:
                        filtered_servers.remove(server)
                    if args.skip_vanilla and not server['usingMods']:
                        filtered_servers.remove(server)
                    if args.skip_private and server['password']:
                        filtered_servers.remove(server)
                    if args.skip_public and not server['password']:
                        filtered_servers.remove(server)
                    if args.skip_full and (len(server['playerList']) >= int(server['maxPlayers'])):
                        filtered_servers.remove(server)

                #filter details by flags
                filtered_servers.sort(key = players_amount, reverse = True)
                details = infomaker(filtered_servers)

            #printing stuff
            print("There are currently {} active servers with {} players".format(online, players))
            if not args.nodetails and details:
                print("-------------\nServers info:")
                for x in details:
                    print(*x, sep="\n")
            if not args.autoupdate:
                break
            print("-------------\nStatics will update each 30 seconds. Press Ctrl+C to exit at any time")
            sleep(30)
    except KeyboardInterrupt:
        pass

### Copyright © 2020, moonburnt
###
### This program is free software. It comes without any warranty, to
### the extent permitted by applicable law. You can redistribute it
### and/or modify it under the terms of the Do What The Fuck You Want
### To Public License, Version 2, as published by Sam Hocevar.
### See the LICENSE file for more details.

### Script that prints info about active King Arthur's Gold servers into terminal. Inspired by bot used on official kag's discord, except it doesnt require discord to function

##Imports
import requests #to get json with data from kag's api
import json #to turn json into python's dictionary
from re import sub as replace #to fix server's description and filter ping's output
from platform import system as os_name #to apply os-specific flag in server_ms
from subprocess import check_output, call #for server_ms and cleaning up terminal
import argparse #for launch arguments used to do various shenanigans with output
from time import sleep #for autoupdate
from gc import collect #to manually remove old dictionaries from memory in automated mode

##Functions
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

def clean_terminal():
    '''Cleans up terminal's output'''
    if os_name() == 'Windows':
        command = 'cls'
    else:
        command = 'clear'
    call(command)

#keys for sorting
def sort_by_players(x):
    '''Sort received list by len of ['playerList'] in its dictionaries'''
    players = len(x['playerList'])
    return int(players)

def sort_by_ping(x):
    '''Sort received list by float of ['ping'] in its dictionaries'''
    return float(x['ping'])

def sort_by_country(x):
    '''Sort received list by str of ['country'] in its dictionaries'''
    return str(x['country'])

def sort_by_gamemode(x):
    '''Sort received list by str of ['gameMode'] in its dictionaries'''
    return str(x['gameMode'])

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
    argparser.add_argument("-au", "--autoupdate", help="Autoupdate server list each X seconds (not less than 10). Default = 10", nargs='?', const=10, type=int)
    argparser.add_argument("-sb", "--sortby", help="Sort servers in output by specified info", type=str, choices = ["more_players", "mp", "less_players", "lp", "ping", "ms", "country", "cn", "gamemode", "gm"])
    argparser.add_argument("-l", "--limit", help="Limit amount of servers in output by certain number", nargs='?', type=int)
    args = argparser.parse_args()

    #set lowest possible amount of time between requests to be 10
    if args.autoupdate:
        if args.autoupdate < 10:
            args.autoupdate = 10

    if not args.nointro:
        print("Awaiting response from kag api...")

    known_server_countries = []

    try:
        while True:
            try:
                servers = requests.get("https://api.kag2d.com/v1/game/1/servers?filters=[{%E2%80%9Cfield%E2%80%9D:%20%E2%80%9Ccurrent%E2%80%9D,%20%E2%80%9Cop%E2%80%9D:%20%E2%80%9Ceq%E2%80%9D,%20%E2%80%9Cvalue%E2%80%9D:%20true},%20{%E2%80%9Cfield%E2%80%9D:%20%E2%80%9CcurrentPlayers%E2%80%9D,%20%E2%80%9Cop%E2%80%9D:%20%E2%80%9Cge%E2%80%9D,%20%E2%80%9Cvalue%E2%80%9D:%201}]", timeout = 30)
                pydata = json.loads(servers.text)
                active_servers = pydata['serverList']
            except requests.exceptions.ReadTimeout:
                print("Couldnt connect to kag api: response took too long. Abort")
                break
            except requests.exceptions.ConnectionError:
                print("Couldnt connect to kag api: network unreachable. Abort")
                break

            online = len(active_servers)
            players = 0
            for x in active_servers:
                players += len(x['playerList'])

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

                for server in filtered_servers:
                    if not args.hide_description:
                        clean_description = replace("\n\n.*", "", server['description']) #MODS USED usually go after two empty lines, so I delet them and everything after
                        server['clean_description'] = clean_description
                    if not args.hide_country:
                        country = None
                        #checking if we already have data regarding that ip's country in memory
                        for item in known_server_countries:
                            if item['ip'] == server['IPv4Address']:
                                country = item['country']
                            else:
                                continue
                        if not country:
                            try:
                                country = server_country(server['IPv4Address'])
                                x = {}
                                x['ip'] = server['IPv4Address']
                                x['country'] = country
                                known_server_countries.append(x)
                            except:
                                country = "Unknown"
                        server['country'] = country
                    if not args.hide_ping:
                        try:
                            ping = server_ms(server['IPv4Address'])
                        except:
                            ping = "999"
                        server['ping'] = ping

                #sorting details by flags
                if args.sortby == "more_players" or args.sortby == "mp":
                    filtered_servers.sort(key = sort_by_players, reverse = True)
                elif args.sortby == "less_players" or args.sortby == "lp":
                    filtered_servers.sort(key = sort_by_players)
                elif (not args.hide_ping and args.sortby == "ping") or (not args.hide_ping and args.sortby == "ms"):
                    filtered_servers.sort(key = sort_by_ping)
                elif (not args.hide_country and args.sortby == "country") or (not args.hide_country and args.sortby == "cn"):
                    filtered_servers.sort(key = sort_by_country)
                elif (not args.hide_gamemode and args.sortby == "gamemode") or (not args.hide_gamemode and args.sortby == "gm"):
                    filtered_servers.sort(key = sort_by_gamemode)
                else:
                    pass

            #setting the amount of servers in output
            if not args.limit or (args.limit > len(filtered_servers)) or (args.limit < 0):
                args.limit = len(filtered_servers)

            if args.autoupdate:
                clean_terminal()

            #printing stuff
            print("There are currently {} active servers with {} players".format(online, players))
            if not args.nodetails and filtered_servers:
                print("-------------\nDetails:")
                for iteration, server in enumerate(filtered_servers):
                    if iteration == args.limit:
                        break
                    else:
                        print("\nName: {}".format(server['name']))
                        if not args.hide_description:
                            print("Description: {}".format(server['clean_description']))
                        if not args.hide_country:
                            print("Country: {}".format(server['country']))
                        print("Address: kag://{}:{}".format(server['IPv4Address'], server['port']))
                        if not args.hide_ping:
                            print("Ping: {} ms".format(server['ping']))
                        if not args.hide_protection:
                            print("Requires Password: {}".format(server['password']))
                        if not args.hide_gamemode:
                            print("Gamemode: {}".format(server['gameMode']))
                        if not args.hide_mods:
                            print("Using Mods: {}".format(server['usingMods']))
                        print("Players: {}/{}".format(len(server['playerList']), server['maxPlayers']))
                        if not args.hide_spectators:
                            print("Spectators: {}".format(server['spectatorPlayers']))
                        if not args.hide_names:
                            print("Currently Playing: {}".format((', '.join(server['playerList']))))
            if not args.autoupdate:
                break

            print("-------------\nStatistics will update each {} seconds. Press Ctrl+C to exit at any time".format(args.autoupdate))
            del servers, active_servers, filtered_servers, online, players
            collect()
            sleep(args.autoupdate)
    except KeyboardInterrupt:
        pass

#!/usr/bin/env python3

# RATT - Really Awful (Awesome?) Trigger Tool
# Copyright 2019 Khronion <khronion@gmail.com>
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with the software.  If not, see <http://www.gnu.org/licenses/>.

import urllib.request
import urllib.error
import shutil
import time
import gzip
import datetime
import ntplib
import colorama
import random
import socket
from pathlib import Path
from colorama import Fore, Back, Style
from bs4 import BeautifulSoup
from collections import OrderedDict

# Update these when a new revision is released
VERSION = "0.3"
RELEASEDATE = "18 June 2019"

# global API cooldown.
cooldown = 0.6

# update length variables
# set up later from atagait's update length resource
minor_length = None
major_length = None

# initialize colorama
colorama.init()


def message(text, kind="info"):
    kinds = {
        "none": ("", ""),
        "info": (Fore.GREEN + "[ INFO  ]" + Style.RESET_ALL, "[ INFO  ]"),
        "error": (Fore.RED + "[ ERROR ]" + Style.RESET_ALL, "[ ERROR ]"),
        "warn": (Fore.YELLOW + "[WARNING]" + Style.RESET_ALL, "[WARNING]"),
        "query": (Fore.CYAN + "[ QUERY ]" + Style.RESET_ALL, "[ QUERY ]"),
        "pad": ("          ", "          "),
        "go": (Back.RED + Fore.LIGHTWHITE_EX + "[!!GO!!!]" + Style.RESET_ALL, "[!!GO!!!]")
    }

    if kind in kinds.keys():
        prefix = kinds[kind]
    else:
        prefix = ""

    print(prefix[0] + " " + text)
    with open("debug_log.txt", "a") as out:
        out.write("{} {}\n".format(prefix[1], text))


def query(text):
    resp = input("[ ENTER ] " + text)
    with open("debug_log.txt", "a") as out:
        out.write("[ ENTER ] {}{}\n".format(text, resp))
    return resp.lower().replace(" ", "_").replace("\n", "")


def random_name():
    r = ['really',
         'rabid',
         'rax\'s',
         'rach\'s',
         'razorable',
         'ripe',
         'reeking',
         'retrograde',
         'reverse',
         'rotten',
         'rare']
    a = ['awesome',
         'awful',
         'atrocious',
         'adventurous',
         'advantageous',
         'asinine',
         'accurate',
         'arbitrary',
         'agonizing',
         'alternative']
    t = ['trigger',
         'trap',
         'trinket',
         'totem',
         'tail',
         'tale',
         'table',
         'teapot',
         'thot',
         'thought',
         'tricycle',
         'tool',
         'tangent']

    return "{} {} {} {}".format(
        random.choice(r).capitalize(),
        random.choice(a).capitalize(),
        random.choice(t).capitalize(),
        random.choice(t).capitalize()
    )

message("""
ooooooooo.         .o.       ooooooooooooo ooooooooooooo 
`888   `Y88.      .888.      8'   888   `8 8'   888   `8 
 888   .d88'     .8"888.          888           888      
 888ooo88P'     .8' `888.         888           888      
 888`88b.      .88ooo8888.        888           888      
 888  `88b.   .8'     `888.       888           888      
o888o  o888o o88o     o8888o     o888o         o888o     
                                                       """, kind="none")

intro_jokes = [
    "Learn to trigger, ya dingus!",
    "Hit CTRL-W to move to region. It's a breeze!",
    "RIP Violet Irises... We hardly knew ye...",
    "If Mercury is in retrograde, update may be slower than expected."
]

message(random_name(), kind="none")
message(random.choice(intro_jokes) + "\n", kind="none")
message("Version " + VERSION + " - Released " + RELEASEDATE + "\n", kind="none")

# Quick intro.
message("When you see [ ENTER ] on the screen, RATT is waiting for you.")
message("Read what the prompt says and type a response.")
query("Type anything and hit ENTER to continue. ")

message("RATT uses the NationStates API. If you run it at the same time")
message("as another API tool, you may hit the rate limit!")
query("Hit ENTER to continue. ")

# Get user nation and verify
while True:
    name = query("Please enter your nation name: ")
    try:
        # use NS API to check if the nation in question exists.
        headers = dict()
        headers['User-Agent'] = 'RATT/' + VERSION + ' (Developer=atagait@hotmail.com; User=' + name + ')'
        time.sleep(0.6)
        verification_request = urllib.request.Request('https://www.nationstates.net/cgi-bin/api.cgi?nation=' + name,
                                                      headers=headers)
        verification_response = urllib.request.urlopen(verification_request).read()
        break

    # If nation does not exist, print an error and repeat
    except urllib.error.HTTPError:
        message("Nation \"" + name + "\" does not exist.", kind="error")

# Print user nation information
verification_content = BeautifulSoup(verification_response, "lxml-xml")
message("Nation verified as " + verification_content.FULLNAME.string + ".")

# Choose major or minor update mode
message("Select the update mode RATT should run in. If this is set wrong,", kind="query")
message("triggers will fire too quickly or too slowly.", kind="query")
message("   1 - Major", kind="query")
message("   2 - Minor", kind="query")

with urllib.request.urlopen("https://atagait.com/python-bin/updateData.json") as Response:
    Data = json.loads(Response.read())
    minor_length = Data["minor"]["packer"] - Data["minor"]["banana"]
    major_length = Data["major"]["packer"] - Data["major"]["banana"]

major_update = None
while True:
    response = query("Update mode (1 or 2): ")
    if response in ("1", "2"):
        major_update = {"1": True, "2": False}[response]
        break

# Get trigger information
try:
    message("To disable trigger finding and instead monitor a listed region,", kind="query")
    message("set trigger interval to 0.", kind="query")
    trigger_length = int(query("What trigger interval should RATT use? "))
    if trigger_length > 12:
        message("Long triggers may be unreliable.", kind="warn")
except ValueError:
    message("Defaulting to 8 seconds.")
    trigger_length = 8

# Download daily dump
dump_path = Path('./regions.xml.gz')
if dump_path.exists() and dump_path.is_file():
    message("RATT can update the region dump, if the current one is too old.", kind="query")
    message("An old version will lead to inaccurate results.", kind="query")
    if query("Update region dump? (Y/N) ") == "y":
        message("Downloading latest region dump.")
        with urllib.request.urlopen("https://www.nationstates.net/pages/regions.xml.gz") as response, \
                open("./regions.xml.gz", 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
            message("Region dump updated!")
    else:
        message("Using existing region dump.")
else:
    message("No region dump found. Downloading latest version.")
    with urllib.request.urlopen("https://www.nationstates.net/pages/regions.xml.gz") as response, \
            open("./regions.xml.gz", 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
        message("Region dump updated.")

message("Now loading. This could take over a minute, depending on your system.")

# ungzip and feed to bs4
decompressed_xml = gzip.GzipFile(filename="./regions.xml.gz")
region_dump = BeautifulSoup(decompressed_xml.read(), "lxml-xml")

# create lookup dictionary and table
# region_dict has format {region_name: (lastupdate, index)}
# lookup_list has tuples of format (region_name, lastupdate)
# After we find our target_region, we go to its lookup_list index and walk backward by one until we find a region that
# is far away enough. Why? Because you can't jump to an arbitrary index in an OrderedDict.
region_dict = OrderedDict()
lookup_list = []
index = 0

for region in region_dump.find_all("REGION"):
    name = region.NAME.string.lower().replace(" ", "_")
    lastupdate = int(region.LASTUPDATE.string)
    region_dict[name] = (lastupdate, index)
    lookup_list.append((name, lastupdate))
    index += 1

# MAIN LOOP

message("RATT initialization complete.")
ntp_client = ntplib.NTPClient()
while True:
    # select target
    target_region = query("Target Region: ")
    trigger_region = None
    valid = False
    # look for a trigger.
    try:
        search_base = region_dict[target_region][0]  # region update time
        search_index = region_dict[target_region][1]  # index to check
        # print("search_index", search_index, "search_base", search_base)
        while not valid:
            if not major_update:
                time_factor = minor_length / major_length)  # ratio of minor update to major update
            else:
                time_factor = 1
            # print("lookup_list[search_index][1]", lookup_list[search_index][1])
            # print("search_base - lookup_list[search_index][1] ", search_base - lookup_list[search_index][1])
            if search_base - lookup_list[search_index][1] >= trigger_length / time_factor:  # if the target is far enough back...
                trigger_time = lookup_list[search_index][1]
                trigger_region = lookup_list[search_index][0]  # store its name.
                valid = True
            search_index -= 1  # walk back one.
    except IndexError:
        message("{} is too early in update. No valid triggers found.".format(target_region), kind="error")
    except KeyError:
        # region not in region dump, cannot be targeted.
        message(target_region + " could not be found in region dump. Aborting.", kind="error")
        message("If this region exists, try restarting RATT and update the region dump.", kind="error")

    # Now that the trigger has been identified, start tracking it for updates. This part won't fire if the region wasn't
    # found in the dump
    while valid:
        # check to see if the trigger has gone off. If it has, alert the user the trigger has already gone off.
        try:
            time.sleep(cooldown)  # Sleep at least 0.6 seconds for API compliance..
            target_req = urllib.request.Request(
                'https://www.nationstates.net/cgi-bin/api.cgi?region=' + trigger_region +
                "&q=lastupdate", headers=headers)
            target_resp = urllib.request.urlopen(target_req).read()
            target_cont = BeautifulSoup(target_resp, "lxml-xml")
            lastupdate = int(target_cont.LASTUPDATE.string)

            # only store time if the last update didn't happen in the current update. If the LASTUPDATE happened within
            # 3 hours of the current time, we can be pretty certain that it updated during the current update. The
            # length of time used to filter needs to be greater than the length of major update but shorter than the
            # time between the start of major and minor update (12 hours).
            try:
                current_time = int(ntp_client.request('pool.ntp.org').orig_time)
            except socket.timeout:
                try:
                    current_time = int(ntp_client.request('time.nist.gov').orig_time)

                # If no authoritative time server can be found, KATT will default to the system time and warn the user
                # that an inaccurate clock can cause problems.
                except ntplib.NTPException:
                    message("Could not connect to external time server.", kind="warn")
                    message("RATT may hang if computer time is inaccurate.", kind="warn")
                    message("If this happens, restart RATT and skip to next target.", kind="warn")
                    current_time = int(time.time())
            message("Trigger region {} identified with trigger length {}s".format(trigger_region, search_base - trigger_time))
            if current_time - lastupdate < 7200:
                message("TRIGGER REGION ALREADY UPDATED!", kind="go")
                break
        except urllib.error.HTTPError:
            message("Trigger could not be identified. Aborting.", kind="error")

        # start monitoring the trigger
        while True:
            updates = 0
            try:
                # get LASTUPDATE SHARD
                time.sleep(cooldown)  # Sleep at least 0.6 seconds for API compliance.
                target_req = urllib.request.Request(
                    'https://www.nationstates.net/cgi-bin/api.cgi?region=' + str(trigger_region) +
                    "&q=lastupdate", headers=headers)
                target_resp = urllib.request.urlopen(target_req).read()
                target_cont = BeautifulSoup(target_resp, "lxml-xml")
                querytime = int(target_cont.LASTUPDATE.string)

                # if LASTUPDATE is different from what we fetched during initialization, then the region has updated.
                # KATT will immediately print an alert.
                if lastupdate != querytime:
                    message(datetime.datetime.now().strftime('%H:%M:%S ') + str(trigger_region) + " has updated!")
                    print("\t" + Back.RED + Fore.LIGHTWHITE_EX + "!!! UPDATE EVENT DETECTED !!!" + Style.RESET_ALL)
                    time.sleep(5)
                    break
                else:
                    # If no update is detected, KATT will print a status update. A status update is not printed on every
                    # API query. The interval between updates is set during initialization.
                    if updates % 5 == 0:
                        message(
                            datetime.datetime.now().strftime('%H:%M:%S') + " Current target: {} ({}s Trigger: {})".format(
                                target_region, search_base - trigger_time, trigger_region))
                    updates += 1

            # If KATT doesn't successfully connect to the API server, it will catch the error, wait 3 seconds, and then
            # continue.
            except urllib.error.URLError:
                message(datetime.datetime.now().strftime(
                    '%H:%M:%S') + " Could not connect to NationStates. Retrying in 3 seconds...", kind="warn")
                time.sleep(3)
        break
    if query("Continue? (Y/N) ") == 'n':
        message("Exiting.")
        break

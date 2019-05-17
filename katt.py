#!/usr/bin/env python3

# KATT - Khron and Atagait's Triggering Tool
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
#

import urllib.request
import urllib.error
import time
import datetime
import ntplib
import colorama
import re
from colorama import Fore, Back, Style
from bs4 import BeautifulSoup

# Update these when a new revision is released
VERSION = "0.2"
RELEASEDATE = "21 April 2019"


def sanitize(text):
    """
    Remove capital letters and convert spaces to underscores

    :param text: String to sanitize
    :return: Sanitized string
    """
    return text.lower().replace(" ", "_").replace("\n", "")


def log_message(text):
    """
    Direct a printed message to the debug log as well. Rejects unexpected characters that prevent writing to the debug
    log in text mode.

    :param text: String to print and log
    """
    with open("debug_log.txt", "a") as out:
        print(text)
        # strip out colorama control codes. This doesn't work perfectly, but it keeps ascii writes from crashing
        out.write(re.sub(r"[^a-zA-Z0-9'_\[\]:]+", ' ', text) + "\n")


def log_input(text):
    """
    Direct a query message and response to the debug log as well. Rejects unexpected characters that cannot be written
    to the debug log in text mode.

    :param text: Query to print and log
    :return: Query response
    """
    with open("debug_log.txt", "a") as out:
        response = input(text)
        # strip out colorama control codes. This doesn't work perfectly, but it keeps ascii writes from crashing
        out.write(re.sub(r"[^a-zA-Z0-9'_\[\]:]+", ' ', text) + response + "\n")
        return response


# define color codes for terminal text
nfo = Fore.GREEN + "[ INFO  ]" + Style.RESET_ALL + " "  # info message (no action needed)
err = Fore.RED + "[ ERROR ]" + Style.RESET_ALL + " "  # error message (fatal/user action needed)
warn = Fore.YELLOW + "[WARNING]" + Style.RESET_ALL + " "  # warning message (no action needed)
query = Fore.CYAN + "[ QUERY ]" + Style.RESET_ALL + " "  # user hints for input
inp = "[ ENTER ] "  # preface all input() messages
pad = "          "  # padding for multiline messages
pending = Fore.MAGENTA + "[WAITING]" + Style.RESET_ALL + " "  # info text when waiting for trigger
hit = Back.RED + Fore.LIGHTWHITE_EX + "[UPDATE!]" + Style.RESET_ALL + " "  # hit message

# initialize colorama
colorama.init()

# ASCII art courtesy of Atagait
log_message(Fore.RED + "\n██╗  ██╗ █████╗ ████████╗████████╗")
log_message("██║ ██╔╝██╔══██╗╚══██╔══╝╚══██╔══╝")
log_message("█████╔╝ ███████║   ██║      ██║   ")
log_message("██╔═██╗ ██╔══██║   ██║      ██║   ")
log_message("██║  ██╗██║  ██║   ██║      ██║   ")
log_message("╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝      ╚═╝   \n" + Style.RESET_ALL)
log_message("        |\\___/|")
log_message("        )     (  ")
log_message("       =\\     /=")
log_message("         )===(   ")
log_message("        /     \\")
log_message("        |     |")
log_message("       /       \\")
log_message("       \\       /")
log_message("_/\\_/\\_/\\__  _/_/\\_/\\_/\\_/\\_/\\_/\\_")
log_message("|  |  |  |( (  |  |  |  |  |  |  |")
log_message("|  |  |  | ) ) |  |  |  |  |  |  |")
log_message("|  |  |  |(_(  |  |  |  |  |  |  |")
log_message("|  |  |  |  |  |  |  |  |  |  |  |")
log_message("|  |  |  |  |  |  |  |  |  |  |  |")
log_message("\\Khron and Atagait's Trigger Tool/")
log_message("Version " + VERSION + " - Released " + RELEASEDATE + "\n")

# Quick tutorial for users who aren't use to using a console.
log_message(nfo + "Whenever you see " + inp + "type your response and hit enter.")
log_input(inp + "Type anything and hit ENTER to continue.")

# Get user nation and verify
while True:
    name = sanitize(log_input(inp + "Please enter your nation name: "))
    try:
        # use NS API to check if the nation in question exists.
        headers = dict()
        headers['User-Agent'] = 'KATT/' + VERSION + ' (Developer=khronion@gmail.com; User=' + name + ')'
        time.sleep(0.6)
        verification_request = urllib.request.Request('https://www.nationstates.net/cgi-bin/api.cgi?nation=' + name,
                                                      headers=headers)
        verification_response = urllib.request.urlopen(verification_request).read()
        break

    # If nation does not exist, print an error and repeat
    except urllib.error.HTTPError:
        log_message(err + "Nation \"" + name + "\" does not exist.")

# Print user nation information
verification_content = BeautifulSoup(verification_response, "lxml-xml")
log_message(nfo + "Nation verified as " + verification_content.FULLNAME.string + ".")

# Set how often KATT should print a status update. This is just a matter of user preference.
try:
    log_message(query + "How often should KATT display a status update? The default is every\n" +
          pad + "5 API calls.")
    interval = int(log_input(inp + "Status update interval (leave blank if you don't know): "))
    if interval < 1:
        interval = 1
        print(warn + "Invalid option. Using minimum value of 1 API call between status\n" +
              pad + "updates")
    else:
        log_message(nfo + "Using user-set value of " + str(interval) + " API call(s) between\n" +
              pad + "updates.")
except ValueError:
    log_message(nfo + "Using default value of 5 API calls between status updates.")
    interval = 5

# Currently we allow the user to set an API call speed, but maybe it makes more sense not to
# make this user-settable.
try:
    log_message(query + "How often should KATT call the NationStates API? The default is every \n" +
          pad + "0.6 seconds. If this is too high, your triggers will be inaccurate.")
    cooldown = float(log_input(inp + "API Call Speed (leave blank if you don't know): "))
    if cooldown < 0.6:
        cooldown = 0.6
        log_message(warn + "Invalid option. Using minimum value of 0.6 seconds between API calls.")
    elif cooldown > 1:
        log_message(warn + "Using more than 1 second between API calls may lead to inaccurate\n" +
              pad + "triggers.")
    else:
        log_message(nfo + "Using user-set value of " + str(cooldown) + " seconds between API calls.")
except ValueError:
    log_message(nfo + "Using default value of 0.6 seconds between API calls.")
    cooldown = 0.6

# Load trigger nation list
while True:
    try:
        log_message(nfo + "Loading trigger nations from trigger_list.txt")
        with open("./trigger_list.txt", "r") as trigger_file:
            trigger_names = trigger_file.readlines()
        if len(trigger_names) > 0:
            break

        # If there are no triggers in trigger_list.txt, KATT will retry loading after prompting the user to add triggers
        else:
            log_message(err + "No trigger nations were found in trigger_list.txt.")
            log_input(inp + "Hit ENTER to reload after adding trigger nations.")

    # If trigger_list.txt doesn't exist, KATT will create it and let the user try again
    except FileNotFoundError:
        log_message(err + " trigger_list.txt was not found.")
        open("./trigger_list.txt", "a").close()
        log_message(err + "A blank trigger_list.txt was created in the current directory.")
        log_message(pad + "Enter trigger regions in this file, one per line.")
        log_input(inp + "Hit ENTER to load after adding trigger nations.")

# Verify triggers and create a dictionary of valid triggers
triggers = dict()

# KATT compares LASTUPDATE to the current world time to determine if a region has already updated during the current
# update. Since not all computers have accurate time and a relatively small error can cause KATT to hang waiting for
# an update that won't happen for 12 hours, KATT tries to get the worldtime from an authoritative time server run by
# NTP or NIST.
ntp_client = ntplib.NTPClient()
try:
    current_time = int(ntp_client.request('pool.ntp.org').orig_time)
except ntplib.NTPException:
    try:
        current_time = int(ntp_client.request('time.nist.org').orig_time)

    # If no authoritative time server can be found, KATT will default to the system time and warn the user that an
    # inaccurate clock can cause problems.
    except ntplib.NTPException:
        log_message(warn + "Could not connect to remote time server. Using system time.")
        log_message(pad + "If system time is inaccurate, KATT could hang mid-update and")
        log_message(pad + "miss trigger regions. If KATT does not detect a trigger,")
        log_message(pad + "close it and restart.")
        current_time = int(time.time())

# Now that we have the world time and a list of regions, query the API for LASTUPDATE times and remove any that have
# already updated during the current update.
for trigger in trigger_names:
    if trigger[0] != '#':
        try:
            time.sleep(cooldown)  # Sleep at least 0.6 seconds for API compliance..
            target_req = urllib.request.Request(
                'https://www.nationstates.net/cgi-bin/api.cgi?region=' + sanitize(trigger) +
                "&q=lastupdate", headers=headers)
            target_resp = urllib.request.urlopen(target_req).read()
            target_cont = BeautifulSoup(target_resp, "lxml-xml")
            lastupdate = int(target_cont.LASTUPDATE.string)

            # only store time if the last update didn't happen in the current update. If the LASTUPDATE happened within
            # 3 hours of the current time, we can be pretty certain that it updated during the current update. The
            # length of time used to filter needs to be greater than the length of major update but shorter than the
            # time between the start of major and minor update (12 hours).
            if current_time - lastupdate > 7200:
                # We use times as the key to easily sort by update order.
                log_message(nfo + sanitize(trigger) + " loaded (LASTUPDATE=" + str(lastupdate) + ")")
                triggers[lastupdate] = sanitize(trigger)
            else:
                log_message(warn + sanitize(trigger) + " has already updated. Removing from trigger list.")

        # If the API throws an error, then we know the listed region doesn't actually exist and can be removed.
        except urllib.error.HTTPError:
            log_message(warn + sanitize(trigger) + " is not a valid region. Removing from trigger list.")

# Now we'll sort the list of triggers by update time so track them in update order, starting with the first region
# that has yet to update.
sorted_trigger_keys = sorted(triggers)

for trigger in sorted_trigger_keys:
    updates = 0
    while True:
        try:
            # get LASTUPDATE SHARD
            time.sleep(cooldown)  # Sleep at least 0.6 seconds for API compliance.
            target_req = urllib.request.Request(
                'https://www.nationstates.net/cgi-bin/api.cgi?region=' + str(triggers[trigger]) +
                "&q=lastupdate", headers=headers)
            target_resp = urllib.request.urlopen(target_req).read()
            target_cont = BeautifulSoup(target_resp, "lxml-xml")
            lastupdate = int(target_cont.LASTUPDATE.string)

            # if LASTUPDATE is different from what we fetched during initialization, then the region has updated.
            # KATT will immediately print an alert.
            if lastupdate != trigger:
                log_message(datetime.datetime.now().strftime(hit + '%H:%M:%S ') + str(triggers[trigger]) + " has updated!")
                log_message("\t" + Back.RED + Fore.LIGHTWHITE_EX + "!!! UPDATE EVENT DETECTED !!!" + Style.RESET_ALL)
                time.sleep(5)
                break
            else:
                # If no update is detected, KATT will print a status update. A status update is not printed on every
                # API query. The interval between updates is set during initialization.
                if updates % interval == 0:
                    log_message(
                        datetime.datetime.now().strftime(pending + '%H:%M:%S') + " Waiting for next trigger region: " +
                        triggers[
                            trigger])
                updates += 1

        # If KATT doesn't successfully connect to the API server, it will catch the error, wait 3 seconds, and then
        # continue.
        except urllib.error.URLError:
            log_message(datetime.datetime.now().strftime(
                warn + '%H:%M:%S') + " Could not connect to NationStates. Retrying in 3 seconds...")
            time.sleep(3)

log_message(nfo + "No more targets left.")
log_input(inp + "Hit ENTER to terminate.")

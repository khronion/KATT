# KATT and RATT

*Khron and Atagait's Trigger Tool* and the *Really Awful Trigger Tool*

## About

KATT is a simple script that takes a list of NationStates regions, sorts them by update order, and informs the user when
the game API reports they have updated.

RATT is a Python script that asks a user for a region, finds a suitable trigger region based on a preset trigger length, and monitors the trigger region for an update event.

RATT-generated triggers are identical to those made using a Spyglass sheet. RATT uses the `regions.xml.gz` API dump to automate the process of looking through a sheet to find a region that updates a certain number of seconds before the target. As a result, it its triggers are subject to a certain degree of error. If accuracy is critical, KATT or Deadeye should be used instead, in conjunction with a manual trigger, preferrably with several backup triggers.

## Running KATT

KATT requires Python 3 with [Colorama](https://pypi.org/project/colorama/), [NTPLib](https://pypi.org/project/ntplib/),
[BeautifulSoup4](https://pypi.org/project/beautifulsoup4/), and [LXML](https://pypi.org/project/lxml/) installed. These
packages may all be installed using `pip`.

```
$ pip install colorama ntplib beautifulsoup4 lxml
$ python KATT.py
```

A windows version is available that is compiled using PyInstaller.

A `trigger_list.txt` file containing one trigger region per line should be placed in same directory that `KATT.py` is
run from. If this file does not exist at run time, KATT will create it and exit.

Once KATT is executed, it will ask the user to provide an identifying user nation name. After it has verified that this
nation exists, KATT will index the trigger list, discard recently updated trigger regions, and monitor them one by one.
As each subsequent region updates, it will print a message to the screen before proceeding to the next region on the
list, until all regions have updated.

If a region has already updated during the current update, KATT will detect this and remove it from the list.

## Running RATT

RATT has the same requirements as KATT.

When started, RATT will ask the user to provide a valid nation and ask the user to specify whether it is being used during a major or minor update. It will then ask the user to set a trigger length. Using 0 as the trigger length disables trigger finding and causes RATT to function similar to KATT or Deadeye. After that, it will download the latest `regions.xml.gz` API dump, or offer to update one if it already exists. This can take over a minute on older systems with limited processor power.

RATT will then ask the user to enter a target region. It will automatically find a trigger region and begin tracking it until an update event is detected. When an update event is detected, it prints a notification to the screen before asking the user to select a new target. If the target region has updated in the last two hours, RATT will warn the user instead.

## Acknowledgments

The following people provided key contributions during the initial development process:

* Atagait created the ASCII art displayed when KATT runs
* Teazle found a bug in the update failsafe logic
* Souls provided feedback on program design and user interface

The following people also helped review and test KATT:

* Azaelai provided initial usability review and field testing
* Felt provided additional feature feedback
* Chris got triggered during the review process (go lie down before you hurt yourself Chris)
* Jay offered nice sentiments during the initial review

## Disclaimer

The software is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

Any individual using a script-based NationStates API tool is responsible for ensuring it complies with the latest
version of the [API Terms of Use](https://www.nationstates.net/pages/api.html#terms). KATT is designed to comply with
these rules, including the rate limit, as of April 21, 2019, under reasonable use conditions, but the authors are not
responsible for any unintended or erroneous program behavior that breaks these rules.

Never run more than one program that uses the NationStates API at once. Doing so will likely cause your IP address to
exceed the API rate limit, which will in turn cause both programs to fail.

"""
This module provides a way to import data from the Habit List iPhone
application (http://habitlist.com/) into Day One Journal
(http://dayoneapp.com/) entries.

To use this module you must first do a manual export of your data from Habit
list.  This can be done by the following:
    - Open Habit List iPhone app
    - Click the 'gear' icon for settings at the bottom of the main 'Today' view
    - Choose the 'Export Data' option
    - E-mail the data to yourself
    - Copy and paste the e-mail contents into a file of your choosing
        - You can choose to optionally remove the first few lines of the e-mail
          that are not JSON data, everything up to the first '[' character.
        - Again, this is optional because this module will attempt to ignore
          any non-JSON data at the START of a file.
        - Remember to remove the 'sent from iPhone' line at the end of your
          e-mail.  This will cause the script to NOT process the JSON data.

At this point, you are ready to do the actual conversion from JSON to Day One
entires.  So, you should check all the 'settings' in this module for things you
would like to change:
    - HEADER_FOR_DAY_ONE_ENTRIES
    - DAYONE_ENTRIES
    - ENTRY_TEMPLATE

Next, you can run this module with your exported JSON data as an argument like
so:
    - python services/habit_list.py -f habit_list_data.json -t

Also, it's encouraged to run this with the '-t' option first so that all your
Day One entires will be created in a local directory called 'test.'  This will
allow you to inspect the conversion.  You can manually copy a few select
entries into your Day One 'entries/' folder to ensure you approve of the
formatting and can easily make any formatting adjustments.  Then, you can run
this module again without the '-t' to fully import Habit List entries into Day
One.
"""

import argparse
import collections
from datetime import datetime
import json
import os
import re
import uuid

from dayonetools.services import convert_to_dayone_date_string

DAYONE_ENTRIES = '/Users/durden/Dropbox/Apps/Day One/Journal.dayone/entries/'

# This text will be inserted into the first line of all entries created, set to
# '' to remove this completely.
HEADER_FOR_DAYONE_ENTRIES = 'Habit List entry'

# Note the strange lack of indentation on the {entry_text} b/c day one will
# display special formatting to text that is indented, which we want to avoid.
ENTRY_TEMPLATE = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Creation Date</key>
    <date>{date}</date>
    <key>Entry Text</key>
    <string> {entry_title}
<![CDATA[
{habits}]]>
#habits #habit_list
    </string>
    <key>Starred</key>
    <false/>
    <key>Tags</key>
    <array>
        <string>habits</string>
        <string>habit_list</string>
    </array>
    <key>UUID</key>
    <string>{uuid_str}</string>
</dict>
</plist>
"""


def _parse_args():
    """Parse sys.argv arguments"""

    parser = argparse.ArgumentParser(
                               description='Export Habit List data to Day One')

    parser.add_argument('-f', '--file', action='store',
                        dest='input_file', required=True,
                        help='JSON file to import from')

    parser.add_argument('-v', '--verbose', default=False, action='store_true',
                        dest='verbose', required=False,
                        help='Verbose debugging information')

    parser.add_argument('-t', '--test', default=False, action='store_true',
                        dest='test', required=False,
                        help=('Test import by creating Day one files in local '
                             'directory for inspect'))

    def _datetime(str_):
        """Convert date string in YYYY-MM-DD format to datetime object"""

        if not str_:
            return None

        try:
            date = datetime.strptime(str_, '%Y-%m-%d')
        except ValueError:
            msg = 'Invalid date format, should be YYYY-MM-DD'
            raise argparse.ArgumentTypeError(msg)

        return date

    parser.add_argument('-s', '--since', type=_datetime,
                        help=('Only process entries starting with YYYY-MM-DD '
                              'and newer'))

    return vars(parser.parse_args())


def _habits_to_markdown(habits):
    """Create markdown list of habits"""

    # FIXME: This is inefficient but not sure of a good way to use join since
    # we want to add a chacter to the beginning and end of each string in list.
    markdown = ''

    for habit in habits:
        markdown += '- %s\n' % (habit)

    return markdown


def _create_habitlist_entry(directory, date, habits, verbose):
    """Create day one file entry for given habits, date pair"""

    # Create unique uuid without any specific machine information
    # (uuid() vs.  uuid()) and strip any '-' characters to be
    # consistent with dayone format.
    uuid_str = re.sub('-', '', str(uuid.uuid4()))

    file_name = '%s.doentry' % (uuid_str)
    full_file_name = os.path.join(directory, file_name)

    date = convert_to_dayone_date_string(date)
    habits = _habits_to_markdown(habits)

    entry = {'entry_title': HEADER_FOR_DAYONE_ENTRIES,
              'habits': habits,'date': date, 'uuid_str': uuid_str}

    with open(full_file_name, 'w') as file_obj:
        text = ENTRY_TEMPLATE.format(**entry)
        file_obj.write(text)

    if verbose:
        print 'Created entry for %s: %s' % (date, file_name)


def main():
    args = _parse_args()
    user_specified_date = args['since']

    if args['test']:
        directory = './test'
        try:
            os.mkdir(directory)
        except OSError as err:
            print 'Warning: %s' % (err)
    else:
        directory = DAYONE_ENTRIES

    with open(args['input_file'], 'r') as file_obj:
        junk = file_obj.readline()
        junk = file_obj.readline()
        junk = file_obj.readline()

        # FIXME: For my sample this is about 27kb of memory
        _json = file_obj.read()

    strip_date_from_time = lambda _date: _date.split()[0]

    # FIXME: This is 48KB in memory..
    habits = collections.defaultdict(list)
    for habit in json.loads(_json):
        name = habit['name']
        for dt in habit['completed']:
            date = strip_date_from_time(dt)
            curr_dtime_obj = datetime.strptime(date, '%Y-%m-%d')

            if user_specified_date is None or (
                                    curr_dtime_obj >= user_specified_date):
                habits[date].append(name)

    for date, habits in habits.iteritems():
        _create_habitlist_entry(directory, date, habits, args['verbose'])

        # Dict: habits[yyyy-mm-dd] = ['run', 'lift weights', ...]
        # Read JSON into memory
        # Go through each habit
        #   Go thru each date in 'completed'
        #   Strip off time, just get yyyy-mm-dd
        #   Insert date into dict if needed
        #   Append to date's list with this habits name
        # Go thru all dates (keys of dict)
        # Create entry for each date with a list of the habits for that day
        #   - Run
        #   - Lift weights
        #   Append to dict


if __name__ == '__main__':
    main()

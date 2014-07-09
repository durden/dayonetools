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
        - Remove the 'sent from iPhone' line at the end of your e-mail.  This
          will cause the script to NOT process the JSON data.
        - DO NOT REMOVE THE LAST TWO EMPTY LINES OF THE E-MAIL. WE CURRENTLY
          HAVE A BUG THAT EXPECTS THESE LINES.
        - You can choose to optionally remove the first few lines of the e-mail
          that are not JSON data, everything up to the first '[' character.
        - Again, this is optional because this module will attempt to ignore
          any non-JSON data at the START of a file.

At this point, you are ready to do the actual conversion from JSON to Day One
entires.  So, you should check all the 'settings' in this module for things you
would like to change:
    - HEADER_FOR_DAY_ONE_ENTRIES
    - DAYONE_ENTRIES
    - ENTRY_TEMPLATE
    - TIMEZONE
        - Make sure to choose the timezone of your iPhone because the Habit
          List app stores all timezones in UTC and you'll want to convert this
          to the timezone your iPhone used at the time you completed the habit.
          This will ensure your Day One entries match the time you completed
          the task and also prevent a habit from showing up more than once per
          day which can happen with UTC time if you complete a habit late in
          one day and early in the next, etc.
        - You can find a list of available timezone strings here:
            - http://en.wikipedia.org/wiki/List_of_tz_database_time_zones

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

from dateutil import tz

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

TIMEZONE = 'America/Chicago'


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

        return date.replace(tzinfo=_user_time_zone())

    parser.add_argument('-s', '--since', type=_datetime,
                        help=('Only process entries starting with YYYY-MM-DD '
                              'and newer'))

    return vars(parser.parse_args())


def _user_time_zone():
    """Get default timezone for user"""

    try:
        return tz.gettz(TIMEZONE)
    except Exception as err:
        print 'Failed getting timezone, check your TIMEZONE variable'
        raise


def _user_time_zone_date(dt, user_time_zone, utc_time_zone):
    """
    Convert given datetime string into a yyyy-mm-dd string taking into
    account the user time zone

    Keep in mind that this conversion might change the actual day if the
    habit was entered 'early' or 'late' in the day.  This is correct because
    the user entered the habit in their own timezone, but the app stores this
    internally (and exports) in utc.  So, here we are effectively converting
    the time back to when the user actually entered it, based on the timezone
    the user claims they were in.
    """

    # We know habit list stores in UTC so don't need the timezone info
    dt = dt.split('+')[0].strip()
    dtime_obj = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')

    # Tell native datetime object we are using UTC, then we need to convert
    # that UTC time into the user's timezone BEFORE stripping off the time
    # to make sure the year, month, and date take into account timezone
    # differences.

    utc = dtime_obj.replace(tzinfo=utc_time_zone)
    return utc.astimezone(user_time_zone)


def _habits_to_markdown(habits):
    """Create markdown list of habits"""

    # FIXME: This is inefficient but not sure of a good way to use join since
    # we want to add a chacter to the beginning and end of each string in list.
    markdown = ''

    for habit, dt_obj in habits:
        markdown += '- [%02d:%02d] %s\n' % (dt_obj.hour, dt_obj.minute, habit)

    return markdown



def create_habitlist_entry(directory, day_str, habits, verbose):
    """Create day one file entry for given habits, date pair"""

    # Create unique uuid without any specific machine information
    # (uuid() vs.  uuid()) and strip any '-' characters to be
    # consistent with dayone format.
    uuid_str = re.sub('-', '', str(uuid.uuid4()))

    file_name = '%s.doentry' % (uuid_str)
    full_file_name = os.path.join(directory, file_name)

    date = convert_to_dayone_date_string(day_str)
    habits = _habits_to_markdown(habits)

    entry = {'entry_title': HEADER_FOR_DAYONE_ENTRIES,
              'habits': habits,'date': date, 'uuid_str': uuid_str}

    with open(full_file_name, 'w') as file_obj:
        text = ENTRY_TEMPLATE.format(**entry)
        file_obj.write(text)

    if verbose:
        print 'Created entry for %s: %s' % (date, file_name)


def parse_habits_file(filename, start_date=None):
    """
    Parse habits json file and return dict of data organized by day

    start_date can be a datetime object used only to return habits that were
    started on or after start_date
    """

    with open(filename, 'r') as file_obj:
        # FIXME: This expects 3 lines of junk at the beginning of the file, but
        # we could just read until we find '[' and ignore up until that point.
        junk = file_obj.readline()
        junk = file_obj.readline()
        junk = file_obj.readline()

        # FIXME: For my sample this is about 27kb of memory
        _json = file_obj.read()

    # FIXME: Downside here is that we assume the user was in the same timezone
    # for every habit.  However, it's possible that some of the habits were
    # entered while the user was traveling in a different timezone, etc.
    iphone_time_zone = _user_time_zone()
    utc_time_zone = tz.gettz('UTC')

    # Use a set b/c we can only do each habit once a day
    habits = collections.defaultdict(set)

    # FIXME: Maybe optimize this to not hold it all in memory

    # We have to parse all json and return it b/c the data is organized by
    # habit and we need it organized by date. So, we can't use a generator or
    # anything to yield values as they come b/c we won't know if we've parsed
    # the entire day until all JSON is parsed.

    # FIXME: Should have something to catch ValueError exceptions around this
    # so we can show the line with the error if something is wrong.
    for habit in json.loads(_json):
        name = habit['name']

        for dt in habit['completed']:
            dt_obj = _user_time_zone_date(dt, iphone_time_zone, utc_time_zone)
            if start_date is None or dt_obj >= start_date:
                # Habits will be organized by day then each one will have it's
                # own time.
                day_str = dt_obj.strftime('%Y-%m-%d')
                habits[day_str].add((name, dt_obj))

    return habits


def main():
    args = _parse_args()

    if args['test']:
        directory = './test'
        try:
            os.mkdir(directory)
        except OSError as err:
            print 'Warning: %s' % (err)
    else:
        directory = DAYONE_ENTRIES

    habits = parse_habits_file(args['input_file'], args['since'])

    for day_str, days_habits in habits.iteritems():
        create_habitlist_entry(directory, day_str, days_habits, args['verbose'])


if __name__ == '__main__':
    main()

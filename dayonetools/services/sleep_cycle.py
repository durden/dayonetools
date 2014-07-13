"""
Script to import Sleep Cycle CSV data exported from iOS app into Day One
plist XML format.

To import your sleep cycle use the settings screen in the iOS app to export
the entire database to a csv file.  Then, email the file to yourself and save
the csv file.  This script will process that csv file with the -f argument.
"""

import argparse
import collections
from datetime import datetime
import csv
import os
import re
import uuid

from dayonetools.services import convert_to_dayone_date_string

DAYONE_ENTRIES = '/Users/durden/Dropbox/Apps/Day One/Journal.dayone/entries/'

# This text will be inserted into the first line of all entries created, set to
# '' to remove this completely.
HEADER_FOR_DAYONE_ENTRIES = 'Sleep'

# Note the strange lack of indentation on the {entry_text} b/c day one will
# display special formatting to text that is indented, which we want to avoid.
ENTRY_TEMPLATE = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Creation Date</key>
    <date>{sleep_start}</date>
    <key>Entry Text</key>
    <string> {entry_title}
- Bedtime: {Start}
- Wake time: {End}
- Quality: {Sleep_quality}
- Total sleep time: {Time_in_bed}
- Notes: {Sleep_Notes}
- Steps: {Activity_steps}

#sleep
    </string>
    <key>Starred</key>
    <false/>
    <key>Tags</key>
    <array>
        <string>sleep</string>
    </array>
    <key>UUID</key>
    <string>{uuid_str}</string>
</dict>
</plist>
"""


def _parse_args():
    """Parse sys.argv arguments"""

    parser = argparse.ArgumentParser(
                                description='Export Sleep Cycle data to Day One')

    parser.add_argument('-f', '--file', action='store',
                        dest='input_file', required=True,
                        help='CSV file to import from')

    parser.add_argument('-v', '--verbose', default=False, action='store_true',
                        dest='verbose', required=False,
                        help='Verbose debugging information')

    parser.add_argument('-t', '--test', default=False, action='store_true',
                        dest='test', required=False,
                        help=('Test import by creating Day one files in local '
                              'directory for inspection'))

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


def _create_entry(entry, directory, verbose):
    """
    Create/write day one file with given sleep cycle entry

    entry should be a named tuple
    """

    # Create unique uuid without any specific machine information
    # (uuid() vs. uuid()) and strip any '-' characters to be
    # consistent with dayone format.
    uuid_str = re.sub('-', '', str(uuid.uuid4()))

    file_name = '%s.doentry' % (uuid_str)
    full_file_name = os.path.join(directory, file_name)

    entry_dict = entry._asdict()
    entry_dict['uuid_str'] = uuid_str

    day_str, time_str = entry_dict['Start'].split(' ')
    hour, minute, second = time_str.split(':')
    entry_dict['sleep_start'] = convert_to_dayone_date_string(day_str,
                                                              hour,
                                                              minute,
                                                              second)

    with open(full_file_name, 'w') as file_obj:
        text = ENTRY_TEMPLATE.format(entry_title=HEADER_FOR_DAYONE_ENTRIES,
                                     **entry_dict)
        file_obj.write(text)

    if verbose:
        print 'Created entry for %s: %s' % (entry.Start, file_name)


def read_entries(filename, start_date=None):
    """
    Read and yield namedtuple for entries from filename

    if start_date is given as a datetime object only entries that happened on
    or after that date will be returned.
    """

    def _sanitize_fields(fields):
        """
        Replace all spaces with '_' and all parenthesis with empty string so we
        can use these names as fields in a named tuple
        """

        # Use regex for parenthesis b/c we want to replace either ( or ) with
        # nothing and don't want to call replace 3 times here.  This is a great
        # example of premature optimization ;)

        paren = re.compile(r'[()]')
        return [paren.sub('', field).replace(' ', '_') for field in fields]


    with open(filename, 'r') as file_obj:
        csv_reader = csv.reader(file_obj, delimiter=';')
        header = csv_reader.next()

        sleep = collections.namedtuple('sleep', _sanitize_fields(header))

        for row in csv_reader:
            # Create named tuple then use it's API to convert to a dict we can
            # easily expand to format the entry text without hardcoding any
            # names in the code itself.  We are heavily dependent on the names
            # in the entry template matching the header line though.
            entry = sleep(*row)

            start_sleep = datetime.strptime(entry.Start, '%Y-%m-%d %H:%M:%S')

            if start_date is None or start_sleep >= start_date:
                yield entry


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

    for entry in read_entries(args['input_file'], args['since']):
        _create_entry(entry, directory, args['verbose'])


if __name__ == '__main__':
    main()

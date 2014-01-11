"""
Script to import Nike fuel data from a CSV format like the following:

distance,miles,steps,pace,fuel,start_time,device,calories,duration
2.70,2.69928887137,5517,(33'46/mi),2714,2013-06-08T05:00:00Z,FUELBAND,839,9:37:00

The result will be a new Day One entry for each line in the CSV file.
"""

import argparse
import collections
from datetime import datetime
import csv
import os
import re
import uuid

DAYONE_ENTRIES = '/Users/durden/Dropbox/Apps/Day One/Journal.dayone/entries/'

# This text will be inserted into the first line of all entries created, set to
# '' to remove this completely.
HEADER_FOR_DAYONE_ENTRIES = 'Nike Fuel'

# Note the strange lack of indentation on the {entry_text} b/c day one will
# display special formatting to text that is indented, which we want to avoid.
ENTRY_TEMPLATE = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Creation Date</key>
    <date>{start_time}</date>
    <key>Entry Text</key>
    <string> {entry_title}
- Fuel: {fuel} points
- Steps: {steps}
- Distance: {distance} miles
- Calories: {calories}
- Device: {device}

#nikefuel #fitness
    </string>
    <key>Starred</key>
    <false/>
    <key>Tags</key>
    <array>
        <string>nikefuel</string>
        <string>fitness</string>
    </array>
    <key>UUID</key>
    <string>{uuid_str}</string>
</dict>
</plist>
"""


def _parse_args():
    """Parse sys.argv arguments"""

    parser = argparse.ArgumentParser(
                                description='Export NikeFuel data to Day One')

    parser.add_argument('-f', '--file', action='store',
                        dest='input_file', required=True,
                        help='CSV file to import from')

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


def _create_nikeplus_entry(activity, directory, verbose):
    """
    Create/write day one file with given nike plus activity

    activity should be a named tuple
    """

    # Create unique uuid without any specific machine information
    # (uuid() vs.  uuid()) and strip any '-' characters to be
    # consistent with dayone format.
    uuid_str = re.sub('-', '', str(uuid.uuid4()))

    file_name = '%s.doentry' % (uuid_str)
    full_file_name = os.path.join(directory, file_name)

    activity_dict = activity._asdict()
    activity_dict['uuid_str'] = uuid_str

    with open(full_file_name, 'w') as file_obj:
        text = ENTRY_TEMPLATE.format(entry_title=HEADER_FOR_DAYONE_ENTRIES,
                                     **activity_dict)
        file_obj.write(text)

    if verbose:
        print 'Created entry for %s: %s' % (activity.start_time, file_name)


def read_entries(filename, start_date=None):
    """
    Read and yield namedtuple for entries from filename

    if start_date is given as a datetime object only entries that happened on
    or after that date will be returned.
    """

    with open(filename, 'r') as file_obj:
        csv_reader = csv.reader(file_obj)
        header = csv_reader.next()

        activity = collections.namedtuple('activity', header)

        for row in csv_reader:
            # Create named tuple then use it's API to convert to a dict we can
            # easily expand to format the entry text without hardcoding any
            # names in the code itself.  We are heavily dependent on the names
            # in the entry template matching the header line though.
            entry = activity(*row)

            # Date information in nikeplus is separated from time information
            # with a 'T'
            date = entry.start_time.split('T')[0].strip()
            entry_date = datetime.strptime(date, '%Y-%m-%d')

            if start_date is None or entry_date >= start_date:
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
        _create_nikeplus_entry(entry, directory, args['verbose'])


if __name__ == '__main__':
    main()

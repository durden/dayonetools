"""
Simple script to parse idonethis.com CSV exported file and turn into individual
day one entries

To use this script you must first export your idonethis.com data in CSV format.
This can be done by performing the following:

1. Login to idonethis.com account
2. Go to settings (Gear icon in top-right navigation)
3. Choose 'Export' from menu
4. Click download button

This will save the CSV file which you can use directly as an argument to this
script.

You then will want to edit DAYONE_ENTRIES and possibly
HEADER_FOR_DAYONE_ENTRIES to match your data file and preferences.

There is also a '-t' option that will process your CSV file and put the results
in a 'test/' directory for inspection.  This is recommended before running this
application on your full Day One directory.

You can find all your imported idonethis entries after pushing the Day One by
searching in Day One for the #idonethis tag.  All imported entries will have
this tag.
"""

import argparse
import csv
from datetime import datetime
import os
import re
import uuid

from dayonetools.services import convert_to_dayone_date_string

DAYONE_ENTRIES = '/Users/durden/Dropbox/Apps/Day One/Journal.dayone/entries/'

# Depending on where you entered your iDoneThis entry the text might be wrapped
# in quotes.  This will automatically remove them.
STRIP_QUOTES = True

# This text will be inserted into the first line of all entries created, set to
# '' to remove this completely.
HEADER_FOR_DAYONE_ENTRIES = 'iDoneThis entry'


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
{entry_text}]]>
#idonethis
    </string>
    <key>Starred</key>
    <false/>
    <key>Tags</key>
    <array>
        <string>idonethis</string>
    </array>
    <key>UUID</key>
    <string>{uuid_str}</string>
</dict>
</plist>
"""


def _parse_args():
    """Parse sys.argv arguments"""

    parser = argparse.ArgumentParser(
                                description='Export iDonethis data to Day One')

    parser.add_argument('-f', '--file', action='store',
                        dest='input_file', required=True,
                        help='CSV file to import from')

    parser.add_argument('-v', '--verbose', default=False, action='store_true',
                        dest='verbose', required=False,
                        help='Verbose debugging information')

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
    parser.add_argument('-t', '--test', default=False, action='store_true',
                        dest='test', required=False,
                        help=('Test import by creating Day one files in local '
                             'directory for inspect'))

    return vars(parser.parse_args())


def _create_dayone_entry(date, entries, directory, verbose):
    """Create single dayone journal entry for list of given entries"""

    entry_text = '\n'.join(entries)
    date = convert_to_dayone_date_string(date)

    # Create unique uuid without any specific machine information (uuid() vs.
    # uuid()) and strip any '-' characters to be consistent with dayone format.
    uuid_str = re.sub('-', '', str(uuid.uuid4()))

    file_name = '%s.doentry' % (uuid_str)
    full_file_name = os.path.join(directory, file_name)

    with open(full_file_name, 'w') as file_obj:
        text = ENTRY_TEMPLATE.format(entry_title=HEADER_FOR_DAYONE_ENTRIES,
                                     date=date,
                                     entry_text=entry_text,
                                     uuid_str=uuid_str)
        file_obj.write(text)

    if verbose:
        print 'Created entry for %s: %s' % (date, file_name)


def _sanitize_entry_text(entry_lines, strip_quotes):
    """
    Sanitize entry text by remove extra whitespace and quotes if asked
    """

    # Allow commas in the entry, everything after date is entry
    # Strip any line endings, we'll standardize them later
    entry_text = ''.join(entry_lines).strip()
    if strip_quotes:
        entry_text = re.sub('"', '', entry_text)

    return entry_text


def read_entries_by_day(filename, start_date=None):
    """
    Parse given CSV file of idonethis entries and yield tuple containting the
    following:
        (date, list of entries for day)

    date will be string in format: YYYY-MM-DD

    if start_date is provided as a datetime object then only days starting on
    or after the start_date will be returned.
    """

    with open(filename, 'r') as file_obj:
        current_day_entries = []
        curr_date = None
        date_re = re.compile('^\d{4}-\d{2}-\d{2}$')

        for row in csv.reader(file_obj):
            # If line doesn't start with a date assume it's just another line
            # in the current entry we are accumulating.
            new_date = row[0]
            if not date_re.match(new_date):
                entry_text = _sanitize_entry_text(row[1:], STRIP_QUOTES)

                if not current_day_entries:
                    raise IndexError(
                        'No current entries to add to, possibly invalid file')

                current_day_entries.append(entry_text)
                continue

            entry_text = _sanitize_entry_text(row[1:], STRIP_QUOTES)

            if curr_date is None:
                curr_date = new_date

            # iDoneThis orders file export in decreasing dates so when we find
            # an entry that occured BEFORE date user asked for we are done.
            if start_date is not None:
                curr_dtime_obj = datetime.strptime(curr_date, '%Y-%m-%d')
                if curr_dtime_obj < start_date:
                    raise StopIteration

            if curr_date == new_date:
                current_day_entries.append(entry_text)
            else:
                yield (curr_date, current_day_entries)
                current_day_entries = [entry_text]
                curr_date = new_date

        # Get last day if there was anything left over
        if current_day_entries:
            yield (curr_date, current_day_entries)


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

    for curr_date, entries in read_entries_by_day(args['input_file'],
                                                  args['since']):
        entries = reversed(entries)

        _create_dayone_entry(curr_date, entries, directory, args['verbose'])


if __name__ == '__main__':
    main()

# -*- mode: python;  coding: utf-8; -*-

"""Common services code"""

import os

AVAILABLE_SERVICES = ['habit_list', 'idonethis', 'nikeplus', 'pedometerpp',
                      'sleep_cycle']


def get_service_module(service_name):
    """Import given service from dayonetools.services package"""

    import importlib
    services_pkg = 'dayonetools.services'

    module = '%s.%s' % (services_pkg, service_name)
    return importlib.import_module(module)


def convert_to_dayone_date_string(day_str, hour=10, minute=0, second=0):
    """
    Convert given date in 'yyyy-mm-dd' format into dayone accepted format of
    iso8601 and adding additional hour, minutes, and seconds if given.
    """

    year, month, day = day_str.split('-')

    from datetime import datetime
    now = datetime.utcnow()

    # FIXME: The current version of day one does not support timezone data
    # correctly.  So, if we enter midnight here then every entry is off by a
    # day.

    # Don't know the hour, minute, etc. so just assume midnight
    date = now.replace(year=int(year),
                       month=int(month),
                       day=int(day),
                       minute=int(minute),
                       hour=int(hour),
                       second=int(second),
                       microsecond=0)

    iso_string = date.isoformat()

    # Very specific format for dayone, if the 'Z' is not in the
    # correct positions the entries will not show up in dayone at all.
    return iso_string + 'Z'


def get_outfolder_names(service, outfolderseed, verbose=False):
    """
    Ensure existence of a temp folder and return the path
    Assemble path to the outfolder according to the given seed
    Search for the Day One Journal in iCloud, DropBox folders and return the path
    or return the temp folder if no journal was found
    :param service: Name of the calling service
    :param outfolderseed: command line seed for the outfolder
    :param verbose: wie der Name schon sagt
    """

    # FIXME: Add progress output for --verbose

    tempfolder = os.path.abspath(os.path.join('..', 'temp', service))
    if not os.path.exists(tempfolder):
        os.makedirs(tempfolder)

    d1folder = ''
    if outfolderseed == 'test':
        # force it into the tempfolder
        d1folder = tempfolder
    elif outfolderseed == 'auto':
        # Try to find the Day One journal at the usual suspect places
        # FIXME: What is the correct name, I’m not using DropBox
        #candidate = os.path.expanduser('~/Dropbox/Apps/Day One/Journal.dayone/entries')
        candidate = os.path.expanduser('~/Dropbox/Applications/Day One/Journal.dayone/entries')
        if os.path.exists(candidate):
            d1folder = candidate
        else:
            candidate = os.path.expanduser(
                '~/Library/Mobile Documents/5U8NS4GX82~com~dayoneapp~dayone/Documents/Journal_dayone/entries'
            )
            if os.path.exists(candidate):
                d1folder = candidate
    elif os.path.exists(outfolderseed):
        # We try to use the given folder
        d1folder = outfolderseed

    if d1folder == '':
        # TODO: issue a warning or flag an error
        d1folder = tempfolder

    return d1folder, tempfolder


# Make all services available from this level
for service_name in AVAILABLE_SERVICES:
    service = get_service_module(service_name)

#!/usr/bin/python
# -*- mode: python;  coding: utf-8; -*-

"""
This service will extract data from the sqlite database of the pedometer++
iOS app (http://crossforward.com) and exports them as Day One Journal
(http://dayoneapp.com/) entries.

The database is used from the iTunes backup of the iOS device which you can locate
from within the iTunes Preferences->Devices via the context menu (Reveal in Finder).

The database file name is assumed to be 'dda8ace3c3f41792dd620ef4269a1344031686a7'

Also, it's encouraged to run this with the '-o test' option first so that all your
Day One entires will be created in a local directory called 'temp.'  This will
allow you to inspect the conversion.  You can manually copy a few select
entries into your Day One 'entries/' folder to ensure you approve of the
formatting and can easily make any formatting adjustments.  Then, you can run
this module again to fully import entries into Day One.
"""
__author__ = 'jotefa'

import argparse
import shutil
from dayonetools.services import *

SERVICENAME = 'pedometerpp'


class PedometerPP():

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Import Pedometer++ data from your iPhone Backup into your Day One Journal'
        )
        parser.add_argument(
            '-d', '--device', action='store',
            dest='device', required=True,
            help='Backup folder of the iOS device'
        )
        parser.add_argument(
            '-o', '--out', default='auto', action='store',
            dest='outfolder', required=True,
            help="Day One Journal folder or 'auto' or 'test'"
        )
        parser.add_argument(
            '-v', '--verbose', default=False, action='store_true',
            dest='verbose', required=False,
            help='Verbose debugging information'
        )
        self.args = vars(parser.parse_args())

        # FIXME: Add progress output for --verbose
        print self.args

        # Prepare output folders
        self.d1folder, self.tempfolder = get_outfolder_names(
            SERVICENAME,
            self.args['outfolder'],
            self.args['verbose']
        )
        print '\nExporting to “{0}”'.format(self.d1folder)
        print '\nTemporary files saved in “{0}”'.format(self.tempfolder)

        # Prepare input database
        backupfolder = '~/Library/Application Support/MobileSync/Backup'
        # TODO: Add testing for OS when Day One becomes available on Windows or other OS

        dbbackup = os.path.join(
            os.path.expanduser(backupfolder),
            self.args['device'],
            'dda8ace3c3f41792dd620ef4269a1344031686a7'  # Name of the pedometer++ database backup
        )
        print '\nCollecting data from “{0}”'.format(dbbackup)

        # FIXME: Check existence

        # Copy the database into tempFolder to avoid messing up the “official”
        # backup with temp files generated during sqlite access
        # It’s a waste, but only 30~KB per half a year
        self.dbfile = os.path.join(self.tempfolder, 'pedometerpp.sqlite')
        shutil.copy(dbbackup, self.dbfile)


def main():
    ppp = PedometerPP()


if __name__ == '__main__':
    main()

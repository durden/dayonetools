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
from __future__ import unicode_literals

__author__ = 'jotefa'

import argparse
import shutil
from dayonetools.services import *
import sqlite3 as sqlite
import datetime
import pytz

SERVICENAME = 'pedometerpp'
SERVICEVERSION = '1.0a1'
SERVICEID = 'de.jotefa.d1tools.pedometerpp'


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
            '-t', '--timezone', default='Europe/Berlin', action='store',
            dest='timezone', required=False,
            help="The timezone of the pedometer (iPhone), default: 'Europe/Berlin'"
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
        print self.args, file

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

        # Initialize our data collection
        self.entries = {}

    def collectentries(self):
        """
        Load the database entries into a python dict
        Key is the UTC time of an entry
        """
        con = sqlite.connect(self.dbfile)
        cur = con.cursor()

        cur.execute("SELECT * FROM ZSTEPCOUNT ORDER BY ZTIMESTAMP")
        col_names = [cn[0] for cn in cur.description]
        print '\n', col_names

        for row in cur.fetchall():
            #print row
            # Pedometer++ saves a ZDATESTRING which is a mess of localized names
            # and US sequence. We ignore it and interpret the ZTIMESTAMP, which
            # is shifted by 31 years.
            dt = datetime.datetime.fromtimestamp(row[4])
            # We set the time to 23:59 to make it the last item of a Day One day
            dt = dt.replace(year=dt.year+31, hour=23, minute=59)
            # Convert from the device time zone to UTC as expected by Day One
            dt = pytz.timezone(self.args['timezone']).localize(dt)
            dt = dt.astimezone(pytz.utc)
            #print dt.tzinfo, dt.dst()

            print '{1} • {0[0]:4} {0[1]:5} {0[2]:5} {0[3]:10} {0[4]:10} {0[5]}'.format(row, dt)
            self.entries[dt] = {
                'ent': row[1],  # FIXME: I have no idea what that is
                'opt': row[2],  # FIXME: I have no idea what that is
                'steps': row[3],
            }


def main():
    ppp = PedometerPP()
    ppp.collectentries()

if __name__ == '__main__':
    main()

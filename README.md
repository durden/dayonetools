# Day One tools

This is a collection of scripts to collect data from various sources and store
it into the (Day One)[http://dayoneapp.com/] journaling application.  Day One
is a fantastic application so I'd like to put as much of the data about my
habits, Internet usage, goals, etc. into it as possible.  Luckily, the format
for Day One is simply XML in the form of OS X plists.  This makes it very easy
to import data into.

## Running scripts

Each script supports a single service.  The documentation, etc. for the script
should be available by running any of the scripts individually with the `-h`
parameter.

## Goals

This repository aims to be a single place for one-shot scripts to semi-automate
exporting various data into the Day One XML format.  The purpose is to
primarily support services without a web API and those that involve more manual
setup to export data, etc.

### Supported services

- [iDoneThis.com](http://idonethis.com)
- [habit list](http://habitlist.com/) (coming soon)

### Differences to Slogger

This set of tools is very similar to the popular
[slogger](https://github.com/ttscoff/Slogger).  However, it differs in a few
ways.

1. [slogger](https://github.com/ttscoff/Slogger) is meant to be run
   automatically on a schedule via cron or any similar scheduling mechanism.
2. [slogger](https://github.com/ttscoff/Slogger) primarily supports services
   that have a web API.
3. [slogger](https://github.com/ttscoff/Slogger) is written in Ruby.

The Day One tools collection of scripts is meant to fill this gap regarding
unsupported services in Slogger.  In addition, it's a different mindset in that
these scripts could be automated but the services they import from are lesser
used and possibly more difficult to export data from.

# Day One tools

This is a collection of scripts to collect data from various sources and store
it into the [Day One](http://dayoneapp.com/) journaling application.  Day One
is a fantastic application so I'd like to put as much of the data about my
habits, Internet usage, goals, etc. into it as possible.  Luckily, the format
for Day One is simply XML in the form of OS X plists.  This makes it very easy
to import data into.

## Goals

This repository aims to be a single place for one-shot scripts to semi-automate
exporting various data into the Day One XML format.  The purpose is to
primarily support services without a web API and those that involve more manual
setup to export data, etc.

## Install
- User mode
    - pip install dayonetools

- Development mode
    - Install package with the standard `pip` workflow:
        - git clone repositiory
        - cd into repository
        - pip install .

Now you should have a top-level script called `dayonetools` to interact with
all the individual services, etc.

- Run `dayonetools -h` to ensure the install worked properly.

## Usage

- Run `dayonetools -h` for help
- Run `dayonetools <service_name> -h` for help on an individual service
    - For example: `dayonetools idonethis -h`

### Supported services

- [iDoneThis.com](http://idonethis.com)
- [nike fuel](http://nikeplus.nike.com/)
- [habit list](http://habitlist.com/)
- [sleep cycle](http://sleepcycle.com/)
- [Timing](http://timingapp.com/) (coming soon)
- [Pedometer++](http://pedometerplusplus.com/) ([itunes store](https://itunes.apple.com/de/artist/cross-forward-consulting-llc/id295660206?mt=8))

### How to contribute

See CONTRIBUTE file for contribution guidelines.

### Differences from Slogger

This set of tools is very similar to the popular
[slogger](https://github.com/ttscoff/Slogger).  However, it differs in a few
ways.

1. [slogger](https://github.com/ttscoff/Slogger) is meant to be run
   automatically on a schedule via cron or any similar scheduling mechanism.
2. [slogger](https://github.com/ttscoff/Slogger) primarily supports services
   that have a web API.
3. [slogger](https://github.com/ttscoff/Slogger) is written in Ruby.

The Day One tools collection of scripts is meant to fill the gap regarding
unsupported services in Slogger.  In addition, it's a different mindset in that
these scripts could be automated but the services they import from are lesser
used and possibly more difficult to export data from.

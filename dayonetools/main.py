"""Entry point for dayonetools import process"""

import sys

import dayonetools.services as services


def _show_help():
    """Print help"""

    _help = "{doc}\n\nUsage: {usage}\nSupported service arguments: {services}"
    args = {'doc': __doc__,
            'usage': '[--version] [%s <service_name>]' % (sys.argv[0]),
            'services': services.AVAILABLE_SERVICES}

    print _help.format(**args)


def _parse_args():
    """
    Parse sys.argv arguments

    Don't use argparse here b/c we are just a front-end to other scripts that
    use argparse.  This script only has one real argument, a service, and we
    forward all other args down to main scripts.  Argparse is a pain when
    wanting to forward arguments to other scripts esp. if the lower ones take
    arguments this one doesn't 'accept.'
    """

    args = {}

    try:
        args['service_name'] = sys.argv[1]
    except IndexError:
        _show_help()
        sys.exit(-1)

    if args['service_name'] == '--version':
        from dayonetools import __version__
        print __version__
        sys.exit(0)

    valid_service = args['service_name'] in services.AVAILABLE_SERVICES

    if valid_service:
        args['service_module'] = services.get_service_module(
                                                        args['service_name'])

    # Manually handle -h so we can pass it to other scripts instead of this
    # main entry point stealing it.
    if '-h' in sys.argv and valid_service:
        pass
    elif '-h' in sys.argv or len(sys.argv) == 2 or not valid_service:
        _show_help()
        sys.exit(0)

    return args


def main():
    args = _parse_args() 

    # We steal the first two arguments, service name and script.
    sys.argv[0] = args['service_name']
    sys.argv.remove(args['service_name'])

    args['service_module'].main()


if __name__ == '__main__':
    main()

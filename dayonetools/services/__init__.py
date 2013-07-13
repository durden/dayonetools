"""Common services code"""

AVAILABLE_SERVICES = ['habit_list', 'idonethis', 'nikeplus']


def get_service_module(service_name):
    """Import given service from dayonetools.services package"""

    import importlib
    services_pkg = 'dayonetools.services'

    module = '%s.%s' % (services_pkg, service_name)
    return importlib.import_module(module)


def convert_to_dayone_date_string(date):
    """
    Convert given date in 'yyyy-mm-dd' format into dayone accepted format of
    iso8601

    The timestamp will match the current time but year, month, and day will
    be replaced with given arguments.
    """

    year, month, day = date.split('-')

    from datetime import datetime
    now = datetime.utcnow()

    # Dayone doesn't read entries correctly when date has a ms component
    ms = 0

    date = now.replace(year=int(year),
                       month=int(month),
                       day=int(day),
                       microsecond=ms)

    iso_string = date.isoformat()

    # Very specific format for dayone, if the 'Z' is not in the
    # correct positions the entries will not show up in dayone at all.
    return iso_string + 'Z'


# Make all services available from this level
for service_name in AVAILABLE_SERVICES:
    service = get_service_module(service_name)

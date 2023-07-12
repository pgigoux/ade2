#!/usr/bin/env python3
import argparse
from epics import PV

# Alarm field names
ALARM_SEVERITY = 'SEVR'
ALARM_STATUS = 'STAT'
ALARM_MESSAGE = 'AMSG'
NEW_ALARM_STATUS = 'NSTA'
NEW_ALARM_SEVERITY = 'NSEV'
NEW_ALARM_MESSAGE = 'NAMSG'
DESCRIPTION = 'DESC'

# Alarm values
SEVERITY_INVALID = 'INVALID'
SEVERITY_NO_ALARM = 'NO_ALARM'
STATUS_UNDEFINED = '17'
STATUS_NO_ALARM = 'NO_ALARM'

GET_TIMEOUT = 2

# Field lists
field_list = (ALARM_SEVERITY, ALARM_STATUS, NEW_ALARM_SEVERITY,
              NEW_ALARM_STATUS, DESCRIPTION)

# Messages are not supported in older versions of EPICS
message_field_list = (ALARM_MESSAGE, NEW_ALARM_MESSAGE)

short_fields = (ALARM_SEVERITY, ALARM_STATUS, NEW_ALARM_SEVERITY, NEW_ALARM_STATUS)
long_fields = (DESCRIPTION, ALARM_MESSAGE, NEW_ALARM_MESSAGE)


def default_dictionary() -> dict:
    d = {ALARM_SEVERITY: SEVERITY_NO_ALARM,
         ALARM_STATUS: STATUS_NO_ALARM,
         NEW_ALARM_SEVERITY: STATUS_NO_ALARM,
         NEW_ALARM_STATUS: STATUS_NO_ALARM,
         DESCRIPTION: '',
         ALARM_MESSAGE: '',
         NEW_ALARM_MESSAGE: ''
         }
    return d


def channel_name(record_name: str, field_name: str) -> str:
    return f'{record_name}.{field_name}'


def print_title(csv_output=False):
    record_name_title = 'Record name'
    if csv_output:
        title = record_name_title
        for field_name in short_fields + long_fields:
            title += f',{field_name}'
    else:
        title = f'{record_name_title:30}'
        for field_name in short_fields:
            title += f'{field_name:15}'
        for field_name in long_fields:
            title += f'{field_name:25}'
    print(title)


def print_line(record_name: str, alarms: dict, csv_output=False):
    if csv_output:
        line = record_name
        for field_name in short_fields + long_fields:
            line += f',{alarms[field_name]}'
    else:
        line = f'{record_name:30}'
        for field_name in short_fields:
            line += f'{alarms[field_name]:15}'
        for field_name in long_fields:
            line += f'{alarms[field_name]:25}'
    print(line)


def process_file(file_name: str, ignore_udf=False, csv_output=False) -> list:
    """
    :param file_name: file name
    :param ignore_udf: ignore undefined alarms?
    :param csv_output: output in csv format?
    :return: list with output
    """
    try:
        f = open(file_name, 'r')
    except FileNotFoundError:
        print(f'file {file_name} does not exist')
        return []

    no_msg_flag = True
    print_title(csv_output=csv_output)

    for line in f:
        record_name = line.strip()

        timeout = False
        d = default_dictionary()

        for field_name in field_list:

            # Get the channel value.
            value = PV(channel_name(record_name, field_name)).get(as_string=True, timeout=GET_TIMEOUT)
            if value is None:
                timeout = True
                print(f'connection timeout {record_name}')
                break
            else:
                d[field_name] = value

            # The undefined alarm status is sometimes reported as a numeric value
            # Convert to the string equivalent.
            if d[field_name] == STATUS_UNDEFINED:
                d[field_name] = 'UDF'

        # Process the message fields
        # The no_msg_flag will be set if the prgram fails to read any of the message fiels.
        # This will prevent timeout while getting these fields down the road.
        if no_msg_flag:
            for field_name in message_field_list:
                value = PV(channel_name(record_name, field_name)).get(as_string=True, timeout=GET_TIMEOUT)
                if value is None:
                    no_msg_flag = False
                    break
                else:
                    d[field_name] = value

        # Skip record if there was a timeout or if there are no alarms
        # Ignoring the UDF alarm state is also done at this point.
        if timeout:
            continue
        else:
            no_alarm = (d[ALARM_SEVERITY] == SEVERITY_NO_ALARM,
                        d[ALARM_STATUS] == STATUS_NO_ALARM,
                        d[NEW_ALARM_SEVERITY] == SEVERITY_NO_ALARM)
            if all(no_alarm) or (d[ALARM_STATUS] == 'UDF' and ignore_udf):
                continue

        # The program will get here only if there are alarms
        print_line(record_name, d, csv_output=csv_output)


if __name__ == '__main__':
    # Process command line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument(action='store',
                        dest='input_file',
                        help='file with channel names',
                        default='')

    parser.add_argument('-i', '--ignore-udf',
                        action='store_true',
                        dest='ignore_udf',
                        default=False,
                        help='do not report undefined records (UDF)')

    parser.add_argument('--csv',
                        action='store_true',
                        dest='csv',
                        default=False,
                        help='format output as csv')

    args = parser.parse_args()

    try:
        process_file(args.input_file, ignore_udf=args.ignore_udf, csv_output=args.csv)
    except KeyboardInterrupt:
        print('Aborted')

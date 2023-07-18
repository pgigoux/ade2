#!/usr/bin/env python3
import argparse
from typing import Union
from epics import PV
from epics import ca

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
STATUS_NO_ALARM = 'NO_ALARM'

# Read timeout (seconds)
GET_TIMEOUT = 2

# Alarm fields that should be present in all records.
# The description is in this list as well as additional data.
field_list = (ALARM_SEVERITY, ALARM_STATUS, NEW_ALARM_SEVERITY,
              NEW_ALARM_STATUS, DESCRIPTION)

# Alarm message fields. They are not supported in older versions of EPICS
message_field_list = (ALARM_MESSAGE, NEW_ALARM_MESSAGE)

# How to format output
short_fields = (ALARM_SEVERITY, ALARM_STATUS, NEW_ALARM_SEVERITY, NEW_ALARM_STATUS)
long_fields = (DESCRIPTION, ALARM_MESSAGE, NEW_ALARM_MESSAGE)

# Dictionary used to convert numeric status alarm codes into string values
alarm_dict = {
    '0': 'NO_ALARM',
    '1': 'READ',
    '2': 'WRITE',
    '3': 'HIHI',
    '4': 'HIGH',
    '5': 'LOLO',
    '6': 'LOW',
    '7': 'STATE',
    '8': 'COS',
    '9': 'COMM',
    '10': 'TIMEOUT',
    '11': 'HW_LIMIT',
    '12': 'CALC',
    '13': 'SCAN',
    '14': 'LINK',
    '15': 'SOFT',
    '16': 'BAD_SUB',
    '17': 'UDF',
    '18': 'DISABLE',
    '19': 'SIMM',
    '20': 'READ_ACCESS',
    '21': 'WRITE_ACCESS',
}


def default_dictionary() -> dict:
    """
    Return a dictionary used to store alarms with default values
    :return: default value dictionary
    """
    d = {ALARM_SEVERITY: SEVERITY_NO_ALARM,
         ALARM_STATUS: STATUS_NO_ALARM,
         NEW_ALARM_SEVERITY: STATUS_NO_ALARM,
         NEW_ALARM_STATUS: STATUS_NO_ALARM,
         DESCRIPTION: '',
         ALARM_MESSAGE: '',
         NEW_ALARM_MESSAGE: ''
         }
    return d


def print_title(csv_output=False):
    """
    Print report title
    :param csv_output: csv output?
    """
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
    """
    Print report line
    :param record_name: record name
    :param alarms: dictionary with the alarm information
    :param csv_output: csv output?
    :return:
    """
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


def get_channel_value(record_name: str, field_name: str, use_ca=False) -> Union[str, None]:
    """
    Get a channel (record + field) value.
    The low level interface will close and clean the connection
    to minimize memory usage on the server side.
    :param record_name: record name
    :param field_name: field name
    :param use_ca: use low level interface
    :return: value or None if unable to read the value
    """
    channel_name = f'{record_name}.{field_name}'
    if use_ca:
        channel_id = ca.create_channel(channel_name, connect=False, callback=None, auto_cb=False)
        if not ca.connect_channel(channel_id, timeout=GET_TIMEOUT, verbose=False):
            return None
        value = ca.get(channel_id, as_string=True, as_numpy=False, wait=True, timeout=GET_TIMEOUT)
        ca.clear_channel(channel_id)
    else:
        pv = PV(channel_name)
        value = pv.get(as_string=True, timeout=GET_TIMEOUT)
    return value


def process_file(file_name: str, ignore_udf=False, csv_output=False, use_ca=False) -> list:
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

        # Loop over the field names.
        # Break the loop if it fails to read.
        for field_name in field_list:

            # Get the channel value.
            # value = PV(channel_name(record_name, field_name)).get(as_string=True, timeout=GET_TIMEOUT)
            value = get_channel_value(record_name, field_name, use_ca=use_ca)
            if value is None:
                timeout = True
                print(f'connection timeout {record_name}')
                break
            else:
                d[field_name] = value

            # The undefined alarm status is sometimes reported as a numeric value
            # Convert to the string equivalent.
            if value in alarm_dict:
                d[field_name] = alarm_dict[value]
            else:
                d[field_name] = value

        # Process the message fields
        # The no_msg_flag will be set if the program fails to read any of them.
        # This will prevent timeouts while getting these fields down the road.
        if no_msg_flag:
            for field_name in message_field_list:
                # value = PV(channel_name(record_name, field_name)).get(as_string=True, timeout=GET_TIMEOUT)
                value = get_channel_value(record_name, field_name, use_ca=use_ca)
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
                        help='file with record names',
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

    parser.add_argument('--ca',
                        action='store_true',
                        dest='ca',
                        default=False,
                        help='use low level interface (minimizes IOC memory usage)')

    args = parser.parse_args()

    try:
        process_file(args.input_file, ignore_udf=args.ignore_udf,
                     csv_output=args.csv, use_ca=args.ca)
    except KeyboardInterrupt:
        print('Aborted')

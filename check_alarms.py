#!/usr/bin/env python3
"""
Look for records that have alarm severity or status different than NO_ALARM.
This program was written for a conda environment running EPICS 7 and pyepics 3.5.0 (Rocky8)

Installation:
* conda create --name=py36 python=3.6
* conda activate py36
* pip install pyepics

Running:
* conda activate py36
* ./check_alarms.py [options] <file>
"""
import argparse
from typing import Union
from epics import PV
from epics import ca
from common import print_title, print_line, default_alarm_dictionary, ignore_alarms
from common import field_list, message_field_list

# Read timeout (seconds)
GET_TIMEOUT = 5


def get_channel_value(record_name: str, field_name: str, use_pv=False) -> Union[str, None]:
    """
    Get a channel (record + field) value.
    The low level interface will close and clean the connection to minimize memory usage on the server side.
    :param record_name: record name
    :param field_name: field name
    :param use_pv: use high level channel access interface
    :return: channel value or None if unable to read the value
    """
    channel_name = f'{record_name}.{field_name}'
    if use_pv:
        pv = PV(channel_name)
        value = pv.get(as_string=True, timeout=GET_TIMEOUT)
    else:
        channel_id = ca.create_channel(channel_name, connect=False, callback=None, auto_cb=False)
        connect_flag = ca.connect_channel(channel_id, timeout=GET_TIMEOUT, verbose=False)
        if not connect_flag:
            return None
        value = ca.get(channel_id, as_string=True, as_numpy=False, wait=True, timeout=GET_TIMEOUT)
        ca.clear_channel(channel_id)
    return value


def process_file(file_name: str, include_udf=False, csv_output=False, use_pv=False) -> list:
    """
    :param file_name: file name
    :param include_udf: include undefined alarms?
    :param csv_output: output in csv format?
    :param use_pv: use PV interface for channel access?
    :return: list with output
    """
    try:
        f = open(file_name, 'r')
    except FileNotFoundError:
        print(f'file {file_name} does not exist')
        return []

    msg_flag = True
    print_title(csv_output=csv_output)

    for line in f:
        record_name = line.strip()

        timeout = False
        d = default_alarm_dictionary()

        # Loop over the field names.
        # Break the loop if it fails to read.
        for field_name in field_list:

            # Get the channel value.
            value = get_channel_value(record_name, field_name, use_pv=use_pv)
            if value is None:
                timeout = True
                print(f'connection timeout {record_name}')
                break
            else:
                d[field_name] = value

            # The alarm status is sometimes reported as a numeric value
            # Convert to the string equivalent.
            if value in d:
                d[field_name] = d[value]
            else:
                d[field_name] = value

        # Process the message fields
        # The no_msg_flag will be set if the program fails to read any of them.
        # This will prevent timeouts while getting these fields down the road.
        if msg_flag:
            for field_name in message_field_list:
                # value = PV(channel_name(record_name, field_name)).get(as_string=True, timeout=GET_TIMEOUT)
                value = get_channel_value(record_name, field_name, use_pv=use_pv)
                if value is None:
                    msg_flag = False
                    break
                else:
                    d[field_name] = value

        # Skip record if there was a timeout or if there are no alarms
        # Ignoring the UDF alarm state is also done at this point.
        if timeout:
            continue
        elif ignore_alarms(d, include_udf=include_udf):
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

    parser.add_argument('--udf',
                        action='store_true',
                        dest='include_udf',
                        default=False,
                        help='include undefined records in the report (UDF)')

    parser.add_argument('--csv',
                        action='store_true',
                        dest='csv',
                        default=False,
                        help='format output as csv')

    parser.add_argument('--pv',
                        action='store_true',
                        dest='pv',
                        default=False,
                        help='use the high level channel interface interface')

    args = parser.parse_args()

    # Process input file. Trap keyboard exceptions (CTR-C).
    try:
        process_file(args.input_file, include_udf=args.include_udf,
                     csv_output=args.csv, use_pv=args.pv)
    except KeyboardInterrupt:
        print('Aborted')

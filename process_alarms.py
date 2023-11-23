#!/usr/bin/env python3
"""
Process the alarm data captured by capture_alarms.sh
This program is an alternative to check_alarms.py for those machines where pyepics is not available

Installation:
* conda create --name=py36 python=3.6
* conda activate py36

Running:
* conda activate py36
* ./process_alarms.py [options] <file>
"""
import sys
import argparse
from common import print_line, print_title, ignore_alarms, numeric_field_list


def missing_fields(d: dict) -> list:
    """
    A dictionary with alarm values is supposed to have at least the numeric
    alarm keywords (fields) and with non null values. Null values or missing
    fields can happen when caget fails to read.
    This function will return the list of missing or empty keywords (an empty
    list if the dictionary is fine).
    :param d: dictionary with alarm values
    :return: list with missing keywords or values
    """
    output_list = []
    for field_name in numeric_field_list:
        if field_name in d:
            if len(d[field_name]) == 0:
                output_list.append(field_name)
        else:
            output_list.append(field_name)
    return output_list


def process_file(file_name: str) -> dict:
    """
    Read the file generated using a bash script, containing the different
    alarms record.field values, one per line.
    :param file_name: input file name
    :return: dictionary with alarm values
    """
    output_dict = {}
    record_list = []
    d = {}
    last_record_name = ''
    with open(file_name, 'r') as f:
        for line in f:
            pv_name, pv_val = line.strip().split(',')
            record_name, field_name = pv_name.split('.')
            if record_name not in record_list:
                record_list.append(record_name)
                if d:
                    field_list = missing_fields(d)
                    if field_list:
                        print(f'missing fields {last_record_name}: {field_list}', file=sys.stderr)
                    else:
                        output_dict[last_record_name] = d
                        d = {}
                last_record_name = record_name
            d[field_name] = pv_val
    return output_dict


def print_data(alarms: dict, include_udf=False, csv_output=False):
    """
    Print the alarm data to the standard output
    :param alarms:
    :param csv_output:
    :param include_udf:
    :return:
    """
    print_title(csv_output=csv_output)
    for record_name in alarms:
        if not ignore_alarms(alarms[record_name], include_udf=include_udf):
            print_line(record_name, alarms[record_name], csv_output=csv_output)


if __name__ == '__main__':
    # alarm_dict = process_file('ag.out')
    # print_data(alarm_dict, include_udf=False, csv_output=True)

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

    args = parser.parse_args()

    try:
        alarm_dict = process_file(args.input_file)
        print_data(alarm_dict, include_udf=args.include_udf, csv_output=args.csv)
    except KeyboardInterrupt:
        print('Aborted', file=sys.stderr)

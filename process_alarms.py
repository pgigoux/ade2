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
import argparse
from common import print_line, print_title, ignore_alarms


def process_file(file_name: str) -> dict:
    """
    Read the file generated using a bash script, containing the different
    alarms record.field values, one per line.
    :param file_name: input file name
    :return: dictionary with alarm values
    """
    output_dict = {}
    with open(file_name, 'r') as f:
        for line in f:
            pv_name, pv_val = line.strip().split(',')
            record_name, field_name = pv_name.split('.')
            if record_name not in output_dict:
                output_dict[record_name] = {}
            d = output_dict[record_name]
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
        print('Aborted')

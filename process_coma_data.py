#!/usr/bin/env python3
import argparse
import datetime

# Keys used to index the value dictionary
KEY_TIMESTAMP = 'timestamp'
KEY_M2XPOS = 'm2xpos'
KEY_M2YPOS = 'm2ypos'
KEY_USERX = 'userx'
KEY_USERY = 'usery'
KEY_Z5 = 'z5'
KEY_Z6 = 'z6'
KEY_TEMPX = 'tempx'
KEY_TEMPY = 'tempy'
KEY_MODELX = 'modelx'
KEY_MODELY = 'modely'
KEY_NOMINALX = 'nominalx'
KEY_NOMINALY = 'nominaly'
KEY_CURRENTX = 'currentx'
KEY_CURRENTY = 'currenty'
KEY_DEMANDX = 'demandx'
KEY_DEMANDY = 'demandy'

# This list defines the order values will be written
KEY_LIST = [KEY_TIMESTAMP,
            KEY_M2XPOS, KEY_M2YPOS,
            KEY_CURRENTX, KEY_CURRENTY,
            KEY_Z5, KEY_Z6,
            KEY_USERX, KEY_USERY,
            KEY_NOMINALX, KEY_NOMINALY,
            KEY_TEMPX, KEY_TEMPY,
            KEY_MODELX, KEY_MODELY,
            KEY_DEMANDX, KEY_DEMANDY]

# Dictionary used to map EPICS channels to data keys
# The data keys are used to access the data in the value dictionary
channel_dictionary = {
    # redundant
    # 'm2:xPos': None, # m2 xpos
    # 'm2:yPos': None, # m2 ypos
    'tcs:om:m2RawXPos': KEY_M2XPOS,
    'tcs:om:m2RawYPos': KEY_M2YPOS,
    'tcs:m2XUserOffset': KEY_USERX,
    'tcs:m2YUserOffset': KEY_USERY,
    'tcs:m2XYOffset.VALA': KEY_USERX,
    'tcs:m2XYOffset.VALB': KEY_USERY,
    # redundant
    # 'tcs:om:m2XYErr.VALA': None, # z5
    # 'tcs:om:m2XYErr.VALB': None, # z6
    'tcs:m2XErrorCorr.VAL': KEY_Z5,
    'tcs:m2YErrorCorr.VAL': KEY_Z6,
    'tcs:om:m2XY.VALA': KEY_TEMPX,
    'tcs:om:m2XY.VALB': KEY_TEMPY,
    'tcs:om:m2XY.VALC': KEY_MODELX,
    'tcs:om:m2XY.VALD': KEY_MODELY,
    'tcs:om:m2XY.VALG': KEY_NOMINALX,
    'tcs:om:m2XY.VALH': KEY_NOMINALY,
    'tcs:om:m2XY.VALI': KEY_CURRENTX,
    'tcs:om:m2XY.VALJ': KEY_CURRENTY,
    'tcs:om:m2XY.VALE': KEY_DEMANDX,
    'tcs:om:m2XY.VALF': KEY_DEMANDY
}


def get_timestamp(line: str) -> datetime.datetime:
    """
    Convert time stamp into a datetime object
    :param line:
    :return:
    """
    _, t, _ = line.split()
    return datetime.datetime.strptime(t, '%Y%m%d-%H:%M:%S')


def new_values() -> dict:
    """
    Initialize the value dictionary
    :return: dictionay with keys and empty values
    """
    return {x: '' for x in channel_dictionary.values()}


def get_title() -> str:
    """
    Format title in csv format
    The column order is defined by KEY_LIST.
    :return: title string
    """
    title = ''
    for key in KEY_LIST:
        title += f'{key},'
    return title[:-1]


def format_data(values: dict) -> str:
    """
    Format the data columns in the dictionary in csv format.
    The column order is defined by KEY_LIST.
    :param values:
    :return: string with comma separated values
    """
    s = ''
    for key in KEY_LIST:
        s += f'{values[key]},'
    return s[:-1]


def write_data(data: list):
    """
    Write data to standard output in csv format (with colum titles)
    The data is stored in a list where each entry is a dictionary with the data columns.
    :param data: list of data "points"
    """
    print(get_title())
    for p in data:
        print(format_data(p))


def process_follow_file(file_name: str, start_date: datetime.datetime, end_date: datetime.datetime):
    """
    Process the file with coma data caputured
    :param file_name: input file name
    :param start_date: stating date
    :param end_date: ending date

    """
    try:
        f = open(file_name, 'r')
    except OSError:
        print(f'Cannot open file {file_name}')
        return

    # Initialize variables
    first_time = True
    values = new_values()
    output_list = []

    for line in f:
        line = line.strip()
        if '---' in line:
            ts = get_timestamp(line)
            values[KEY_TIMESTAMP] = ts
            if first_time:
                first_time = False
            else:
                if start_date < ts < end_date:
                    # print('=', values)
                    output_list.append(values)
                    # format_data(values)
                    values = new_values()
        elif 'drives:driveM2S.VALA' in line:
            continue
        else:
            # Extract channel name and value
            channel = value = ''
            aux = line.split()
            try:
                channel = aux[0]
                value = aux[1]
            except IndexError:
                pass
            if channel in channel_dictionary:
                key = channel_dictionary[channel]
                values[key] = value
                # print(values)

    write_data(output_list)

    f.close()


if __name__ == '__main__':
    # Process command line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument(action='store',
                        dest='input_file',
                        help='file with coma data',
                        default='')

    parser.add_argument('-s', '--start',
                        action='store',
                        dest='start_date',
                        default='',
                        help='starting date (YYYYMMDD-HHMMSS)')

    parser.add_argument('-e' '--end',
                        action='store',
                        dest='end_date',
                        default='',
                        help='ending date (YYYYMMDD-HHMMSS)')

    args = parser.parse_args()

    try:
        sd = datetime.datetime.strptime(args.start_date, '%Y%m%d-%H%M%S')
    except ValueError:
        sd = datetime.datetime(2000, 1, 1, 0, 0, 0)
    try:
        ed = datetime.datetime.strptime(args.end_date, '%Y%m%d-%H%M%S')
    except ValueError:
        ed = datetime.datetime(2050, 1, 1, 0, 0, 0)

    process_follow_file(args.input_file, sd, ed)

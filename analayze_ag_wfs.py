#!/usr/bin/env python
"""
interpol parameters

A,B,C   old/middle/new demand
D       quadratic fit parameters
E       Mark, PWFS1=1, PWFS2=2
F:      T1 copy
G:      OUTTYPE
H:      INTERPOLTYPE
I:      SAMSPEED

VALA    current x
VALB    current y
VALC    current z
VALD    current vx
VALE    current vx
VALF    current vx
VALG    apply time
VALH    global sample  (0..xxxx)
VALI    sample on table or number of written arrays (0..19)
"""
import re
import argparse
from datetime import datetime
import matplotlib.pyplot as plt

# Used to filter out lines with valid time stamps
YEAR = datetime.now().year

starting_time = None

INDEX_CHANNEL_NAME = 0
INDEX_DATE = 1
INDEX_TIME = 2
INDEX_DATA = 3
INDEX_APPLY_TIME = 6
INDEX_X = 7
INDEX_Y = 8
INDEX_Z = 9


def date_to_datetime(date: str, time: str) -> datetime:
    """
    Convert date and time to a datetime object
    :param date: date 'YYYY-MM-DD'
    :param time: time 'HH:MM:SS.SSSSSS"
    :return: datetime object
    """
    s = f'{date} {time}'
    return datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f')


def date_to_delta(date: str, time: str) -> float:
    """
    Convert date and time to a datetime object
    :param date: date 'YYYY-MM-DD'
    :param time: time 'HH:MM:SS.SSSSSS"
    :return: seconds from reference
    """
    global starting_time
    dt = datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M:%S.%f')
    if starting_time is None:
        starting_time = dt
    delta = dt - starting_time
    # print(dt, delta, delta.total_seconds())
    return delta.total_seconds()


def extract_data(file_name: str, channel_name: str, channel_index: int) -> tuple:
    """
    Extract data matching the channel name from the file.
    Each file in the line consists of the channel name, date, time and data.
    Data starts at INDEX_DATA and can continue for array data.
    :param file_name: input file
    :param channel_name: channel name to extract
    :param channel_index: data index in the line
    :return:
    """
    m = re.compile(f'^{channel_name}.*{YEAR}')
    t_out = []
    v_out = []
    try:
        f = open(file_name, 'r')
    except OSError:
        print(f'File {file_name} does not exist')
        return None, None

    for line in f:
        if m.search(line):
            line = line.strip().split()
            # print(line)
            # t_out.append(date_to_datetime(line[1], line[2]))
            t = date_to_delta(line[INDEX_DATE], line[INDEX_TIME])
            print('--', t, line[channel_index])
            if t < 0:
                continue
            t_out.append(t)
            v_out.append(float(line[channel_index]))
    return t_out, v_out


def plot_data(label: str, t: list, v: list):
    plt.title(label)
    plt.plot(t, v)
    plt.show()


def plot_data_2(label: str, t_1: list, v_1: list, t_2: list, v_2: list):
    fig, (ax1, ax2) = plt.subplots(2)
    fig.suptitle(label)
    ax1.plot(t_1, v_1)
    ax2.plot(t_2, v_2)
    plt.show()


def create_channel_dictionary(wfs_name: str) -> dict:
    return {
        # 't1': (f'ag:{wfs_name}:interpol.A', 6),
        # 'x1': (f'ag:{wfs_name}:interpol.A', 7),
        # 'y1': (f'ag:{wfs_name}:interpol.A', 8),
        # 'z1': (f'ag:{wfs_name}:interpol.A', 9),
        #
        # 't2': (f'ag:{wfs_name}:interpol.B', 6),
        # 'x2': (f'ag:{wfs_name}:interpol.B', 7),
        # 'y2': (f'ag:{wfs_name}:interpol.B', 8),
        # 'z2': (f'ag:{wfs_name}:interpol.B', 9),
        #
        # 't3': (f'ag:{wfs_name}:interpol.C', 6),
        # 'x3': (f'ag:{wfs_name}:interpol.C', 7),
        # 'y3': (f'ag:{wfs_name}:interpol.C', 8),
        # 'z3': (f'ag:{wfs_name}:interpol.C', 9),

        't1': (f'ag:{wfs_name}:followA.VALA', INDEX_APPLY_TIME),
        'x1': (f'ag:{wfs_name}:followA.VALA', INDEX_X),
        'y1': (f'ag:{wfs_name}:followA.VALA', INDEX_Y),
        'z1': (f'ag:{wfs_name}:followA.VALA', INDEX_Z),

        't2': (f'ag:{wfs_name}:followA.VALB', INDEX_APPLY_TIME),
        'x2': (f'ag:{wfs_name}:followA.VALB', INDEX_X),
        'y2': (f'ag:{wfs_name}:followA.VALB', INDEX_Y),
        'z2': (f'ag:{wfs_name}:followA.VALB', INDEX_Z),

        't3': (f'ag:{wfs_name}:followA.VALC', INDEX_APPLY_TIME),
        'x3': (f'ag:{wfs_name}:followA.VALC', INDEX_X),
        'y3': (f'ag:{wfs_name}:followA.VALC', INDEX_Y),
        'z3': (f'ag:{wfs_name}:followA.VALC', INDEX_Z),

        'x': (f'ag:{wfs_name}:interpol.VALA', INDEX_DATA),
        'y': (f'ag:{wfs_name}:interpol.VALB', INDEX_DATA),
        'z': (f'ag:{wfs_name}:interpol.VALC', INDEX_DATA),

        'vx': (f'ag:{wfs_name}:interpol.VALD', INDEX_DATA),
        'vy': (f'ag:{wfs_name}:interpol.VALE', INDEX_DATA),
        'vz': (f'ag:{wfs_name}:interpol.VALF', INDEX_DATA),

        't': (f'ag:{wfs_name}:interpol.VALG', INDEX_DATA),

        'gs': (f'ag:{wfs_name}:interpol.VALH', INDEX_DATA),
        's': (f'ag:{wfs_name}:interpol.VALI', INDEX_DATA)
    }


if __name__ == '__main__':
    # # Debugging
    # file_name = 'log20240209-e7.txt'
    # channel_dictionary = create_channel_dictionary('p1')
    # t_list, v_list = extract_data(file_name, channel_dictionary['x'])
    # if t_list is not None:
    #     plot_data(f'{file_name} - x', t_list, v_list)
    # exit(0)

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('input_file', action='store', help='input file')
    parser.add_argument('--c1', action='store',
                        help='first channel to plot')
    parser.add_argument('--c2', action='store', default='',
                        help='second channel to plot (optional)')
    parser.add_argument('--wfs', action='store', default='p1',
                        choices=['p1', 'p2'], help='wavefront sensor')

    parser.epilog = """
    Channel names:
    x1,y1,z1    old demand
    x2,y2,z2    middle demand
    x3,y3,z3    new demand
    x           current x
    y           current y
    z           current z
    vx          current vx
    vy          current vy
    vz          current vz
    t           apply time
    gs          global sample  (0..)
    s           sample on table or number of written arrays (0..19)
    """

    args = parser.parse_args()

    channel_dictionary = create_channel_dictionary(args.wfs)

    t1, v1, t2, v2 = None, None, None, None

    # Extract data
    if args.c1 in channel_dictionary:
        t1, v1 = extract_data(args.input_file, channel_dictionary[args.c1][0],
                              channel_dictionary[args.c1][1])

    if args.c2 in channel_dictionary:
        t2, v2 = extract_data(args.input_file, channel_dictionary[args.c2][0],
                              channel_dictionary[args.c2][1])

    # Plot data
    if t1 is not None and t2 is not None:
        plot_data_2(f'{args.input_file}: {args.c1} - {args.c2}', t1, v1, t2, v2)
    elif t1 is not None:
        plot_data(f'{args.input_file}: {args.c1}', t1, v1)
    elif t2 is not None:
        plot_data(f'{args.input_file}: {args.c2}', t2, v2)
    else:
        print(f'Nothing to plot')

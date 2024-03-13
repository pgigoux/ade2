"""
Determine the support package dependencies.

This program assumes that the source of all the support packages are all located
in the same directory, and that each package has a spec file that specifies its
dependencies.

By default, the program generates the build order.

The -devel is stripped of the package dependencies to make things easier to handle.
"""
import os
import re
import argparse

DEFAULT_PATH = os.getcwd()
IGNORE = ['epics-base', 're2c', 'gemini-ade', 'rpcgen', 'libtirpc', 'tdct', 'psmisc', '%{name}']
MATCH_REQ = '^Requires:'
MATCH_BUILD = '^BuildRequires:'
DEVEL = '-devel'


def spec_file(name: str):
    """
    Generate the spec file name from the package name
    Most spec files are of the form "package_name.spec"
    :param name: package name
    :return: spec file name with full path
    """
    if name == 'agseq':
        root = 'agSeq'
    elif name == 'AbDf1':
        root = 'abdf1'
    elif name == 'streamdevice':
        root = 'StreamDevice'
    elif name == 'gemUtil':
        root = 'gemutil'
    elif name == 'geminiRec':
        root = 'geminirec'
    else:
        root = name
    return os.path.join(name, f'{root}.spec')


def map_dependency(dep: str) -> str:
    """
    Map dependency name to package name.
    They are normally the same, but there are a few exceptions.
    :param dep: dependency name
    :return: package name
    """
    if dep == 'geminipcre':
        return 'pcre'
    elif dep == 'geminicalc':
        return 'calc'
    else:
        return dep


def filter_line(line: str) -> set:
    """
    Return a set with the package dependencies.
    Remove -devel packages since they are redundant.
    :param line: input line
    :return: dependency set
    """
    line = line.replace(DEVEL, '')
    return {map_dependency(_) for _ in line.split()[1:] if _ not in IGNORE}


def process_file(file_name: str) -> tuple:
    """
    Process spec file
    It returns the "Requires" and "BuildRequires" sets in a tuple
    :param file_name: spec file name
    :return: tuple with dependencies
    """
    req_set = set()
    build_set = set()
    with open(file_name, 'r') as f:
        for line in f:
            line = line.strip()
            if re.search(MATCH_REQ, line):
                req_set = req_set | filter_line(line)
            elif re.search(MATCH_BUILD, line):
                build_set = build_set | filter_line(line)
    return req_set, build_set


def process_dependencies(path_name: str, file_name: str) -> dict:
    """
    Process package dependencies
    It returns a dictionary indexed by the package name where each entry
    is a tuple of two sets with the "Requires" and "BuildRequires" dependencies.
    :param path_name: directory where the package source is located
    :param file_name: file containing the list of packages to process
    :return: dictionary with dependencies
    """
    d = {}
    try:
        f = open(file_name, 'r')
        for line in f:
            package_name = line.strip()
            spec_file_name = os.path.join(path_name, spec_file(package_name))
            d[package_name] = process_file(spec_file_name)
        f.close()
        return d
    except IOError:
        print(f'{file_name} could not be processed')


def generate_dot_output(file_name: str, deps: dict):
    """
    :param file_name: output file name
    :param deps: dependency dictionary
    """
    f = open(file_name, 'w')
    f.write('digraph dependencies {\n')
    for key in deps:
        r, b = deps[key]
        if b:
            for dep in b:
                f.write(key + f' -> {dep};\n')
        else:
            f.write(key + ';\n')
    f.write('}\n')
    f.close()


def build_order(deps: dict) -> dict:
    """
    Determine the package build order_dict based on the package dependencies
    It returns a dictionary where the key is a number starting from zero.
    The zero entry contains all the packages with no dependencies.
    :param deps: dependency dictionary
    :return: build order_dict dictionary
    """
    level = 0
    order_dict = {level: set()}

    # Build the set of packages with no dependencies (level 0)
    name_set = {_ for _ in deps}
    for name in name_set:
        r, b = deps[name]
        if not b:
            order_dict[level].add(name)
    pending_set = name_set - order_dict[level]
    # print('no deps', sorted(deps[level]))
    # print('pending', sorted(pending_set))

    while len(pending_set) > 0 and level < 20:
        level += 1
        order_dict[level] = set()
        # print('--', level, sorted(pending_set))
        for name in pending_set:
            r, b = deps[name]
            # print('=', b)
            if len(pending_set.intersection(b)) == 0:
                order_dict[level].add(name)
            # print(level, name, b, deps[level])
        pending_set = pending_set - order_dict[level]
        # print('    ', sorted(deps[level]))

    return order_dict


def print_build_order(order_dict: dict):
    """
    Print the build order to the terminal
    :param order_dict: build order dictionary
    """
    print('Build order. Packages with no dependencies have level zero:')
    for level in sorted(order_dict):
        for dep in sorted(order_dict[level]):
            print(f'{level}: {dep}')


def print_dependencies(deps: dict):
    """
    Print a dependency dictionary is format easy to read
    Used during debugging.
    :param deps: dependency dictionary
    """
    for key in sorted(deps):
        r, b = deps[key]
        if r or b:
            print(key)
            print('  Requires:      ', r)
            print('  BuildRequires: ', b)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(action='store',
                        dest='input_file',
                        help='file with package list',
                        default='')

    parser.add_argument('-d', '--deps',
                        action='store_true',
                        dest='deps',
                        default=False,
                        help='print dependencies instead of the build order?')

    parser.add_argument('-p', '--path',
                        action='store',
                        dest='path',
                        default=DEFAULT_PATH,
                        help='include undefined records in the report (UDF)')

    parser.add_argument('--dot',
                        action='store_true',
                        dest='dot',
                        default=False,
                        help='generate dot graph output?')

    parser.add_argument('--dotfile',
                        action='store',
                        dest='dotfile',
                        default='output.dot',
                        help='dot file name')

    args = parser.parse_args(['pkglist.txt', '--deps', '--path', '/home/pgigoux/work/ade2/support', '--dot'])
    # args = parser.parse_args()

    if len(args.input_file):
        dep_dict = process_dependencies(args.path, args.input_file)
        if args.deps:
            print_dependencies(dep_dict)
        else:
            build_dict = build_order(dep_dict)
            print_build_order(build_dict)

        if args.dot:
            generate_dot_output(args.dotfile, dep_dict)
    else:
        print('no input file')
        exit(1)

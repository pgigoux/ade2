import os
import re

PKG_PATH = '/home/pgigoux/work/ade2/support'
PKG_LIST = 'pkglist.txt'
IGNORE = ['epics-base', 're2c', 'gemini-ade', 'rpcgen', 'libtirpc', 'tdct', 'psmisc', '%{name}']
MATCH_REQ = '^Requires:'
MATCH_BUILD = '^BuildRequires:'
DEVEL = '-devel'


def spec_file(name: str):
    """
    Generate the spec file name from the package name
    :param name: package
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
    return os.path.join(PKG_PATH, name, f'{root}.spec')


def map_dependency(dep: str) -> str:
    if dep == 'geminipcre':
        return 'pcre'
    elif dep == 'geminicalc':
        return 'calc'
    else:
        return dep


def filter_line(line: str) -> set:
    """
    Return a set with the package dependencies. Remove -devel packages.
    :param line: input line
    :return: dependency set
    """
    line = line.replace(DEVEL, '')
    return {map_dependency(_) for _ in line.split()[1:] if _ not in IGNORE}


def process_file(file_name: str) -> tuple:
    """
    Process spec file
    :param file_name:
    :return:
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
    # print('--', req_list, build_list)
    return req_set, build_set


def process_package(name: str) -> tuple:
    file_name = spec_file(name)
    # print(file_name)
    r, b = process_file(file_name)
    return r, b


def process_dependencies(file_name: str) -> dict:
    d = {}
    try:
        f = open(file_name, 'r')
        for line in f:
            line = line.strip()
            d[line] = process_package(line)
        f.close()
        return d
    except IOError:
        print(f'{file_name} could not be processed')


def print_dictionary(d: dict):
    for key in sorted(d):
        r, b = d[key]
        if r or b:
            print(key, b)
            # print('\t', r)
            # print('\t', b)


def generate_dot_output(file_name: str, deps: dict):
    """
    :param file_name: output file name
    :param deps: dependency dictionary
    """
    f = open(file_name, 'w')
    f.write('digraph rpms {\n')
    for key in deps:
        r, b = deps[key]
        if b:
            for dep in b:
                f.write(key + f' -> {dep};\n')
        else:
            f.write(key + ';\n')
    f.write('}\n')
    f.close()


def print_order(deps: dict):
    level = 0
    d = {level: set()}

    name_set = {_ for _ in deps}

    # Build the set of packages with no dependencies (level 0)
    for name in name_set:
        r, b = deps[name]
        if not b:
            d[level].add(name)
    pending_set = name_set - d[level]
    # print('no deps', sorted(d[level]))
    # print('pending', sorted(pending_set))

    while len(pending_set) > 0 and level < 10:
        level += 1
        d[level] = set()
        # print('--', level, sorted(pending_set))
        for name in pending_set:
            r, b = deps[name]
            # print('=', b)
            if len(pending_set.intersection(b)) == 0:
                d[level].add(name)
            # print(level, name, b, d[level])
        pending_set = pending_set - d[level]
        # print('    ', sorted(d[level]))

    print('Packages with no dependencies:')
    print(' ', sorted(d[0]))
    print('Build order:')
    for key in d:
        print(f' level: {key} {sorted(d[key])}')


# def print_build_order(deps: dict):
#     level = 0
#     d = {level: []}
#     name_list = [_ for _ in deps]
#
#     for name in name_list:
#         r, b = deps[name]
#         if not b:
#             d[level].append(name)
#             name_list.remove(name)
#     print('no deps', d)
#
#     print('name_list', name_list)
#
#     while len(name_list) > 0:
#         level += 1
#         d[level] = []
#
#         for name in name_list:
#             print('--', name)
#             r, b = deps[name]
#             print('b', b)
#             found = False
#             for dep in b:
#                 if dep in d[level - 1] and dep not in name_list:
#                     print(f'{dep} found')
#                     found = True
#             if found:
#                 d[level].append(name)
#                 name_list.remove(name)
#                 print('remove', name, name_list)
#         print(level, d[level])
#         if level > 5:
#             break


# print(name_list)
# while len(name_list) > 0:
#     for name in name_list:
#         r, b = deps[name]
#         if not b:
#             if level not in d:
#                 d[level] = name
#             else:
#                 d[level].append(name)
#             name_list.remove(name)
#         else:
#
#     level += 1


if __name__ == '__main__':
    dep_dict = process_dependencies(PKG_LIST)
    print_dictionary(dep_dict)
    print('---')
    print_order(dep_dict)
    # print_build_order(dep_dict)
    # generate_dot_output('test.dot', dep_dict)

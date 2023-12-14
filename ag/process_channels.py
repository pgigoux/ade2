#!/usr/bin/env python3
import re

FILE_LIST = [
    'ag_top.db',
    'ag_sadtop.db',
    'agSeqSadTop.db',
    'agSeqTopGS.db',
    'oiwfsgwTop.db'
]

MACROS = {
    r'${ag}': 'tag:',
    r'${pwfs1}': 'pwfs1:',
    r'${pwfs2}': 'pwfs2:',
    r'${oiwfs}': 'oiwfs:',
    r'${hrwfs}': 'thrwfs:',
    r'${f2top}': 'f2:',
    r'${tcs}': 'tcs:'
}


def print_list(input_list: list):
    for e in input_list:
        print(e)
    print(len(input_list))


def print_dict(d: dict, csv_output=True):
    for key in sorted(d):
        if csv_output:
            s = str(d[key]).replace('{', '').replace('}', '').replace('\'', '').replace(' ','')
            # print(s)
            print(f'{key},{s}')
        else:
            print(f'{key:30}: {sorted(d[key])}')
    print(len(d))


def not_reference(s: str) -> bool:
    """
    Determine whether a field value is not a reference to another record:
    empty stings, numbers,
    :param s: input string
    :return: True if it's a constant value, False otherwise
    """
    if len(s) == 0 or re.search('^[-+]?[0-9]+', s) or re.search('#', s) or re.search('@', s):
        return True
    else:
        return False


def substitute_macros(line: str, macros: dict) -> str:
    """
    Substitute macros in a given line
    :param line: input line
    :param macros: dictionary with macro substitutions
    :return: line with macros replaced with actual values
    """
    # m = MACRO_PATTERN.search(line)
    m = re.search(r'\${.*}', line)
    output_line = line
    if m is not None:
        m_str = m.group()
        if m_str in macros:
            output_line = line.replace(m_str, MACROS[m_str], )
    # print(output_line)
    return output_line


def reference_field(field_name: str) -> bool:
    """
    Determine whether the field is one of the possible links to other records
    :param field_name:
    :return: True if it is, False otherwise.
    """
    ref_list = (r'INP', r'OUT', r'DOL', r'LNK', r'FLNK', r'SELL', r'NVL', r'S.LK')
    for ref in ref_list:
        if re.search(ref, field_name):
            return True
    return False


def process_fields(file_list: list, record_list: list) -> dict:
    output_dict = {}
    for file_name in file_list:
        print('++', file_name)
        with open(file_name, 'r') as f:
            for line in f:
                line = substitute_macros(line.strip(), MACROS)
                # line = line.strip()
                # print(line)
                if re.search(r'^field', line):
                    # print(line)
                    name, value = line.split(',', 1)
                    field_name = re.sub(r'^field\(', '', name)
                    # print(f'{name} - {value} ({field_name})')
                    if reference_field(field_name):
                        field_value = re.sub(r' .*', '', re.sub(r'"', '', re.sub(r'"\)', '', value)))
                        if not_reference(field_value):
                            continue
                        # print(line)
                        if '.' in field_value:
                            ref_record, ref_field = field_value.split('.')
                        else:
                            ref_record, ref_field = field_value, 'VAL'
                        # try:
                        #     ref_record, ref_field = field_value.split('.')
                        # except ValueError:
                        #     ref_field = ''
                        # print(ref_record, ref_field)
                        if ref_record not in record_list:
                            if ref_record not in output_dict:
                                output_dict[ref_record] = set()
                            output_dict[ref_record].add(ref_field)

                        # print(f'n={name}, v={value} - fn=[{field_name}] fv=[{field_value}] - rr=[{ref_record}] rf=[{ref_field}]')

    return output_dict


def get_record_names(file_list: list) -> list:
    """
    Get the list of record name in all the database files
    :param file_list: list of database files
    :return: record name list
    """
    output_list = []
    for file_name in file_list:
        with open(file_name, 'r') as f:
            print('--', file_name)
            for line in f:
                line = substitute_macros(line.strip(), MACROS)
                if re.search(r'^record', line):
                    record_name = re.sub(r'".*', '', re.sub(r'record.*,"', '', line))
                    output_list.append(record_name)
    return output_list


if __name__ == '__main__':
    # substitute_macros('record(ai,"${oiwfs}ins1fgdiag2vald")')
    # process_file_list(FILE_LIST)
    record_list = get_record_names(FILE_LIST)
    field_dict = process_fields(FILE_LIST, record_list)
    print_dict(field_dict)


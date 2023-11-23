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

# Alarm fields that should be present in all records.
# The description is in this list as well as additional data.
# The description is included for convenience
field_list = (ALARM_SEVERITY, ALARM_STATUS, NEW_ALARM_SEVERITY,
              NEW_ALARM_STATUS, DESCRIPTION)

# Alarm message fields. They are not supported in older versions of EPICS
message_field_list = (ALARM_MESSAGE, NEW_ALARM_MESSAGE)

# Alarm fields that have a numeric (enum) value
numeric_field_list = (ALARM_SEVERITY, ALARM_STATUS, NEW_ALARM_SEVERITY, NEW_ALARM_STATUS)

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


def default_alarm_dictionary() -> dict:
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


def ignore_alarms(d: dict, include_udf=False) -> bool:
    """
    Decide whether a dictionary containing the alarms for a given record
    can be ignored, either because they are all NO_ALARM or because the
    flag to ignore UDF alarms is set.
    :param d: dictionary with alarms values
    :param include_udf: include udf alarms?
    :return: True if the alarms can be ignored, False otherwise
    """
    no_alarm = (d[ALARM_SEVERITY] == SEVERITY_NO_ALARM,
                d[ALARM_STATUS] == STATUS_NO_ALARM,
                d[NEW_ALARM_SEVERITY] == SEVERITY_NO_ALARM)
    if all(no_alarm) or (d[ALARM_STATUS] == 'UDF' and not include_udf):
        return True
    else:
        return False


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


def print_line(record_name: str, d: dict, csv_output=False):
    """
    Format and print report line
    :param record_name: record name
    :param d: dictionary with the alarm values
    :param csv_output: csv output?
    """
    if csv_output:
        line = record_name
        for field_name in short_fields + long_fields:
            line += f',{d[field_name]}'
    else:
        line = f'{record_name:30}'
        for field_name in short_fields:
            line += f'{d[field_name]:15}'
        for field_name in long_fields:
            line += f'{d[field_name]:25}'
    print(line)

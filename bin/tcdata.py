#!/usr/bin/env python

""" standard """
import json
import operator
import os
import sys
import traceback
""" third-party """
""" custom """
from tcex import TcEx

tcex = TcEx()

tcex.parser.add_argument('--data_file', help='The file containing the data to stage.', required=True)
tcex.parser.add_argument('--validate', action='store_true', help='Validate instead of stage.')
args = tcex.args

def data_endswith(db_data, user_data):
    """Validate data ends with user data"""
    if db_data.endswith(user_data):
        return True
    return False

def data_in(db_data, user_data):
    """Validate data in user data"""
    if db_data in user_data:
        return True
    return False

def data_it(db_data, user_type):
    """Validate data is Type"""
    data_type = {
        'array': list,
        'dict': dict,
        'entity': dict,
        'list': list,
        'str': str,
        'string': str
    }
    # user_type_tuple = tuple([data_type[t] for t in user_types])
    # if isinstance(db_data, user_type_tuple):
    if data_type.get(user_type) is not None:
        if isinstance(db_data, data_type.get(user_type)):
            return True
    return False

def data_not_in(db_data, user_data):
    """Validate data not in user data"""
    if db_data not in user_data:
        return True
    return False

# def data_not_none(db_data, user_data=None):
#     """Validate data is not None"""
#     if db_data is not None:
#         return True
#     return False

def data_startswith(db_data, user_data):
    """Validate data starts with user data"""
    if db_data.startswith(user_data):
        return True
    return False


def main():
    """ """
    # Define common comparison operators
    operators = {
        'eq': operator.eq,
        'ew': data_endswith,
        'ge': operator.ge,
        'gt': operator.gt,
        'in': data_in,
        'ni': data_not_in,
        'it': data_it,  # is type
        'lt': operator.lt,
        'le': operator.le,
        'ne': operator.ne,
        # 'nn': data_not_none,
        'sw': data_startswith
    }

    data_file = os.path.abspath(args.data_file)
    if os.path.isfile(data_file):  # double check file exist
        # for windows (untested)
        try:
            f = os.fdopen(os.open(data_file, os.O_RDWR | os.O_BINARY | os.O_TEMPORARY), 'rb')
        except AttributeError:
            f = open(data_file, 'r')
        data_array = json.load(f)
        f.close()

        for ddata in data_array:
            variable = ddata.get('variable')
            user_data = ddata.get('data')
            if isinstance(user_data, int):
                user_data = str(ddata.get('data'))
            user_operator = ddata.get('operator', 'eq')

            if args.validate:
                tcex.log.info('Validating output variable {}'.format(variable))
                # read from store
                db_data = tcex.playbook.read(variable)
                tcex.log.debug('Validation Data: ({}) [{}]'.format(user_data, type(user_data)))
                tcex.log.debug('DB Data: ({}) [{}]'.format(db_data, type(db_data)))

                if user_operator in operators and operators.get(user_operator)(db_data, user_data):
                    tcex.log.info('Validation was successful')
                else:
                    tcex.log.error('Validation failed for variable: {}, Operator: {}'.format(
                        variable, user_operator))
                    sys.exit(1)
            else:
                tcex.log.info('Creating variable {}'.format(variable))
                tcex.playbook.create(variable, user_data)

    else:
        tcex.log.error('Could not open data file ({}).'.format(data_file))

    sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        # TODO: Update this, possibly raise
        print(traceback.format_exc())
        tcex.log.error('Generic Failure ({}).'.format(traceback.format_exc()))
        sys.exit(1)
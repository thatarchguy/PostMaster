"""
Author: StackFocus
File: utils.py
Purpose: General helper utils
"""

import os
from re import match
from mmap import mmap
from json import loads
from ..errors import ValidationError
from postmaster import db
from postmaster.models import Configs


def is_file_writeable(file):
    """ Returns a bool based on if a file is writable or not
    """
    if os.path.isfile(file):
        return os.access(file, os.W_OK)
    else:
        absolute_path = os.path.abspath(file)
        dir_of_file = os.path.dirname(absolute_path)
        return os.access(dir_of_file, os.W_OK)


def is_config_update_valid(setting, value, valid_value_regex):
    """ A helper function for the update_config function on the /configs/<int:config_id> PUT route.
    A bool is returned based on if the users input is valid.
    """
    if match(valid_value_regex, value):

        if setting == 'Log File':
            if not is_file_writeable(value):
                raise ValidationError('The specified log path is not writable')
            else:
                # Enables Mail Database Auditing when the log file is set
                mail_db_auditing = Configs.query.filter_by(setting='Mail Database Auditing').first()
                mail_db_auditing.value = 'True'
                db.session.add(mail_db_auditing)

        elif setting == 'Login Auditing' or setting == 'Mail Database Auditing':
            log_file = Configs.query.filter_by(setting='Log File').first().value

            if not log_file:
                raise ValidationError('The log file must be set before auditing can be enabled')

        elif setting == 'Enable LDAP Authentication':
            ldap_string = Configs.query.filter_by(setting='AD Server LDAP String').first().value
            ad_domain = Configs.query.filter_by(setting='AD Domain').first().value
            ad_group = Configs.query.filter_by(setting='AD PostMaster Group').first().value

            if not (ldap_string and ad_domain and ad_group):
                raise ValidationError('The LDAP settings must be configured before LDAP authentication is enabled')

        elif setting == 'AD Server LDAP String' or setting == 'AD Domain' or setting == 'AD PostMaster Group':
            ldap_enabled = Configs.query.filter_by(setting='Enable LDAP Authentication').first().value

            if ldap_enabled == 'True' and not value:
                raise ValidationError('LDAP authentication must be disabled when deleting LDAP configuration items')

        return True
    else:
        if setting == 'Minimum Password Length':
            raise ValidationError('An invalid minimum password length was supplied. The value must be between 1-25.')

        raise ValidationError('An invalid setting value was supplied')

def get_logs_dict(numLines=50, reverseOrder=False):
    """
    Returns the JSON formatted log file as a dict
    """
    logPath = Configs.query.filter_by(setting='Log File').first().value
    if logPath and os.path.exists(logPath):
        logFile = open(logPath, mode='r+')

        try:
            mmapHandler = mmap(logFile.fileno(), 0)
        except ValueError as e:
            if str(e) == 'cannot mmap an empty file':
                # If the file is empty, return empty JSON
                return {'items': [], }
            else:
                raise ValidationError(
                    'There was an error opening "{0}"'.format(
                        os.getcwd().replace('\\', '/') + '/' + logPath))

        newLineCount = 0
        # Assigns currentChar to the last character of the file
        currentChar = mmapHandler.size() - 1

        # If the file ends in a new line, add 1 more line to process
        # for mmapHandler[currentChar:].splitlines() later on
        if mmapHandler[currentChar] == '\n':
            numLines += 1

        # While the number of lines iterated is less than numLines
        # and the beginning of the file hasn't been reached
        while newLineCount < numLines and currentChar > 0:
            # If a new line character is found, this means
            # the current line has ended
            if mmapHandler[currentChar] == '\n':
                newLineCount += 1
            # Subtract from the charcter count to read the previous character
            currentChar -= 1

        # If the beginning of the file hasn't been reached,
        # strip the preceeding new line character
        if currentChar > 0:
            currentChar += 2

        # Create the list
        logs = mmapHandler[currentChar:].splitlines()

        # Close the log file
        mmapHandler.close()
        logFile.close()

        if reverseOrder:
            logs = list(reversed(logs))

        return {'items': [loads(log) for log in logs], }
    else:
        raise ValidationError('The log file could not be found')

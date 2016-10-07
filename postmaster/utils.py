"""
Author: StackFocus
File: utils.py
Purpose: General helper utils
"""

import ldap
from struct import unpack
from re import search, sub, IGNORECASE
from json import dumps
from datetime import datetime
from os import path
from wtforms.validators import StopValidation as WtfStopValidation
from postmaster import app, db, models, bcrypt
from postmaster.errors import ValidationError


def maildb_auditing_enabled():
    """ Returns a bool based on if mail db auditing is enabled
    """
    auditing_setting = models.Configs.query.filter_by(
        setting='Mail Database Auditing').first().value
    return auditing_setting == 'True'


def login_auditing_enabled():
    """ Returns a bool based on if mail db auditing is enabled
    """
    auditing_setting = models.Configs.query.filter_by(
        setting='Login Auditing').first().value
    return auditing_setting == 'True'


def json_logger(category, admin, message):
    """ Takes a category (typically error or audit), a log message and the responsible
    user. It then appends it with an ISO 8601 UTC timestamp to a JSON formatted log file
    """
    log_path = app.config.get('LOG_LOCATION')
    if log_path and ((category == 'error') or
       (category == 'audit' and maildb_auditing_enabled()) or
       (category == 'auth' and login_auditing_enabled())):
        try:
            with open(log_path, mode='a+') as log_file:
                log_file.write("{}\n".format(dumps(
                    {
                        'category': category,
                        'message': message,
                        'admin': admin,
                        'timestamp': datetime.utcnow().isoformat() + 'Z'
                    },
                    sort_keys=True)))
                log_file.close()
        except IOError:
            raise ValidationError('The log could not be written to "{0}". '
                                  'Verify that the path exists and is writeable.'.format(path.abspath(log_path)))


def add_default_configuration_settings():
    """ Adds the default configuration settings to the database if they aren't present.
    This is to be used from manage.py when creating the database.
    """
    if not models.Configs.query.filter_by(setting='Minimum Password Length').first():
        min_pwd_length = models.Configs()
        min_pwd_length.setting = 'Minimum Password Length'
        min_pwd_length.value = '8'
        min_pwd_length.regex = '^([0-9]|[1][0-9]|[2][0-5])$'
        db.session.add(min_pwd_length)

    if not models.Configs.query.filter_by(setting='Account Lockout Threshold').first():
        account_lockout_threshold = models.Configs()
        account_lockout_threshold.setting = 'Account Lockout Threshold'
        account_lockout_threshold.value = '5'
        account_lockout_threshold.regex = '^([0-9]|[1][0-9]|[2][0-5])$'
        db.session.add(account_lockout_threshold)

    if not models.Configs.query.filter_by(setting='Account Lockout Duration in Minutes').first():
        account_lockout_duration = models.Configs()
        account_lockout_duration.setting = 'Account Lockout Duration in Minutes'
        account_lockout_duration.value = '30'
        account_lockout_duration.regex = '^([1-9]|[1-9][0-9])$'
        db.session.add(account_lockout_duration)

    if not models.Configs.query.filter_by(setting='Reset Account Lockout Counter in Minutes').first():
        reset_account_lockout = models.Configs()
        reset_account_lockout.setting = 'Reset Account Lockout Counter in Minutes'
        reset_account_lockout.value = '30'
        reset_account_lockout.regex = '^([1-9]|[1-9][0-9])$'
        db.session.add(reset_account_lockout)

    if not models.Configs.query.filter_by(setting='Login Auditing').first():
        login_auditing = models.Configs()
        login_auditing.setting = 'Login Auditing'
        login_auditing.value = 'False'
        login_auditing.regex = '^(True|False)$'
        db.session.add(login_auditing)

    if not models.Configs.query.filter_by(setting='Mail Database Auditing').first():
        mail_db_auditing = models.Configs()
        mail_db_auditing.setting = 'Mail Database Auditing'
        mail_db_auditing.value = 'False'
        mail_db_auditing.regex = '^(True|False)$'
        db.session.add(mail_db_auditing)

    if not models.Configs.query.filter_by(setting='Enable LDAP Authentication').first():
        ldap_auth = models.Configs()
        ldap_auth.setting = 'Enable LDAP Authentication'
        ldap_auth.value = 'False'
        ldap_auth.regex = '^(True|False)$'
        db.session.add(ldap_auth)

    if not models.Configs.query.filter_by(setting='AD Server LDAP String').first():
        ad_server = models.Configs()
        ad_server.setting = 'AD Server LDAP String'
        ad_server.regex = '^(.*)$'
        db.session.add(ad_server)

    if not models.Configs.query.filter_by(setting='AD Domain').first():
        ad_domain = models.Configs()
        ad_domain.setting = 'AD Domain'
        ad_domain.regex = '^(.*)$'
        db.session.add(ad_domain)

    if not models.Configs.query.filter_by(setting='AD PostMaster Group').first():
        ad_group = models.Configs()
        ad_group.setting = 'AD PostMaster Group'
        ad_group.regex = '^(.*)$'
        db.session.add(ad_group)

    if not models.Admins.query.first():
        admin = models.Admins().from_json(
            {'username': 'admin', 'password': 'PostMaster', 'name': 'Default Admin'})
        db.session.add(admin)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()


def increment_failed_login(username):
    """ Increments the failed_attempts value, updates the last_failed_date value, and sets the unlock_date value
    if necessary on the admin
    """
    admin = models.Admins.query.filter_by(username=username).first()
    if not admin:
        raise ValidationError('The admin does not exist in the database.')

    account_lockout_threshold = int(models.Configs.query.filter_by(setting='Account Lockout Threshold').first().value)
    reset_account_lockout_counter = int(models.Configs.query.filter_by(
        setting='Reset Account Lockout Counter in Minutes').first().value)
    account_lockout_duration = int(models.Configs.query.filter_by(
        setting='Account Lockout Duration in Minutes').first().value)

    admin.increment_failed_login(account_lockout_threshold, reset_account_lockout_counter, account_lockout_duration)

    try:
        db.session.add(admin)
        db.session.commit()

        # If the account is locked out, log an audit message
        if not admin.is_unlocked():
            audit_message = '"{0}" is now locked out and will be unlocked in {1} minute(s)'.format(
                username, account_lockout_duration)
            json_logger('audit', username, audit_message)
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', username,
            'The following error occurred when incrementing the failed login attempts field on "{0}": {1}'.format(
                username, str(e)))
        ValidationError('A database error occurred. Please try again.', 'error')
    finally:
        db.session.close()


def clear_lockout_fields_on_user(username):
    """ Clears the lockout fields (failed_attempts, last_failed_date, unlock_date) on a user. This is used
    to unlock a user, or when a user logs in successfully.
    """
    admin = models.Admins.query.filter_by(username=username).first()

    if not admin:
        raise ValidationError('The admin does not exist in the database.')

    try:
        admin.clear_lockout_fields()
        db.session.add(admin)
        db.session.commit()
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', username,
            'The following error occurred when try to clear out the lockout fields: {0}'.format(str(e)))
        ValidationError('A database error occurred. Please try again.', 'error')
    finally:
        db.session.close()


def reset_admin_password(username, new_password):
    """ Resets an admin's password with one supplied
    """
    admin = models.Admins.query.filter_by(username=username).first()

    if not admin:
        raise ValidationError('The admin does not exist in the database.')

    admin.set_password(new_password)

    try:
        db.session.add(admin)
        db.session.commit()
        json_logger('audit', 'CLI', ('The administrator "{0}" had their password changed via the CLI'.format(username)))
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', username,
            'The following error occurred when try to reset an admin\'s password: {0}'.format(str(e)))
        ValidationError('A database error occurred. Please try again.', 'error')
    finally:
        db.session.close()


def add_ldap_user_to_db(username, display_name):
    """ Adds an LDAP user stub in the Admins table of the database for flask_login
    """
    try:
        new_admin = models.Admins().ldap_user_from_json({
            'username': username,
            'name': display_name
        })
        db.session.add(new_admin)
        db.session.commit()
        json_logger('audit', username,
                    '"{0}" was added as an LDAP admin to the database"'.format(username))
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', username,
            'The following error occurred when adding an LDAP admin: {0}'.format(str(e)))
        ValidationError('A database error occurred. Please try again.', 'error')
    finally:
        db.session.close()


def validate_wtforms_password(form, field):
        """ Validates the password from a wtforms object
        """
        username = form.username.data
        password = form.password.data
        two_factor = form.two_factor.data if form.two_factor.data else None

        try:
            if form.auth_source.data == 'PostMaster User':
                admin = models.Admins.query.filter_by(username=username, source='local').first()
                if admin:
                    if admin.is_unlocked():
                        if bcrypt.check_password_hash(admin.password, password):
                            if admin.otp_active:
                                if not admin.verify_totp(two_factor):
                                    raise WtfStopValidation('2 Factor token was incorrect')
                            form.admin = admin
                            return
                        else:
                            increment_failed_login(username)
                    else:
                        raise WtfStopValidation('The user is currently locked out. Please try logging in again later.')
                json_logger(
                    'auth', username,
                    'The administrator "{0}" entered an incorrect username or password'.format(
                        username))
                raise WtfStopValidation('The username or password was incorrect')
            else:
                ad_object = AD()
                if ad_object.login(username, password):
                    if ad_object.check_group_membership():
                        friendly_username = ad_object.get_loggedin_user()
                        display_name = ad_object.get_loggedin_user_display_name()
                        if not models.Admins.query.filter_by(username=friendly_username, source='ldap').first():
                            add_ldap_user_to_db(friendly_username, display_name)
                        admin = models.Admins.query.filter_by(username=friendly_username, source='ldap').first()
                        if admin.otp_active:
                            if not admin.verify_totp(two_factor):
                                raise WtfStopValidation('2 Factor token was incorrect')
                        form.admin = admin
        except ADException as e:
            raise WtfStopValidation(e.message)


def get_wtforms_errors(form):
    """ Returns the errors from wtforms in a single string with new lines
    """
    i = 0
    error_messages = ''
    for field, errors in form.errors.items():
        for error in errors:
            # If this isn't the first error, add a new line for the next error
            if i != 0:
                error_messages += '\n'
            # If the error is from DataRequired, make the error more user friendly
            if 'This field is required' in error:
                error_messages += 'The {0} was not provided'.format(
                    getattr(form, field).label.text.lower())
            else:
                error_messages += error
            i += 1

    return error_messages


class ADException(Exception):
    """ A custom exception for the PostMasterLDAP class
    """
    pass


class AD(object):
    """ A class that handles all the Active Directory tasks for the Flask app
    """
    ldap_connection = None
    ldap_server = None
    ldap_admin_group = None
    domain = None

    def __init__(self):
        """ The constructor that initializes the ldap_connection object
        """
        ldap_enabled = models.Configs().query.filter_by(setting='Enable LDAP Authentication').first()
        if ldap_enabled is not None and ldap_enabled.value == 'True':
            ldap_server = models.Configs().query.filter_by(setting='AD Server LDAP String').first()
            domain = models.Configs().query.filter_by(setting='AD Domain').first()
            ldap_admin_group = models.Configs().query.filter_by(setting='AD PostMaster Group').first()

            if ldap_server is not None and search('LDAP[S]?:\/\/(.*?)\:\d+', ldap_server.value, IGNORECASE):
                self.ldap_server = ldap_server.value

                if domain is not None and ldap_admin_group is not None:
                    self.domain = domain.value
                    self.ldap_admin_group = ldap_admin_group.value

                    if search('[LDAPS]', self.ldap_server, IGNORECASE):
                        # Force SSL and don't use TLS
                        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

                    self.ldap_connection = ldap.initialize(self.ldap_server)
                    self.ldap_connection.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
                    # Turn off referrals
                    self.ldap_connection.set_option(ldap.OPT_REFERRALS, 0)
                else:
                    json_logger('error', 'NA', 'The LDAP Admin Group is not configured properly')
                    raise ADException('LDAP authentication is not properly configured')
            else:
                json_logger('error', 'NA',
                            'The LDAP server string is not configured or isn\'t properly formatted')
                raise ADException('The LDAP server could not be contacted')
        else:
            json_logger('error', 'NA', 'An LDAP authentication attempt was made but it is currently disabled')
            raise ADException('LDAP authentication is not enabled')

    def __del__(self):
        """ The destructor that disconnects from LDAP
        """
        self.ldap_connection.unbind()

    def login(self, username, password):
        """ Uses the supplied username and password to bind to LDAP and returns a boolean
        """
        # If a UPN, domain, or distinguishedName was provided then use that, otherwise form the UPN
        if '@' in username or '\\' in username or search('CN=', username, IGNORECASE):
            bind_username = username
        else:
            bind_username = username + '@' + self.domain

        try:
            self.ldap_connection.simple_bind_s(
                bind_username,
                password
            )
            return True

        except ldap.INVALID_CREDENTIALS:
            json_logger(
                'auth', bind_username,
                'The administrator "{0}" entered an incorrect username or password via LDAP'.format(bind_username))
            raise ADException('The username or password was incorrect')
        except ldap.SERVER_DOWN:
            json_logger(
                'error', bind_username,
                'The LDAP server "{0}" could not be contacted'.format(self.ldap_server))
            raise ADException('The LDAP server could not be contacted')
        except Exception as e:
            json_logger(
                'error', bind_username,
                'The LDAP bind could not complete with the following message: {0}'.format(e.message))
            raise ADException('The connection to the LDAP server failed. Please try again.')

    def get_loggedin_user(self):
        """ Returns the logged in username without the domain
        """
        # Check if the ldap_connection is in a logged in state
        if self.ldap_connection.whoami_s():
            # AD returns the username as DOMAIN\username, so this gets the sAMAccountName
            return sub(r'(^.*(?<=\\))', '', self.ldap_connection.whoami_s())

        return None

    def get_loggedin_user_display_name(self):
        """ Returns the display name or the object name if the display name is not available of the logged on user
        """
        # Check if the ldap_connection is in a logged in state
        username = self.get_loggedin_user()
        if username:
            # Get the base distinguished name based on the domain name
            base_dn = 'dc=' + (self.domain.replace('.', ',dc='))
            search_filter = '(&(objectClass=user)(sAMAccountName={0}))'.format(username)
            # Returns the displayName and name of the user
            result = self.ldap_connection.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter, ['displayName', 'name'])

            # Make sure the search returned results
            if result and result[0][0] is not None:
                # Makes sure the displayName attribute was returned
                if 'displayName' in result[0][1]:
                    return result[0][1]['displayName'][0]
                elif 'name' in result[0][1]:
                    return result[0][1]['name'][0]
            else:
                json_logger(
                    'error', username,
                    'The display name of the user "{0}" could not be found'.format(username))
                raise ADException('There was an error searching the LDAP server. Please try again.')
        else:
            raise ADException('You must be logged into LDAP to search')

        return None

    def get_distinguished_name(self, sAMAccountName):
        """ Gets the distinguishedName of an LDAP object based on the sAMAccountName
        """
        # Check if the ldap_connection is in a logged in state
        if self.ldap_connection.whoami_s():

            if sAMAccountName:
                # Get the base distinguished name based on the domain name
                base_dn = 'dc=' + (self.domain.replace('.', ',dc='))
                search_filter = '(&(sAMAccountName={0}))'.format(sAMAccountName)
                search_result = self.ldap_connection.search_s(base_dn, ldap.SCOPE_SUBTREE,
                                                              search_filter, ['distinguishedName'])
                # Make sure the search returned results
                if search_result and search_result[0][0] is not None:
                    return search_result[0][0]
            return None
        else:
            raise ADException('You must be logged into LDAP to search')

    def check_nested_group_membership(self, group_sAMAccountName, user_sAMAccountName):
        """ Checks the nested group membership of a user by supplying the sAMAccountName, and verifies if the user is a
        part of that supplied group. A list with the groups the user is a member of will be returned
        """
        # Check if the ldap_connection is in a logged in state
        if self.ldap_connection.whoami_s():
            group_dn = self.get_distinguished_name(group_sAMAccountName)
            user_dn = self.get_distinguished_name(user_sAMAccountName)

            if group_dn and user_dn:
                # Get the base distinguished name based on the domain name
                base_dn = 'dc=' + (self.domain.replace('.', ',dc='))
                search_filter = '(member:1.2.840.113556.1.4.1941:={0})'.format(user_dn)
                search_result = self.ldap_connection.search_s(base_dn, ldap.SCOPE_SUBTREE,
                                                              search_filter, ['distinguishedName'])
                for group in search_result:
                    if group[0] == group_dn:
                        return True
            return False
        else:
            raise ADException('You must be logged into LDAP to search')

    def get_primary_group_dn_of_user(self, user_sAMAccountName):
        """ Returns the distinguished name of the primary group of the user
        """
        # Check if the ldap_connection is in a logged in state
        username = self.get_loggedin_user()
        if username:
            if user_sAMAccountName:
                # Get the base distinguished name based on the domain name
                base_dn = 'dc=' + (self.domain.replace('.', ',dc='))
                search_filter = '(&(sAMAccountName={0}))'.format(user_sAMAccountName)
                search_result = self.ldap_connection.search_s(base_dn, ldap.SCOPE_SUBTREE,
                                                              search_filter, ['primaryGroupID'])
                # Make sure the search returned results
                if search_result and search_result[0][0] and 'primaryGroupID' in search_result[0][1]:
                    primary_group_id = search_result[0][1]['primaryGroupID'][0]
                else:
                    json_logger(
                        'error', username,
                        'The primaryGroupID of the user "{0}" could not be found').format(user_sAMAccountName)
                    raise ADException('There was an error searching the LDAP server. Please try again.')

                # Returns the displayName and name of the user
                domain_result = self.ldap_connection.search_s(base_dn, ldap.SCOPE_BASE)
                # Make sure the objectSid was returned
                if domain_result and domain_result[0][0] is not None and 'objectSid' in domain_result[0][1]:
                    domain_sid = domain_result[0][1]['objectSid'][0]
                else:
                    json_logger(
                        'error', username,
                        'The SID of the domain could not be found')
                    raise ADException('There was an error searching the LDAP server. Please try again.')

                search_filter = '(&(objectClass=group)(objectSid={0}-{1}))'.format(
                    self.sid2str(domain_sid), primary_group_id)
                primary_group_result = self.ldap_connection.search_s(base_dn, ldap.SCOPE_SUBTREE,
                                                                     search_filter, ['distinguishedName'])
                if primary_group_result and primary_group_result[0][0]:
                    return primary_group_result[0][0]
            return None
        else:
            raise ADException('You must be logged into LDAP to search')

    def check_group_membership(self):
        """ Checks the group membership of the logged on user. This will return True if the user is a member of
        the Administrator group set in the database
        """
        # Check if the ldap_connection is in a logged in state
        if self.ldap_connection.whoami_s():
            # AD returns the username as DOMAIN\username, so this gets the sAMAccountName
            username = sub(r'(^.*(?<=\\))', '', self.ldap_connection.whoami_s())
            # Get the distinguished name of the admin group in the database
            group_distinguished_name = self.get_distinguished_name(self.ldap_admin_group)

            if not group_distinguished_name:
                json_logger(
                    'error', username,
                    'The PostMaster Admin group "{0}" could not be found'.format(self.ldap_admin_group))
                raise ADException('There was an error searching LDAP. Please try again.')

            if self.check_nested_group_membership(self.ldap_admin_group, username):
                return True

            # If the user was not a member of the group, check to see if the admin group is the primary group
            # of the user which is not included in memberOf (this is typically Domain Users)
            primary_group_dn = self.get_primary_group_dn_of_user(username)
            if primary_group_dn and group_distinguished_name.upper() == primary_group_dn.upper():
                return True

            json_logger(
                'auth', username,
                ('The LDAP user "{0}" authenticated but the login failed because they weren\'t '
                    'a PostMaster administrator').format(username))
            raise ADException('The user account is not authorized to login to PostMaster')
        else:
            raise ADException('You must be logged into LDAP to search')

    def sid2str(self, sid):
        """ Converts a hexadecimal string returned from the LDAP query to a
        string version of the SID in format of S-1-5-21-1270288957-3800934213-3019856503-500
        This function was based from: http://www.gossamer-threads.com/lists/apache/bugs/386930
        """
        srl = ord(sid[0])
        number_sub_id = ord(sid[1])
        iav = unpack('!Q', '\x00\x00' + sid[2:8])[0]
        sub_ids = [
            unpack('<I', sid[8+4*i:12+4*i])[0]
            for i in range(number_sub_id)
        ]

        return 'S-{0}-{1}-{2}'.format(srl, iav, '-'.join([str(s) for s in sub_ids]))

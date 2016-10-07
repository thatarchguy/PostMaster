import string
import random
import json
from mock import patch
import onetimepass
from datetime import datetime, timedelta
from postmaster import app, db
from postmaster.models import Configs, Admins


class TestMailDbFunctions:

    def test_aliases_get(self, loggedin_client):
        rv = loggedin_client.get("/api/v1/aliases", follow_redirects=True)
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 200

    def test_aliases_add_fail_domain_managed(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/aliases", data=json.dumps(
            {"source": "pickles@test123.com", "destination": "rawr@test123.com"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "not managed" in rv.data

    def test_aliases_add_fail_not_current(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/aliases", data=json.dumps(
            {"source": "pickles@postmaster.com", "destination": "rawr@postmaster.com"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "not a current" in rv.data

    def test_aliases_add_fail_source_empty(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/aliases", data=json.dumps(
            {"source": "", "destination": "rawr@postmaster.com"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "The source email was not specified" in rv.data

    def test_aliases_add_fail_destination_empty(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/aliases", data=json.dumps(
            {"source": "rawr@postmaster.com", "destination": ""}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "The destination email was not specified" in rv.data

    def test_aliases_add_pass(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/aliases", data=json.dumps(
            {"source": "rawr@postmaster.com", "destination": "email@postmaster.com"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 201

    def test_aliases_update_source_pass(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/aliases/2", data=json.dumps(
            {"source": "somealias@postmaster.com"}))
        assert rv.status_code == 200

    def test_aliases_update_destination_pass(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/aliases/2", data=json.dumps(
            {"destination": "email@postmaster.org"}))
        assert rv.status_code == 200

    def test_alias_update_fail_source_or_destination_not_supplied(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/aliases/2", data=json.dumps(
            {"someotherdata": "aomeotherdata"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "The source or destination was not supplied in the request" in rv.data

    def test_aliases_delete_pass(self, loggedin_client):
        rv = loggedin_client.delete("/api/v1/aliases/2", follow_redirects=True)
        assert rv.status_code == 204

    def test_users_get(self, loggedin_client):
        rv = loggedin_client.get("/api/v1/users", follow_redirects=True)
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 200

    def test_users_add_fail_not_valid(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/users", data=json.dumps(
            {"email": "picklesasda", "password": "som3passw0rd"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "not a valid" in rv.data

    def test_users_add_fail_domain_managed(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/users", data=json.dumps(
            {"email": "pickles@test123.com", "password": "som3passw0rd"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "not managed" in rv.data

    def test_users_add_fail_password_empty(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/users", data=json.dumps(
            {"email": "pickles@test123.com", "password": ""}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "The password was not specified" in rv.data

    def test_users_add_fail_email_empty(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/users", data=json.dumps(
            {"email": "", "password": "som3passw0rd"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "The email address was not specified" in rv.data

    def test_users_update_fail_password_not_supplied(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/users/2", data=json.dumps(
            {"someotherdata": "pickles"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "The password was not supplied in the request" in rv.data

    def test_users_add_pass(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/users", data=json.dumps(
            {"email": "pickles@postmaster.com", "password": "som3passw0rd"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 201

    def test_users_update_pass(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/users/2", data=json.dumps(
            {"password": "som3passw0rd123"}))
        assert rv.status_code == 200

    def test_users_delete_pass(self, loggedin_client):
        rv = loggedin_client.delete("/api/v1/users/2", follow_redirects=True)
        assert rv.status_code == 204

    def test_domains_get(self, loggedin_client):
        rv = loggedin_client.get("/api/v1/domains", follow_redirects=True)
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 200

    def test_users_add_fail_domain_missing(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/domains", data=json.dumps(
            {"lol": "what"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "not specified" in rv.data

    def test_domains_add_fail_already_exists(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/domains", data=json.dumps(
            {"name": "postmaster.com"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "already exists" in rv.data

    def test_domains_add_fail_name_empty(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/domains", data=json.dumps(
            {"name": ""}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "The domain name was not specified" in rv.data

    def test_domains_add_pass(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/domains", data=json.dumps(
            {"name": "".join((random.choice(string.ascii_uppercase + string.digits) for _ in range(6))) + ".com"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 201

    def test_domains_delete_pass(self, loggedin_client):
        rv = loggedin_client.delete("/api/v1/domains/2", follow_redirects=True)
        assert rv.status_code == 204

    def test_admins_get_one(self, loggedin_client):
        rv = loggedin_client.get("/api/v1/admins/1", follow_redirects=True)
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 200

    def test_admins_get_all(self, loggedin_client):
        rv = loggedin_client.get("/api/v1/admins", follow_redirects=True)
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 200

    def test_admins_add_pass(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/admins", data=json.dumps(
            {"username": "user_admin@postmaster.com", "password": "som3passw0rd", "name": "Test Admin"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 201

    def test_admins_add_fail_duplicate(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/admins", data=json.dumps(
            {"username": "admin", "password": "som3passw0rd", "name": "Test Admin"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "already exists" in rv.data

    def test_admins_add_fail_no_username(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/admins", data=json.dumps(
            {"password": "som3passw0rd", "name": "Test Admin"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "The username was not specified" in rv.data

    def test_admins_add_fail_no_password(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/admins", data=json.dumps(
            {"username": "user_admin2@postmaster.com", "name": "Test Admin"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "The password was not specified" in rv.data

    def test_admins_add_fail_no_name(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/admins", data=json.dumps(
            {"username": "user_admin2@postmaster.com", "password": "som3passw0rd"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "The name was not specified" in rv.data

    def test_admins_update_password_pass(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/admins/2", data=json.dumps(
            {"password": "som3passw0rd123"}))
        assert rv.status_code == 200

    def test_admins_update_name_pass(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/admins/2", data=json.dumps(
            {"name": "Some New Name"}))
        assert rv.status_code == 200

    def test_admins_update_username_pass(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/admins/2", data=json.dumps(
            {"username": "newemail@postmaster.com"}))
        assert rv.status_code == 200

    def test_admins_update_fail(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/admins/2", data=json.dumps(
            {"randomkey": "random_value"}))
        assert rv.status_code == 400
        assert "The username, password, or name was not supplied in the request" in rv.data

    def test_admins_delete_pass(self, loggedin_client):
        rv = loggedin_client.delete("/api/v1/admins/2", follow_redirects=True)
        assert rv.status_code == 204

    def test_admins_unlock(self, loggedin_client):
        test_admin = Admins().from_json({
            'username': 'test_admin',
            'password': 'S0meG00dP@ss',
            'name': 'Test Admin'
        })
        test_admin.failed_attempts = 5
        test_admin.last_failed_date = datetime.utcnow()
        test_admin.unlock_date = datetime.utcnow() + timedelta(minutes=30)

        db.session.add(test_admin)
        db.session.commit()

        new_test_admin = Admins.query.filter_by(username='test_admin').one()
        rv = loggedin_client.put("/api/v1/admins/{0}/unlock".format(new_test_admin.id), follow_redirects=True)
        assert rv.status_code == 200

    def test_admins_unlock_not_found(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/admins/50/unlock", follow_redirects=True)
        assert rv.status_code == 404

    def test_admins_2factor_qrcode(self, loggedin_client):
        rv = loggedin_client.get("/api/v1/admins/1/2factor/qrcode")
        assert rv.status_code == 200

    def test_admins_2factor_status(self, loggedin_client):
        rv = loggedin_client.get("/api/v1/admins/1/2factor")
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 200

    def test_admins_2factor_update_fail(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/admins/1/2factor")
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "invalid request" in rv.data

    def test_admins_2factor_enable_fail(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/admins/1/2factor", data=json.dumps({"enabled": "True"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "Cannot enable 2 factor" in rv.data

    def test_admins_2factor_verify_invalid(self, loggedin_client):
        test_admin = Admins().from_json({
            'username': 'test_admin',
            'password': 'S0meG00dP@ss',
            'name': 'Test Admin'
        })
        test_admin.generate_otp_secret()
        test_admin.otp_active = 1

        db.session.add(test_admin)
        db.session.commit()
        rv = loggedin_client.post("/api/v1/admins/{0}/2factor/verify".format(test_admin.id), data=json.dumps({"code": 123456}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "invalid code" in rv.data

    def test_admins_2factor_verify_secret_fail(self, loggedin_client):
        test_admin = Admins().from_json({
            'username': 'test_admin',
            'password': 'S0meG00dP@ss',
            'name': 'Test Admin'
        })

        db.session.add(test_admin)
        db.session.commit()
        rv = loggedin_client.post("/api/v1/admins/{0}/2factor/verify".format(test_admin.id), data=json.dumps({"code": 123456}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "2 Factor Secret" in rv.data

    def test_admins_2factor_verify_valid(self, loggedin_client):
        test_admin = Admins().from_json({
            'username': 'test_admin',
            'password': 'S0meG00dP@ss',
            'name': 'Test Admin'
        })
        test_admin.generate_otp_secret()
        test_admin.otp_active = 1

        db.session.add(test_admin)
        db.session.commit()

        secret = test_admin.otp_secret
        token = onetimepass.get_totp(secret)
        assert test_admin.verify_totp(token)
        rv = loggedin_client.post("/api/v1/admins/{0}/2factor/verify".format(test_admin.id), data=json.dumps({"code": token}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert "Success" in rv.data
        assert rv.status_code == 200
        assert "Success" in rv.data

    def test_configs_get_one(self, loggedin_client):
        rv = loggedin_client.get("/api/v1/configs/1", follow_redirects=True)
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 200

    def test_configs_get_all(self, loggedin_client):
        rv = loggedin_client.get("/api/v1/configs", follow_redirects=True)
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 200

    def test_configs_update_pass(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/configs/10", data=json.dumps(
            {"value": "An Admin Group"}))
        assert rv.status_code == 200

    def test_configs_update_fail(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/configs/5", data=json.dumps(
            {"someparameter": "somevalue"}))
        assert rv.status_code == 400
        assert 'An invalid setting value was supplied' in rv.data

    @patch('os.access', return_value=False)
    def test_configs_enable_login_auditing_log_write_fail(self, mock_os_access, loggedin_client):
        rv = loggedin_client.put("/api/v1/configs/5", data=json.dumps(
            {"value": "True"}))
        assert rv.status_code == 400
        assert 'The log could not be written to' in rv.data

    @patch('os.access', return_value=True)
    def test_configs_enable_login_auditing_log_write_pass(self, mock_os_access, loggedin_client):
        rv = loggedin_client.put("/api/v1/configs/5", data=json.dumps(
            {"value": "True"}))
        assert rv.status_code == 200

    @patch('os.access', return_value=False)
    def test_configs_enable_maildb_auditing_log_write_fail(self, mock_os_access, loggedin_client):
        rv = loggedin_client.put("/api/v1/configs/6", data=json.dumps(
            {"value": "True"}))
        assert rv.status_code == 400
        assert 'The log could not be written to' in rv.data

    @patch('os.access', return_value=True)
    def test_configs_enable_maildb_auditing_log_write_pass(self, mock_os_access, loggedin_client, tmpdir):
        log_file = tmpdir.join('postmaster.log')
        app.config['LOG_LOCATION'] = str(log_file)
        rv = loggedin_client.put("/api/v1/configs/6", data=json.dumps(
            {"value": "True"}))
        # Clean up the temp directory created by the test
        tmpdir.remove()
        assert rv.status_code == 200

    def test_configs_min_pwd_update_pass(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/configs/1", data=json.dumps(
            {"value": "7"}))
        assert rv.status_code == 200

    def test_configs_min_pwd_update_fail(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/configs/1", data=json.dumps(
            {"value": "9999"}))
        assert rv.status_code == 400
        assert 'An invalid value was supplied. The value must be between 0-25.' in rv.data

    def test_configs_update_enable_ldap_no_server(self, loggedin_client):
        """ Tests the update_config function (PUT route for configs) when LDAP is set to enabled
        but an LDAP server is not configured. A return value of an error is expected.
        """
        # Set the AD Server LDAP String to empty
        ldap_string = Configs.query.filter_by(setting='AD Server LDAP String').first()
        old_ldap_string_value = ldap_string.value
        ldap_string.value = None
        db.session.add(ldap_string)
        db.session.commit()

        rv = loggedin_client.put("/api/v1/configs/7", data=json.dumps(
            {"value": "True"}))

        # Reverts to the previous AD Server LDAP String
        ldap_string.value = old_ldap_string_value
        db.session.add(ldap_string)
        db.session.commit()

        assert rv.status_code == 400
        assert 'The LDAP settings must be configured before LDAP authentication is enabled' in rv.data

    def test_configs_update_empty_ldap_server_when_ldap_enabled(self, loggedin_client):
        """ Tests the update_config function (PUT route for configs) when the LDAP server is set to empty
        but LDAP is enabled. A return value of an error is expected.
        """
        # Enables LDAP Authentication
        ldap_enabled = Configs.query.filter_by(setting='Enable LDAP Authentication').first()
        old_ldap_enabled_value = ldap_enabled.value
        ldap_enabled.value = 'True'
        db.session.add(ldap_enabled)
        db.session.commit()

        rv = loggedin_client.put("/api/v1/configs/8", data=json.dumps(
            {"value": ""}))

        # Reverts to the previous state
        ldap_enabled.value = old_ldap_enabled_value
        db.session.add(ldap_enabled)
        db.session.commit()

        assert rv.status_code == 400
        assert 'LDAP authentication must be disabled when deleting LDAP configuration items' in rv.data

"""
Author: StackFocus
File: admins.py
Purpose: The admins API for PostMaster which allows
an admin to create, delete, and update admins
"""

from flask import request
from flask_login import login_required, current_user
import pyqrcode
from StringIO import StringIO
from postmaster import db
from postmaster.models import Admins
from postmaster.utils import json_logger, clear_lockout_fields_on_user
from ..decorators import json_wrap, paginate
from ..errors import ValidationError, GenericError
from . import apiv1


@apiv1.route("/admins", methods=["GET"])
@login_required
@paginate()
def get_admins():
    """ Queries all the admin users in Admins, and returns paginated JSON
    """
    if request.args.get('search'):
        return Admins.query.filter(Admins.username.ilike(
            "%{0}%".format(request.args.get('search')))).order_by(Admins.username)
    return Admins.query.order_by(Admins.username)


@apiv1.route("/admins/<int:admin_id>", methods=["GET"])
@login_required
@json_wrap
def get_admin(admin_id):
    """ Queries a specific admin user based on ID in Admins, and returns JSON
    """
    return Admins.query.get_or_404(admin_id)


@apiv1.route('/admins', methods=['POST'])
@login_required
@json_wrap
def new_admin():
    """ Creates a new admin user in Admins, and returns HTTP 201 on success
    """
    admin = Admins().from_json(request.get_json(force=True))
    db.session.add(admin)
    try:
        db.session.commit()
        json_logger(
            'audit', current_user.username,
            'The administrator "{0}" was created successfully'.format(
                admin.username))
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', current_user.username,
            'The following error occurred in new_admin: {0}'.format(str(e)))
        raise GenericError('The admininstrator could not be created')
    finally:
        db.session.close()
    return {}, 201


@apiv1.route('/admins/<int:admin_id>', methods=['DELETE'])
@login_required
@json_wrap
def delete_admin(admin_id):
    """ Deletes an admin user by ID in Admins, and returns HTTP 204 on success
    """
    admin = Admins.query.get_or_404(admin_id)
    if db.session.query(Admins).count() == 1:
        raise GenericError(
            'There needs to be at least one adminstrator')
    db.session.delete(admin)
    try:
        db.session.commit()
        json_logger('audit', current_user.username,
                    'The administrator "{0}" was deleted successfully'.format(
                        admin.username))
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', current_user.username,
            'The following error occurred in delete_admin: {0}'.format(str(e)))
        raise GenericError('The administrator could not be deleted')
    finally:
        db.session.close()
    return {}, 204


@apiv1.route('/admins/<int:admin_id>', methods=['PUT'])
@login_required
@json_wrap
def update_admin(admin_id):
    """ Updates an admin user by ID in Admins, and returns HTTP 200 on success
    """
    auditMessage = ''
    admin = Admins.query.get_or_404(admin_id)
    json = request.get_json(force=True)

    if 'username' in json:
        newUsername = json['username'].lower()
        if Admins.query.filter_by(username=newUsername).first() is None:
            auditMessage = 'The administrator "{0}" had their username changed to "{1}"'.format(
                admin.username, newUsername)
            admin.username = newUsername
        else:
            ValidationError('The username supplied already exists')
    elif 'password' in json:
        admin.set_password(json['password'])
        auditMessage = 'The administrator "{0}" had their password changed'.format(
            admin.username)
    elif 'name' in json:
        auditMessage = 'The administrator "{0}" had their name changed to "{1}"'.format(admin.username, admin.name)
        admin.name = json['name']
    else:
        raise ValidationError(
            'The username, password, or name was not supplied in the request')

    try:
        db.session.add(admin)
        db.session.commit()
        json_logger('audit', current_user.username, auditMessage)
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', current_user.username,
            'The following error occurred in update_admin: {0}'.format(str(e)))
        raise GenericError('The administrator could not be updated')
    finally:
        db.session.close()
    return {}, 200


@apiv1.route('/admins/<int:admin_id>/unlock', methods=['PUT'])
@login_required
@json_wrap
def unlock_admin(admin_id):
    """ Unlocks an admin by ID in Admins, and returns HTTP 200 on success
    """
    admin = Admins.query.get_or_404(admin_id)
    clear_lockout_fields_on_user(admin.username)
    return {}, 200


@apiv1.route('/admins/<int:admin_id>/2factor', methods=['GET'])
@login_required
@json_wrap
def twofactor_status(admin_id):
    """ Returns if 2 factor is enabled or not

        This information is in the main user route,
        but I added it here as a stub for the URI.
    """
    admin = Admins.query.get_or_404(admin_id)
    return dict(enabled=admin.otp_active)


@apiv1.route('/admins/<int:admin_id>/2factor', methods=['PUT'])
@login_required
@json_wrap
def twofactor_disable(admin_id):
    """ Disable 2 factor using API.

        Enabling 2 factor from this route is not possible.
    """
    admin = Admins.query.get_or_404(admin_id)
    status = request.get_json(force=True).get('enabled')
    if status:
        if status.lower() == "false":
            admin.otp_active = False
            try:
                db.session.add(admin)
                db.session.commit()
            except ValidationError as e:
                raise e
            except Exception as e:
                db.session.rollback()
                json_logger(
                    'error', current_user.username,
                    'The following error occurred in twofactor_disable: {0}'.format(str(e)))
                raise GenericError('The administrator could not be updated')
            return dict(enabled=admin.otp_active)
        elif status.lower() == "true":
            raise GenericError("Cannot enable 2 factor from this route - see docs")
    raise GenericError("An Invalid parameter was supplied")


@apiv1.route('/admins/<int:admin_id>/2factor/qrcode', methods=['GET'])
@login_required
def qrcode(admin_id):
    """ Presents the user with a QR code to scan to setup 2 factor authentication
    """
    # render qrcode for FreeTOTP
    admin = Admins.query.get_or_404(admin_id)
    if admin.id != current_user.id:
        raise GenericError('You may not view other admin\'s QR codes')
    if admin.otp_active:
        return ('', 204)
    admin.generate_otp_secret()
    try:
        db.session.add(admin)
        db.session.commit()
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', current_user.username,
            'The following error occurred in qrcode: {0}'.format(str(e)))
        raise GenericError('The administrator could not be updated')
    url = pyqrcode.create(admin.get_totp_uri())
    stream = StringIO()
    url.svg(stream, scale=5)
    return stream.getvalue().encode('utf-8'), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@apiv1.route('/admins/<int:admin_id>/2factor/verify', methods=['POST'])
@login_required
@json_wrap
def verify_qrcode(admin_id):
    """ Verifies if the 2 factor token provided is correct

        This will enable 2 factor for a user.
    """
    admin = Admins.query.get_or_404(admin_id)
    if request.get_json(force=True).get('code'):
        if not admin.otp_secret:
            raise GenericError("The 2 Factor Secret has not been generated yet")
        if admin.verify_totp(request.get_json(force=True).get('code')):
            if not admin.otp_active:
                audit_message = 'The administrator "{0}" enabled 2 factor'.format(
                    admin.username)
                admin.otp_active = True
                try:
                    db.session.add(admin)
                    db.session.commit()
                    json_logger('audit', current_user.username, audit_message)
                except ValidationError as e:
                    raise e
                except Exception as e:
                    db.session.rollback()
                    json_logger(
                        'error', current_user.username,
                        'The following error occurred in verify_qrcode: {0}'.format(str(e)))
                    raise GenericError('The administrator could not be updated')
            return dict(status="Success")
        else:
            raise GenericError("An invalid code was supplied")
    else:
        raise ValidationError("The code was not supplied")

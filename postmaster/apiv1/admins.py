"""
Author: StackFocus
File: admins.py
Purpose: The admins API for PostMaster which allows
an admin to create, delete, and update admins
"""

from flask import request
from flask_login import login_required, current_user
from postmaster import db, bcrypt
from postmaster.models import Admins, Configs
from postmaster.utils import json_logger
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
            db.session.add(admin)
        else:
            ValidationError('The username supplied already exists')
    elif 'password' in json:
        minPwdLength = int(Configs.query.filter_by(
            setting='Minimum Password Length').first().value)
        if len(json['password']) < minPwdLength:
            raise ValidationError(
                'The password must be at least {0} characters long'.format(
                    minPwdLength))
        auditMessage = 'The administrator "{0}" had their password changed'.format(
            admin.username)
        admin.password = bcrypt.generate_password_hash(json['password'])
        db.session.add(admin)
    elif 'name' in json:
        auditMessage = 'The administrator "{0}" had their name changed to "{1}"'.format(
            admin.username, admin.name)
        admin.name = json['name']
        db.session.add(admin)
    else:
        raise ValidationError(
            'The username, password, or name was not supplied in the request')

    try:
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

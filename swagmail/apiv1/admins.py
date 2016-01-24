"""
Author: Swagger.pro
File: admins.py
Purpose: The admins API for SwagMail which allows
an admin to create, delete, and update admins
"""

from flask import request
from flask_login import login_required, current_user
from swagmail import db, bcrypt
from swagmail.models import Admins
from ..decorators import json_wrap, paginate
from ..errors import ValidationError, GenericError
from . import apiv1
from utils import json_logger


@apiv1.route("/admins", methods=["GET"])
@login_required
@paginate()
def get_admins():
    """ Queries all the admin users in Admins, and returns paginated JSON
    """
    if request.args.get('search'):
        return Admins.query.filter(Admins.email.ilike(
            "%{0}%".format(request.args.get('search'))))
    return Admins.query


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
            'audit', current_user.email,
            'The administrator "{0}" was created successfully'.format(
                admin.email))
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', current_user.email,
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
    db.session.delete(admin)
    try:
        db.session.commit()
        json_logger('audit', current_user.email,
                    'The administrator "{0}" was deleted successfully'.format(
                        admin.email))
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', current_user.email,
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

    if 'email' in json:
        if Admins.query.filter_by(email=json['email']).first() is None:
            auditMessage = 'The administrator "{0}" had their email changed to "{1}"'.format(
                admin.email, json['email'])
            admin.email = json['email']
            db.session.add(admin)
        else:
            ValidationError('The email supplied already exists')
    elif 'password' in json:
        auditMessage = 'The administrator "{0}" had their password changed'.format(
            admin.email)
        admin.password = bcrypt.generate_password_hash(json['password'])
        db.session.add(admin)
    elif 'name' in json:
        auditMessage = 'The administrator "{0}" had their name changed to "{1}"'.format(
            admin.email, admin.name)
        admin.name = json['name']
        db.session.add(admin)
    else:
        raise ValidationError(
            'The email, password, or name was not supplied in the request')

    try:
        db.session.commit()
        json_logger('audit', current_user.email, auditMessage)
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', current_user.email,
            'The following error occurred in update_admin: {0}'.format(str(e)))
        raise GenericError('The administrator could not be updated')
    finally:
        db.session.close()
    return {}, 200

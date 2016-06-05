"""
Author: StackFocus
File: users.py
Purpose: The users API for PostMaster which allows
an admin to create, delete, and update users
"""

from flask import request
from flask_login import login_required, current_user
from postmaster import db
from postmaster.models import VirtualUsers, VirtualAliases, Configs
from postmaster.utils import json_logger
from ..decorators import json_wrap, paginate
from ..errors import ValidationError, GenericError
from . import apiv1


@apiv1.route("/users", methods=["GET"])
@login_required
@paginate()
def get_users():
    """ Queries all the users in VirtualUsers, and returns paginated JSON
    """
    if request.args.get('search'):
        return VirtualUsers.query.filter(VirtualUsers.email.ilike(
            "%{0}%".format(request.args.get('search')))).order_by(
                VirtualUsers.email)
    return VirtualUsers.query.order_by(VirtualUsers.email)


@apiv1.route("/users/<int:user_id>", methods=["GET"])
@login_required
@json_wrap
def get_user(user_id):
    """ Queries a specific user based on ID in VirtualUsers, and returns JSON
    """
    return VirtualUsers.query.get_or_404(user_id)


@apiv1.route('/users', methods=['POST'])
@login_required
@json_wrap
def new_user():
    """ Creates a new user in VirtualUsers, and returns HTTP 201 on success
    """
    user = VirtualUsers().from_json(request.get_json(force=True))
    db.session.add(user)
    try:
        db.session.commit()
        json_logger(
            'audit', current_user.username,
            'The user "{0}" was created successfully'.format(user.email))
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', current_user.username,
            'The following error occurred in new_user: {0}'.format(str(e)))
        raise GenericError('The user could not be created')
    finally:
        db.session.close()
    return {}, 201


@apiv1.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
@json_wrap
def delete_user(user_id):
    """ Deletes a user by ID in VirtualUsers, and returns HTTP 204 on success
    """
    user = VirtualUsers.query.get_or_404(user_id)

    aliases = VirtualAliases.query.filter_by(destination=user.email).all()
    if aliases:
        for alias in aliases:
            db.session.delete(alias)
    db.session.delete(user)
    try:
        db.session.commit()
        json_logger(
            'audit', current_user.username,
            'The user "{0}" was deleted successfully'.format(user.email))
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', current_user.username,
            'The following error occurred in delete_user: {0}'.format(str(e)))
        raise GenericError('The user could not be deleted')
    finally:
        db.session.close()
    return {}, 204


@apiv1.route('/users/<int:user_id>', methods=['PUT'])
@login_required
@json_wrap
def update_user(user_id):
    """ Updates a user by ID in VirtualUsers, and returns HTTP 200 on success
    """
    user = VirtualUsers.query.get_or_404(user_id)
    json = request.get_json(force=True)

    if 'password' in json:
        minPwdLength = int(Configs.query.filter_by(
            setting='Minimum Password Length').first().value)
        if len(json['password']) < minPwdLength:
            raise ValidationError(
                'The password must be at least {0} characters long'.format(
                    minPwdLength))
        user.password = VirtualUsers().encrypt_password(json['password'])
        auditMessage = 'The user "{0}" had their password changed'.format(
            user.email)
        db.session.add(user)
    else:
        raise ValidationError('The password was not supplied in the request')
    try:
        db.session.commit()
        json_logger('audit', current_user.username, auditMessage)
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', current_user.username,
            'The following error occurred in update_user: {0}'.format(str(e)))
        raise GenericError('The user could not be updated')
    finally:
        db.session.close()
    return {}, 200

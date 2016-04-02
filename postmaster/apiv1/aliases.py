"""
Author: StackFocus
File: aliases.py
Purpose: The aliases API for PostMaster which allows
an admin to create, delete, and update aliases
"""

from flask import request
from flask_login import login_required, current_user
from postmaster import db
from postmaster.models import VirtualAliases
from postmaster.utils import json_logger
from ..decorators import json_wrap, paginate
from ..errors import ValidationError, GenericError
from . import apiv1
from sqlalchemy import or_


@apiv1.route("/aliases", methods=["GET"])
@login_required
@paginate()
def get_aliases():
    """ Queries all the aliases in VirtualAliases, and returns paginated JSON
    """
    if request.args.get('search'):
        return VirtualAliases.query.filter(
            or_(VirtualAliases.destination.ilike(
                "%{0}%".format(request.args.get('search'))),
                VirtualAliases.source.ilike(
                    "%{0}%".format(request.args.get('search'))))).order_by(
                        VirtualAliases.source)
    return VirtualAliases.query.order_by(VirtualAliases.source)


@apiv1.route("/aliases/<int:alias_id>", methods=["GET"])
@login_required
@json_wrap
def get_alias(alias_id):
    """ Queries a specific alias based on ID in VirtualAliases, and returns JSON
    """
    return VirtualAliases.query.get_or_404(alias_id)


@apiv1.route('/aliases', methods=['POST'])
@login_required
@json_wrap
def new_alias():
    """ Creates a new alias in VirtualAliases, and returns HTTP 201 on success
    """
    alias = VirtualAliases().from_json(request.get_json(force=True))
    db.session.add(alias)
    try:
        db.session.commit()
        json_logger(
            'audit', current_user.username,
            'The alias "{0}" was created successfully'.format(alias.source))
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', current_user.username,
            'The following error occurred in new_alias: {0}'.format(str(e)))
        raise GenericError('The alias could not be created')
    finally:
        db.session.close()
    return {}, 201


@apiv1.route('/aliases/<int:alias_id>', methods=['DELETE'])
@login_required
@json_wrap
def delete_alias(alias_id):
    """ Deletes an alias by ID in VirtualAliases, and returns HTTP 204 on success
    """
    alias = VirtualAliases.query.get_or_404(alias_id)
    db.session.delete(alias)
    try:
        db.session.commit()
        json_logger(
            'audit', current_user.username,
            'The alias "{0}" was deleted successfully'.format(alias.source))
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', current_user.username,
            'The following error occurred in delete_alias: {0}'.format(str(e)))
        raise GenericError('The alias could not be deleted')
    finally:
        db.session.close()
    return {}, 204


@apiv1.route('/aliases/<int:alias_id>', methods=['PUT'])
@login_required
@json_wrap
def update_alias(alias_id):
    """ Updates an alias by ID in VirtualAliases, and returns HTTP 200 on success
    """
    alias = VirtualAliases.query.get_or_404(alias_id)
    json = request.get_json(force=True)

    if 'source' in json:
        newSource = json['source'].lower()
        if VirtualAliases().validate_source(newSource):
            auditMessage = 'The alias "{0}" had their source changed to "{1}"'.format(
                alias.source, newSource)
            alias.source = newSource
            db.session.add(alias)
    elif 'destination' in json:
        newDestination = json['destination'].lower()
        if VirtualAliases().validate_destination(newDestination):
            auditMessage = 'The alias "{0}" had their destination changed to "{1}"'.format(
                alias.source, newDestination)
            alias.destination = newDestination
            db.session.add(alias)
    else:
        raise ValidationError(
            'The source or destination was not supplied in the request')

    try:
        db.session.commit()
        json_logger('audit', current_user.username, auditMessage)
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', current_user.username,
            'The following error occurred in update_alias: {0}'.format(str(e)))
        raise GenericError('The alias could not be updated')
    finally:
        db.session.close()
    return {}, 200

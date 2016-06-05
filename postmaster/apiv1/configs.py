"""
Author: StackFocus
File: configs.py
Purpose: The configs API for PostMaster which
allows an admin to update PostMaster configurations
"""

from flask import request
from flask_login import login_required, current_user
from postmaster import db
from postmaster.models import Configs
from postmaster.utils import json_logger
from ..decorators import json_wrap, paginate
from ..errors import ValidationError, GenericError
from . import apiv1
from utils import is_config_update_valid


@apiv1.route("/configs", methods=["GET"])
@login_required
@paginate()
def get_configs():
    """ Queries all the settings in Configs, and returns paginated JSON
    """
    return Configs.query


@apiv1.route("/configs/<int:config_id>", methods=["GET"])
@login_required
@json_wrap
def get_config(config_id):
    """ Queries a specific setting based on ID in Configs, and returns JSON
    """
    return Configs.query.get_or_404(config_id)


@apiv1.route('/configs/<int:config_id>', methods=['PUT'])
@login_required
@json_wrap
def update_config(config_id):
    """ Updates a config by ID in Configs, and returns HTTP 200 on success
    """
    config = Configs.query.get_or_404(config_id)
    json = request.get_json(force=True)

    if 'value' in json and is_config_update_valid(config.setting, json['value'], config.regex):
        audit_message = 'The setting "{0}" was set from "{1}" to "{2}"'.format(config.setting, config.value,
                                                                               json['value'])
        config.value = json['value']
        db.session.add(config)
    else:
        raise ValidationError('An invalid setting value was supplied')

    try:
        db.session.commit()
        json_logger('audit', current_user.username, audit_message)
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', current_user.username,
            'The following error occurred in update_config: {0}'.format(str(
                e)))
        raise GenericError('The configuration could not be updated')
    finally:
        db.session.close()
    return {}, 200

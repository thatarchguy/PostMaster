"""
Author: StackFocus
File: domains.py
Purpose: The domains API for PostMaster which allows
an admin to create, and delete domains
"""

from flask import request
from flask_login import login_required, current_user
from postmaster import db
from postmaster.models import VirtualDomains
from postmaster.utils import json_logger
from ..decorators import json_wrap, paginate
from ..errors import ValidationError, GenericError
from . import apiv1


@apiv1.route("/domains", methods=["GET"])
@login_required
@paginate()
def get_domains():
    """ Queries all the domains in VirtualDomains, and returns paginated JSON
    """
    if request.args.get('search'):
        return VirtualDomains.query.filter(VirtualDomains.name.ilike(
            "%{0}%".format(request.args.get('search')))).order_by(
                VirtualDomains.name)
    return VirtualDomains.query.order_by(VirtualDomains.name)


@apiv1.route("/domains/<int:domain_id>", methods=["GET"])
@login_required
@json_wrap
def get_domain(domain_id):
    """ Queries a specific domain based on ID in VirtualDomains, and returns JSON
    """
    return VirtualDomains.query.get_or_404(domain_id)


@apiv1.route('/domains', methods=['POST'])
@login_required
@json_wrap
def new_domain():
    """ Creates a new domain in VirtualDomains, and returns HTTP 201 on success
    """
    domain = VirtualDomains().from_json(request.get_json(force=True))
    db.session.add(domain)
    try:
        db.session.commit()
        json_logger(
            'audit', current_user.username,
            'The domain "{0}" was created successfully'.format(domain.name))
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', current_user.username,
            'The following error occurred in new_domain: {0}'.format(str(e)))
        raise GenericError('The domain could not be created')
    finally:
        db.session.close()
    return {}, 201


@apiv1.route('/domains/<int:domain_id>', methods=['DELETE'])
@login_required
@json_wrap
def delete_domain(domain_id):
    """ Deletes a domain by ID in VirtualDomains, and returns HTTP 204 on success
    """
    domain = VirtualDomains.query.get_or_404(domain_id)
    db.session.delete(domain)
    try:
        db.session.commit()
        json_logger(
            'audit', current_user.username,
            'The domain "{0}" was deleted successfully'.format(domain.name))
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', current_user.username,
            'The following error occurred in delete_domain: {0}'.format(str(
                e)))
        raise GenericError('The domain could not be deleted')
    finally:
        db.session.close()
    return {}, 204

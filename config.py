"""
Author: Swagger.pro
File: config.py
Purpose: config for the app
"""

HOST_NAME = 'mail.swagger.pro'

import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'swagmail.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# Make this random (used to generate session keys)
SECRET_KEY = '73Sjkadas%hASDe45@1238Due12jdodjfFDweq82348*(#89asdasdas'

"""
Dev
"""
HOST = '0.0.0.0'
DEBUG = True

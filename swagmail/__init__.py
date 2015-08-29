"""
Author: Swagger.pro
File: __init__.py
Purpose: initializes the application settings modules
"""

from flask import Flask, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from swagmail import views, models

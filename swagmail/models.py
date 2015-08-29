"""
Author: Swagger.pro
File: models.py
Purpose: database definitions for SQLAlchemy
"""
from swagmail import db

class virtual_domains(db.Model):
    """
    A table to house the email domains
    """
    __table_name__ = 'virtual_domains'
    __table_args__ = {
        'mysql_engine':'InnoDB',
        'mysql_charset':'utf8'
    }

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<virtual_domains(name=\'%s\')>' % (self.name)


class virtual_users(db.Model):
    """
    A table to house the email user accounts
    """
    __table_name__ = 'virtual_users'
    __table_args__ = {
        'mysql_engine':'InnoDB',
        'mysql_charset':'utf8'
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    domain_id = db.Column(db.Integer, db.ForeignKey('virtual_domains.id', ondelete='CASCADE'), nullable=False)
    password = db.Column(db.String(106), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self, domain_id, password, email):
        self.domain_id = domain_id
        self.password = password
        self.email = email

    def __repr__(self):
        return '<virtual_users(email=\'%s\')>' % (self.email)

class virtual_aliases(db.Model):
    """
    A table to house the email aliases
    """
    __table_name__ = 'virtual_aliases'
    __table_args__ = {
        'mysql_engine':'InnoDB',
        'mysql_charset':'utf8'
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    domain_id = db.Column(db.Integer, db.ForeignKey('virtual_domains.id', ondelete='CASCADE'), nullable=False)
    source = db.Column(db.String(100), unique=True, nullable=False)
    destination = db.Column(db.String(100), nullable=False)

    def __init__(self, source, destination):
        self.domain_id = domain_id
        self.source = password
        self.destination = email

    def __repr__(self):
        return '<virtual_aliases(source=\'%s\')>' % (self.source)

#!flask/bin/python
"""
Author: Swagger.pro
File: app.py
Purpose: runs the app!
"""

import os
from flask_script import Manager
from swagmail import app, db, models
from flask_migrate import Migrate, MigrateCommand

manager = Manager(app)
app.config.from_object('config')

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

@manager.command
def createdb():
    '''Runs the db init, db migrate, db upgrade commands automatically'''
    os.system('python manage.py db init')
    os.system('python manage.py db migrate')
    os.system('python manage.py db upgrade')


@manager.shell
def make_shell_context():
    ''' Returns app, db, models to the shell '''
    return dict(app=app, db=db, models=models)


@manager.command
def clean():
    '''Cleans the codebase'''

    if os.name == 'nt':
        commands = ["powershell.exe -Command \"@('*.pyc', '*.pyo', '*~', '__pycache__') |  Foreach-Object { Get-ChildItem -Filter $_ -Recurse | Remove-Item -Recurse -Force }\"",
                    "powershell.exe -Command \"@('swagmail.db', 'migrations') |  Foreach-Object { Get-ChildItem -Filter $_ | Remove-Item -Recurse -Force }\""]
    else:
        commands = ["find . -name '*.pyc' -exec rm -f {} \;",
                    "find . -name '*.pyo' -exec rm -f {} \;",
                    "find . -name '*~' -exec rm -f {} \;",
                    "find . -name '__pycache__' -exec rmdir {} \;",
                    "rm -f swagmail.db"]
    for command in commands:
        os.system(command)


if __name__ == "__main__":
    manager.run()

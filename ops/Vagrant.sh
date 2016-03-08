#!/bin/bash

usage() {
cat << EOF
Usage: $0
    This script will install PostMaster using Apache or nginx
Options:
    -p : Preserves the existing database

examples:
$0
$0 -p
EOF
}

PRESERVE=false

while getopts ":p" opt; do
    case $opt in
        p)
            PRESERVE=true
            ;;
        \?)
            >&2 echo "Invalid option: -$optarg"
            usage
            exit 1
            ;;
    esac
done

export DEBIAN_FRONTEND=noninteractive
debconf-set-selections <<< 'mysql-server mysql-server/root_password password vagrant'
debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password vagrant'

echo 'Updating the aptitude repository...'
apt-get -y update > /dev/null

packages=('python' 'python-pip' 'python-dev' 'libldap2-dev' 'libssl-dev' 'libsasl2-dev' 'libffi-dev' 'apache2' 'libapache2-mod-wsgi' 'mysql-server' 'libmysqlclient-dev')

for package in "${packages[@]}"
do
    if dpkg --get-selections | grep -q "^$package[[:space:]]*install$" >/dev/null
    then
        echo "Skipping the installation of $package"
    else
        echo "Installing $package..."
        apt-get install -y $package > /dev/null
    fi
done

echo 'Checking the python version...'
if [ $(python -V 2>&1 | grep -c "2.7") -eq 0 ]
then
    >&2 echo 'Please ensure that python 2.7 is installed and is the default python version'
    exit 1
fi

echo 'Creating the /opt/postmaster/logs directory'
mkdir /opt/postmaster/logs
chown www-data:www-data /opt/postmaster/logs

if ! [ -d '/opt/postmaster/env' ]
then
    echo 'Installing the virtual environment...'
    pip install virtualenv > /dev/null
    virtualenv /opt/postmaster/env > /dev/null
    source /opt/postmaster/env/bin/activate
else
    >&2 echo '/opt/postmaster/env already exists. Please make sure it is removed before rerunning the script'
    exit 1
fi

cd /opt/postmaster/git
echo 'Installing the Python packages required in the virtualenv...'
pip install -r requirements.txt > /dev/null

if [ $PRESERVE = false ]
then
    echo 'Creating the database...'
    python manage.py clean
    mysql -u root -pvagrant -e "CREATE DATABASE servermail"
    python manage.py setdburi 'mysql://root:vagrant@localhost:3306/servermail'
    python manage.py createdb
else
    echo 'Preserving the existing database'
fi

python manage.py generatekey

deactivate

if [ $(apachectl -M | grep -c 'wsgi_module') == 0 ]
then
    echo 'Enabling the wsgi module for Apache...'
    a2enmod -q wsgi > /dev/null
fi

if [ $(apachectl -S | grep -c "000-default.conf") != 0 ]
then
    echo 'Disabling 000-default.conf...'
    a2dissite 000-default.conf > /dev/null
fi

echo 'Copying and enabling the standard PostMaster Apache configuration...'
cp -f /opt/postmaster/git/ops/apache.conf /etc/apache2/sites-available/postmaster.conf
chmod 644 /etc/apache2/sites-available/postmaster.conf
a2ensite -q postmaster.conf > /dev/null

echo 'Restarting Apache...'
service apache2 restart > /dev/null

unset DEBIAN_FRONTEND

echo 'The installation has completed!'

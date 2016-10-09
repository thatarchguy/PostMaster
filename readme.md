[![Stories in Ready](https://badge.waffle.io/StackFocus/PostMaster.png?label=ready&title=Ready)](https://waffle.io/StackFocus/PostMaster)
## PostMaster [![Build Status](https://travis-ci.org/StackFocus/PostMaster.svg?branch=master)](https://travis-ci.org/StackFocus/PostMaster) ![Python](https://img.shields.io/badge/python-2.7-blue.svg) ![Flask](http://flask.pocoo.org/static/badges/made-with-flask-s.png)

### Overview

PostMaster is a beautiful web application to manage domains, users, and aliases on a Linux mail server.
After setting up a Linux mail server using the guide from [DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-configure-a-mail-server-using-postfix-dovecot-mysql-and-spamassassin) or [Linode](https://www.linode.com/docs/email/postfix/email-with-postfix-dovecot-and-mysql),
you start to see how tedious it can be to write raw SQL queries to add a new user to your Linux mail server.
PostMaster abstracts the domain, user, and alias management of your mail server into a responsive web interface, that is both simple to use and secure.

Although PostMaster was built to work with the database schema instructed in the [DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-configure-a-mail-server-using-postfix-dovecot-mysql-and-spamassassin) or [Linode](https://www.linode.com/docs/email/postfix/email-with-postfix-dovecot-and-mysql) guides,
paid support is available for the developers of PostMaster to customize it to work in your environment.

PostMaster is written by Kevin Law and Matthew Prahl.

### Features

* Add, remove, edit, or search domains, users, and aliases on a Linux mail server database
* Responsive web interface that works great on phones, tablets, and PCs
* Configurable auditing to keep track of changes
* Active Directory LDAP login support
* Friendly REST APIs to automate tasks
* Runs on Linux, Docker, and Windows

### Documentation

* [Change Log](https://stackfocus.github.io/PostMaster/ChangeLog/)
* [Installation and Configuration](https://stackfocus.github.io/PostMaster/)
* [API Basic Usage](http://stackfocus.github.io/PostMaster/API/ApiUsage/)
* [OpenAPI Specification](https://stackfocus.github.io/PostMaster/API/openAPI-spec.html)

### Screenshots

#### Dashboard:
![Dashboard](docs/imgs/Dashboard.png?raw=true)

#### Domains:
![Domains](docs/imgs/Domains.png?raw=true)

#### Users:
![Users](docs/imgs/Users.png?raw=true)

#### Aliases:
![Aliases](docs/imgs/Aliases.png?raw=true)

#### Configurations:
![Configurations](docs/imgs/Configurations.png?raw=true)

#### Search:
![Search](docs/imgs/Search.png?raw=true)

#### Mobile:
![Mobile](docs/imgs/Mobile.png?raw=true)

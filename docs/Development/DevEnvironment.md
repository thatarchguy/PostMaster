### Overview

PostMaster uses a combination of [Vagrant](https://www.vagrantup.com/) and [Ansible](https://www.ansible.com/) to
automate the setup of a development environment. In this scenario, Ansible is run entirely on the guest, and is thus
not required on the host system.

### Getting Started

- Install Vagrant by using your package manager or downloading it at:
[https://www.vagrantup.com/downloads.html](https://www.vagrantup.com/downloads.html)

- If you are using libvirt as your Vagrant provider (typical use case when
developing on Fedora), you must have the `sshfs` Vagrant plugin installed. To
install it, either run `sudo dnf install vagrant-sshfs` or
`vagrant install sshfs`.

- Run `vagrant up` to provision a Vagrant guest (development VM). Some operating
systems require running vagrant with `sudo` or administrative rights.

- Access PostMaster at [http://localhost:8080](http://localhost:8080) via your web browser

- Login using the username "admin" and the password "PostMaster"

- For more help with Vagrant, such as deleting and recreating your development environment, visit
[https://www.vagrantup.com/docs/cli/](https://www.vagrantup.com/docs/cli/)


Additional Information:

- The Vagrant guest is running a local MySQL instance which can be accessed locally with `mysql -uroot -pvagrant`
- The Vagrant guest is not running a mail server


#### Code Updates

The source code is located on the Vagrant guest at `/opt/postmaster/git`, but code changes made locally
will be automatically synced to the development VM via Vagrant.


#### Activate the virtualenv

On the guest, run the following:
```
$ source /opt/postmaster/env/bin/activate
```

#### Apply the Code Updates
Any Python file updates will require you to restart Apache on the Vagrant guest. To do so, run the following on
the Vagrant guest:

```
$ sudo service apache2 restart
```

#### Run the Unit Tests

On the Vagrant guest, activate the virtualenv (see above) and run the following in "/opt/postmaster/git":
```
$ py.test tests
```

#### Checking Logs

Logs can be found on the Vagrant guest at the following locations:
```
/opt/postmaster/logs/postmaster.log
/opt/postmaster/logs/postmaster.access.log
/opt/postmaster/logs/postmaster.error.log
```

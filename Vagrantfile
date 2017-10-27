# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
    config.vm.box = "boxcutter/ubuntu1604"
    config.vm.provider "libvirt" do |v, override|
        override.vm.box = "elastic/ubuntu-16.04-x86_64"
        override.vm.synced_folder "./", "/opt/postmaster/git", type: "sshfs", sshfs_opts_append: "-o nonempty"
    end
    config.vm.network "forwarded_port", guest: 5000, host: 8080
    config.vm.synced_folder "./", "/opt/postmaster/git"
    config.vm.provision "shell", inline: "apt-get update && apt-get install -y git"
    config.vm.provision "ansible_local" do |ansible|
        ansible.playbook = "ops/ansible/deploy.yml"
        ansible.galaxy_role_file = "ops/ansible/vagrant-requirements.yml"
        ansible.sudo = true
        ansible.extra_vars = {
            postmaster_install_mysql: true,
            postmaster_vagrant_install: true,
            postmaster_secret_key: 'ChangeMe',
            postmaster_db_user: 'vagrant',
            postmaster_db_password: 'vagrant',
            mysql_bind_address: '127.0.0.1',
            mysql_enabled_on_startup: 'yes',
            mysql_databases: [{
                name: 'servermail'
            }],
            mysql_users: [{
                name: "vagrant",
                password: "vagrant",
                host: "localhost",
                priv: "servermail.*:ALL",
            }]
        }
    end
    # We have to change the permission of config.py to world readable since
    # ownership can't be modified on a synced folder
    config.vm.provision "shell", inline: "chmod 664 /opt/postmaster/git/config.py"
    # Start the dev server
    config.vm.provision "shell", inline: "/opt/postmaster/env/bin/python /opt/postmaster/git/manage.py runserver --host 0.0.0.0 &", run: "always"
end

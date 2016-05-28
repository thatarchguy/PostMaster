# -*- mode: ruby -*-
# vi: set ft=ruby :

$script = <<SCRIPT
#!/bin/bash
if [ ! -f /usr/bin/ansible-playbook ]; then
    apt-get update
    apt-get install -y software-properties-common
    apt-add-repository ppa:ansible/ansible
    apt-get update
    apt-get install -y ansible
fi

ansible-playbook -i "localhost," -c local /opt/postmaster/git/ops/ansible/site.yml --extra-vars="remote_user=vagrant" --extra-vars="provision_type=dev"
SCRIPT

Vagrant.configure(2) do |config|
    config.vm.box = "puphpet/ubuntu1404-x64"
    config.vm.network "forwarded_port", guest: 8082, host: 8080
    config.vm.synced_folder "./", "/opt/postmaster/git"
    config.vm.provision "shell", inline: $script
end

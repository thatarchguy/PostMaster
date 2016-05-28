#!/bin/bash
ansible-playbook -i "localhost," -c local /opt/postmaster/git/ops/ansible/site.yml

#!/usr/bin/env python
import sys
import re
import subprocess
sys.path.append('src')
from quiltz.messaging.version import version

new_version = sys.argv[1]
old_version = version
if not re.match(r'\d+\.\d+\.\d+',new_version):
    print("invalid version: {}".format(new_version))

answer = input('are you sure to release from {} to {}: '.format(old_version, new_version))
if answer != 'yes':
    print('no confirmation')
    exit(0) 

with open('src/quiltz/messaging/version.py', "w+") as file:
    file.write('version="{}"'.format(new_version))

def run(*cmdline):
    print("running {}".format(cmdline))
    subprocess.call(cmdline)    

run("git", "pull")
run("git", "add", ".")
run("git", "commit", "-am", "release {}".format(new_version))
run("git", "tag", "{}".format(new_version))
run("git", "push")
run("git", "push", "--tags")

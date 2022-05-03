#!/usr/bin/env python3
import os
import argparse
import pathlib
import requests
import shutil
import secrets
import getpass
from subprocess import call
from sys import exit


ASN_URL = 'https://iptoasn.com/data/ip2asn-combined.tsv.gz'
CYBERCHEF_URL = 'https://github.com/gchq/CyberChef/releases/download/v9.32.3/CyberChef_v9.32.3.zip'
WORKING_DIR = os.environ.get('PWD')
FILESHARE_DIR = f'{WORKING_DIR}/data/gostatic/'
TOKEN_LENGTH = 16


def get_pass():
    count = 0
    while count < 3:
        print('Enter LDAP Admin password')
        pass1 =  getpass.getpass()
        print('Comfirm password')
        pass2 = getpass.getpass()
        if pass1 == pass2:
            return pass1
        if pass1 != pass2:
            print('Passwords do not match')
            count += 1


def get_cyberchef():
    try:
        os.mkdir('data/gostatic/cyberchef')
        os.chdir('data/gostatic/cyberchef')
        cyberchef = requests.get(CYBERCHEF_URL)
        with open('cyberchef.zip', 'wb') as f:
            f.write(cyberchef.content)
        shutil.unpack_archive('cyberchef.zip')
        pathlib.Path('cyberchef.zip').unlink()
    except requests.exceptions.ConnectionError:
        print('Could not download cyberchef Zip file')
        pass
    finally:
        os.chdir(WORKING_DIR)
        


def build_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d',
        '--domain',
        help='Base Domain (ex. example.com)',
        required=True
    )

    #### Change ME
    parser.add_argument(
        '-p',
        '--password',
        help=' OpenLDAP admin password [default: admin]',
        action='store_true',
        default=True,
        required=False
    )
    global args
    args = parser.parse_args()


def copy_files():
    command = 'sudo chmod -R 777 thehive'
    try:
        os.mkdir('configs')
        os.mkdir('configs/self-service-password')
        os.mkdir('configs/thehive')
        os.mkdir('configs/cortex')

    except FileExistsError:
        pass
    shutil.copy('templates/env.tmp', '.env')
    os.chmod('.env', 0o600)
    shutil.copy('templates/config.inc.php.tmp', 'configs/self-service-password/config.inc.php')
    shutil.copy('templates/docker-compose.yml.tmp', 'docker-compose.yml')
    shutil.copy('templates/application.thehive.conf.tmp', 'configs/thehive/application.conf')
    shutil.copy('templates/application.cortex.conf.tmp', 'configs/cortex/application.conf')

    
def set_pass():
    if not args.password:
        return 'admin'
    elif args.password:
        passwd = get_pass()
        return passwd


def update_file(fname, pattern, text):
    t =''
    with open(fname, 'r') as f:
        t = f.read()
        t = t.replace(pattern, text)
    with open(fname, 'w') as f:
        f.write(t)


def get_asn_tsv():
    file_name = ASN_URL.split("/")[-1]
    abs_path = pathlib.Path(f'{FILESHARE_DIR}{file_name}')

    # Try to make gostatic dir
    try:
        os.mkdir('data')
        os.mkdir(FILESHARE_DIR)
    except FileExistsError:
        pass


    if abs_path.exists():
        while True:
            resp = input('Replace current iptoasn TSV? [y/n]\n>> ')
            if resp.lower().strip() == 'y':
                os.remove(abs_path)
                file = requests.get(ASN_URL)
                with open(abs_path, 'wb') as f:
                    f.write(file.content)
                break
            else:
                print('skipping downloading new iptoasn TSV')
                break
    else:
        file = requests.get(ASN_URL)
        with open(abs_path, 'wb') as f:
            f.write(file.content)

def check_root():
    uid = os.getuid()
    if uid == 0:
        print('This script is not meant to be ran as root')
        exit(1)
    else:
        pass


if __name__ == '__main__':

    check_root()
    build_args()
    get_asn_tsv()
    get_cyberchef()
    copy_files()
    passw = set_pass()




    domain = args.domain
    # domain = 'longdong.local'
    ldap = ''
    ldap_l = domain.split('.')
    c = 1
    for x in ldap_l:
        ldap += f'dc={x}'
        if c < len(ldap_l):
            c += 1
            ldap += ','
    update_file('configs/thehive/application.conf', 'VVVV', secrets.token_urlsafe(TOKEN_LENGTH))
    update_file('configs/thehive/application.conf', 'YYYY', ldap)
    update_file('configs/thehive/application.conf', 'ZZZZ', passw)            
    update_file('.env', 'WWWW', secrets.token_urlsafe(TOKEN_LENGTH))
    update_file('.env', 'XXXX', domain)
    update_file('.env', 'YYYY', ldap)
    update_file('.env', 'ZZZZ', passw)
    update_file('configs/self-service-password/config.inc.php', 'YYYY', ldap)
    update_file('configs/self-service-password/config.inc.php', 'ZZZZ', passw)


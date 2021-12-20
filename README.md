# one stop docker shop

## Quickstart

You'll first need Docker and docker-compose. If you don't already have it here you can run this [script](https://raw.githubusercontent.com/deathnmind/satus-velox/main/scripts/install%20scripts/install_docker.sh) for ubuntu. Otherwise, follow the [install instructions](https://docs.docker.com/get-docker/) for your operating system.

 ```bash
chmod +x setup.py
./setup.py -d <base_domain>

docker-compose up -d
 ```

If you don't know what your base domain is ask Mike.

---

## Description

This is a docker compose config designed to build a basic util server providing the following services:

* OpenLDAP
* Reverse Proxy
* Self service password rest
* gostatic
* phpLDAPadmin
* IPchecker3000
* IPtoASN
* Dashmachine
* Rocketchat
* CyberChef

 All services are designed to sit behind the reverse proxy, except LDAP and LDAPS, and should be redirected to HTTPS.

---

## Default Credentials

 |  Service   |  Username   |   Password  |
| --- | --- | --- |
| dashmachine | admin | admin |
| nginxproxymanager | admin@example.com | changeme |
| thehive4 | admin@thehive.local | secret |

---

## Reverse Proxy mappings

| Scheme | Forward Hostname / IP | Forward Port |  
| --- | --- | --- |
| http | dashmachine | 5000 |
| http | iptoasn | 53661 |
| http | gostatic | 8043 |
| http | ipchecker3000 | 80  |
| http | phpldapadmin | 80  |
| http | nginxproxymanager | 81  |
| http | selfservicepassword | 80  |
| http | thehive4 | 9000 |
| http | rocketchat | 3000 |

---

## Rocketchat

- Rocketchat host header is set to `rc.{BASE_DOMAIN}`
- BASE_DOMAIN is provided during setup with setup.py.
- Rocketchat FQDN must match the host header, `rc.{BASE_DOMAIN}` by default, or it won't load.

---

## Simple PKI example with easy-rsa

```bash
sudo apt install easy-rsa -y
make-cadir example.com
cd example.com/
./easyrsa init-pki
./easyrsa build-ca
```

When promted for Common Name enter a name such as example-ca

```bash
Common Name (eg: your user, host, or server name) [Easy-RSA CA]:example-ca
```

Create certificate signed by CA for a server

```bash
./easyrsa build-server-full links.example.com nopass
```

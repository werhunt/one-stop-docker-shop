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
| Cortex |    |    |
| Elasticsearch| |     |
| Kibana |   |  |
| MISP    |  admin@admin.test | admin
| Shuffle | |    |

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






















### Mapping volumes
If you take a look of docker-compose.yml you will see you need some local folder that needs to be mapped, so before do docker-compose up, ensure at least folders with config files exist:
- ./cortex/application.conf:/etc/cortex/application.conf
- ./thehive/application.conf:/etc/thehive/application.conf

Structure would look like:
```
├── docker-compose.yml
├── README.md
├── thehive
│   └── application.conf
├── cortex
│   └── application.conf
└── vol
    ├── cassandra-data
    ├── data
    ├── elasticsearch_data
    ├── elasticsearch_logs
    ├── index
    ├── mysql
    ├── shuffle-apps
    ├── shuffle-database
    └── shuffle-files
```
If you run docker-compose with sudo, ensure you have created vol/elasticsearch_data and vol/elasticsearch_logs folders with non root user, otherwise elasticsearch container will not start.
In the same way permission must be granted to vol/index folder or thehive container will raise issues.

### ElasticSearch
ElasticSearch container likes big mmap count (https://www.elastic.co/guide/en/elasticsearch/reference/current/vm-max-map-count.html) so from shell you can change with
```sysctl -w vm.max_map_count=262144```
To set this value permanently, update the vm.max_map_count setting in /etc/sysctl.conf. To verify after rebooting, run sysctl vm.max_map_count

If you would run all containers on the same system - and maybe you have a limited amount of RAM - better to set some limit, for ElasticSearch, in docker-compose.yml I added those:

```- bootstrap.memory_lock=true```
```- "ES_JAVA_OPTS=-Xms256m -Xmx256m"```

Adjust depending on your needs and your env. Without these settings in my environment ElasticSearch was using 1.5GB


### Known Issues

If the `elasticsearch` container fails to start correctly, or constantly crashes, ensure that the folder ownership is set to the user that ran `docker-compose`.  

This can be corrected by running the following command:

```bash
chown -R 1000:1000 <path_to_elasticsearch>
```

Followed by restarting the `elasticsearch` node with:

```bash
docker-compose up -d elasticsearch
```

### Cassandra
Like for ElasticSearch maybe you would run all on same system and maybe you don't have a limited amount of RAM, better to set some size, here for Cassandra, in docker-compose.yml I added those:

```- MAX_HEAP_SIZE=1G```
```- HEAP_NEWSIZE=1G```

Adjust depending on your needs and your env. Without these settings in my environment Cassandra was using 4GB.


### Cortex-Analyzers
- In order to use Analyzers in docker version, it is set  the online json url instead absolute path of analyzers in the application.conf of Cortex:
  https://download.thehive-project.org/analyzers.json
- In order to use Analyzers in docker version it is set the application.conf thejob: ```
  job {
  runner = [docker]
}   ```
- The analyzer in docker version will need to download from internet images, so have to add in "/etc/default/docker"
  ``` DOCKER_OPTS="--dns 8.8.8.8 --dns 1.1.1.1" ```
- When Cortex launches an analyzer need to pass the object to being analyzed, so need share /tmp folder
- When Cortex launches an analyzer it uses docker.sock, have to map in compose
 ```  /var/run/docker.sock:/var/run/docker.sock  ```
- Have to change permission on /var/run/docker.sock in order to let use socket by cortex docker and cortex-analyzers docker
  ```sudo chmod 666 /var/run/docker.sock```
- First time an analyzer/responder is executed, it will take a while because docker image is being downloaded on the fly, from second run of analyzer/responder it runs normally

### Cortex
- login page on 9001 port, then click "update database" and create superadmin
- as superadmin create org and other user (remember to set password) and create apikey to use for connect with the hive 

### The Hive
- In order to let The Hive reads the external application.conf and configure Cortex had to pass in command of docker compose the following option:
  --no-config
- In order to let The Hive reads the external application.conf and configure MISP for receive alerts had to pass in command of docker compose the following option:
 ```  --no-config-secret ```
- Default credentials: admin@thehive.local // secret
- In order to connect The Hive with cortex take the cortex key generated in Cortex and set it in thehive/application.conf
- MISP connection is https, in order to skip the verify of self signed certificate have do add this setting in the hive application.conf under MISP section:
  ``` wsConfig { ssl { loose { acceptAnyCertificate: true } } } ```
 
### MISP
- login with default credentials: admin@admin.test // admin
- request change password
- go in Automation page and grab the api key to use in the hive application.conf to receive alerts from MISP or to use in MISP analyzers inside Cortex.

### SHUFFLE
To test automation I choose SHUFFLE (https://shuffler.io/)

In docker-compose.yml , after the comment "#READY FOR AUTOMATION ? " there is part dedicated to Shuffle (you can remove as the others if not needed)
Here will not document how to use it, there is already documentation (https://shuffler.io/docs/about).

Here just describe how to connect the things together.

- After SHUFFLE starts, go at login page (the frontend port by default is 3001), put credentials choosen in docker-compose.yml , for your convenience I set admin // password , create your first workflow, can be anything you have in mind, then go in Triggers, place Webhook node on dashboard, select it and grab the Webhook URI. it will be something like http://192.168.29.1:3001/api/v1/hooks/webhook_0982214b-3b92-4a85-b6fa-771982c2b449
- Go in applicaiton.conf of The Hive and modify the url under webhook notification part:
```
notification.webhook.endpoints = [
  {
    name: local
    url: "http://192.168.29.1:3001/api/v1/hooks/webhook_0982214b-3b92-4a85-b6fa-771982c2b449"
    version: 0
    wsConfig: {}
    includedTheHiveOrganisations: []
    excludedTheHiveOrganisations: []
  }
]
```
- In The Hive webhooks are not enabled by default, you should enable it, there is a guide to do it: https://github.com/TheHive-Project/TheHiveDocs/blob/master/TheHive4/Administration/Webhook.md
In my case I had to call this:
```
curl -XPUT -uuser@thehive.local:user@thehive.local -H 'Content-type: application/json' 127.0.0.1:9000/api/config/organisation/notification -d '
{
  "value": [
    {
      "delegate": false,
      "trigger": { "name": "AnyEvent"},
      "notifier": { "name": "webhook", "endpoint": "local" }
    }
  ]
}'
```
- Now are able to play automation with The Hive, Cortex-Analyzers, MISP thanks to SHUFFLE!


### Result
In conclusion, after execute ```sudo docker-compose up``` you will have the following services running:


| Service   |      Address      |  User |  Password |
|----------|:-------------:|:------:|------:|
| The Hive |  http://localhost:9000 | admin@thehive.local | secret
| Cortex |    http://localhost:9001  |    |
| Elasticsearch | http://localhost:9200 |     |
| Kibana |  http://localhost:5601 |  |
| MISP |    https://localhost:443   |  admin@admin.test | admin
| Shuffle | http://localhost:3001 |    |

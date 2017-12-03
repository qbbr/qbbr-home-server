# qbbr-home-server

JSON REST API Server for event data storage

```bash
. .env.dist
flask initdb
flask run
```

# usage

```bash
curl -i -XPUT -H 'Content-Type: application/json' -d '{"value":55}' 127.0.0.1:5000/cpu_temp.json
curl -i -XGET -H 'Content-Type: application/json' 127.0.0.1:5000/cpu_temp.json
curl -i -XGET -H 'Content-Type: application/json' 127.0.0.1:5000
```

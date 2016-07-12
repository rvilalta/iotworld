curl -X GET -H "Content-Type: application/json" http://127.0.0.1:8080/restconf/config/HVAC/Temperature/

curl -X PUT -H "Content-Type: application/json" http://27.0.0.1:8080/restconf/config/HVAC/Heat/ -d'{"Heat":{"Status":"Run"}}'

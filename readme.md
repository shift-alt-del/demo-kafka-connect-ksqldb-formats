
what's this
------------
A quick demo for us to check with the differences between connect converters.

Documents:
- https://docs.confluent.io/platform/6.2.0/connect/userguide.html
- https://docs.confluent.io/platform/6.2.0/connect/concepts.html#converters

Converters:
- AvroConverter `io.confluent.connect.avro.AvroConverter`: use with Schema Registry
- ProtobufConverter `io.confluent.connect.protobuf.ProtobufConverter`: use with Schema Registry
- JsonSchemaConverter `io.confluent.connect.json.JsonSchemaConverter`: use with Schema Registry
- JsonConverter `org.apache.kafka.connect.json.JsonConverter` (without Schema Registry): use with structured data
- StringConverter `org.apache.kafka.connect.storage.StringConverter`: simple string format
- ByteArrayConverter `org.apache.kafka.connect.converters.ByteArrayConverter`: provides a “pass-through” option that does no conversion


## connector
Documents:
- https://docs.confluent.io/kafka-connect-jdbc/current/source-connector/index.html
- Notice: msyql driver (`mysql-connector-java-x.x.xx.jar`) is not included, please donwload it by yourself. 

```
mkdir confluent-hub-components

# safe to ignore CP license errors
confluent-hub install --component-dir confluent-hub-components --no-prompt confluentinc/kafka-connect-jdbc:10.4.1
```

## mysql db to play with
```
mkdir -p mysql

cat << EOF > mysql/custom-config.cnf
[mysqld]
server-id                = 223344 
log_bin                  = mysql-bin 
binlog_format            = ROW 
binlog_row_image         = FULL 
expire_logs_days         = 10
gtid_mode                = ON
enforce_gtid_consistency = ON
EOF
```

## docker-compose.yaml

- leave `KSQL_CONNECT_VALUE_CONVERTER` as json.
- leave `KSQL_CONNECT_KEY_CONVERTER` as string. (going to overrite when submitting connect.)

## init mysql and demo data
```
# start containers
docker-compose up -d

# initialize mysql users
docker exec -i mysql mysql -uroot -pmysql-pw < ./mysql/init.sql

# create tables
docker exec -i mysql mysql -uroot -pmysql-pw demo < ./mysql/create_table.sql

# import dummy data
docker exec -i mysql mysql -uroot -pmysql-pw demo < ./mysql/add_data.sql

# check tables creation
docker exec -it mysql mysql -uroot -pmysql-pw demo -e "show tables;"
docker exec -it mysql mysql -uroot -pmysql-pw demo -e "select * from event_str limit 1;"
docker exec -it mysql mysql -uroot -pmysql-pw demo -e "select * from event_int limit 1;"
```

## init connect
```
docker exec -it ksqldb-cli ksql http://ksqldb-server:8088

SET 'auto.offset.reset' = 'earliest';

# submit connectors
RUN SCRIPT '/tmp/scripts/auto_generated_create.txt';

# check connectors
SHOW CONNECTORS;

# check topics
SHOW TOPICS;
```

## check key format.
```
cd tools
python3 consumer.py multiple_string_event_int
```

it will prints out key bytes, value bytes, schema_id, schema_api_url, schema. 
```
topic=single_jsonschema_event_str
key=b'\x00\x00\x00\x00\x06"BBB"'
value=b'\x00\x00\x00\x00\x03\x02\x06BBB\x02\x08help\x02\xc0\x03'
schema_id=6
schema_api_url=http://localhost:8081/schemas/ids/6
schema={'schemaType': 'JSON', 'schema': '{"oneOf":[{"type":"null"},{"type":"string"}]}'}
``` 

## fin
```
docker-compose down -v
```


## appendix:
Data dir error on container startup, could be fixed by run script as below.
```
docker volume prune
```

Generate ksql connector creation scripts.
```
cd tools
python3 create_connect_ksqls.py
```


## references:
Confluent tutorials & connect guaides
- https://docs.ksqldb.io/en/latest/tutorials/materialized/
- https://docs.confluent.io/platform/6.2.0/connect/userguide.html
- https://docs.confluent.io/platform/6.2.0/connect/concepts.html#converters

SMT
- https://docs.confluent.io/kafka-connect-jdbc/current/source-connector/index.html#message-keys
- https://docs.confluent.io/platform/current/connect/transforms/valuetokey.html#valuetokey
- https://docs.confluent.io/platform/current/connect/transforms/extractfield.html
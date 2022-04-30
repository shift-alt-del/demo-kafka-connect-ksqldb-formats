
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
docker exec -it mysql mysql -uroot -pmysql-pw demo -e "select * from table_key_str limit 1;"
docker exec -it mysql mysql -uroot -pmysql-pw demo -e "select * from table_key_int limit 1;"
```

## init connect
```
docker exec -it ksqldb-cli ksql http://ksqldb-server:8088

SET 'auto.offset.reset' = 'earliest';

# MST, message key: 
# https://docs.confluent.io/kafka-connect-jdbc/current/source-connector/index.html#message-keys
# SMT - ValueToKey:
# https://docs.confluent.io/platform/current/connect/transforms/valuetokey.html#valuetokey
# SMT - ExtractField$Key:
# https://docs.confluent.io/platform/current/connect/transforms/extractfield.html
CREATE SOURCE CONNECTOR demo_source_connector WITH (
    'connector.class'='io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url'='jdbc:mysql://mysql:3306/demo',
    'connection.user'='example-user',
    'connection.password'='example-pw',
    'topic.prefix'='mysql-',

    'key.converter.schema.registry.url' = 'http://schema-registry:8081',
    'key.converter' = 'org.apache.kafka.connect.storage.StringConverter',

    'poll.interval.ms'=3600000,
    'table.whitelist'='demo.table_key_str,demo.table_key_int',
    'mode'='bulk',
    'transforms'='createKey,extractFieldAskey',
    'transforms.createKey.type'='org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.createKey.fields'='user_id',
    'transforms.extractFieldAskey.type'='org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractFieldAskey.field'='user_id'
);
```

## Appendix:
Data dir error on container startup, could be fixed by run script as below.
```
docker volume prune
```


## References:
- https://docs.ksqldb.io/en/latest/tutorials/materialized/
- https://docs.confluent.io/platform/6.2.0/connect/userguide.html
- https://docs.confluent.io/platform/6.2.0/connect/concepts.html#converters

# What's this repo about

A quick demo to show the differences between connect converters.

- How connector writes the data?
- How ksqlDB load the data?

**Connect converters:**

https://docs.confluent.io/platform/6.2.0/connect/userguide.html
- AvroConverter `io.confluent.connect.avro.AvroConverter`: use with Schema Registry
- ProtobufConverter `io.confluent.connect.protobuf.ProtobufConverter`: use with Schema Registry
- JsonSchemaConverter `io.confluent.connect.json.JsonSchemaConverter`: use with Schema Registry
- JsonConverter `org.apache.kafka.connect.json.JsonConverter` (without Schema Registry): use with structured data
- StringConverter `org.apache.kafka.connect.storage.StringConverter`: simple string format
- ByteArrayConverter `org.apache.kafka.connect.converters.ByteArrayConverter`: provides a “pass-through” option that does no conversion

**ksqlDB formats:**

https://docs.ksqldb.io/en/latest/reference/serialization/
- AVRO
- PROTOBUF
- JSON_SR
- JSON
- KAFKA
- NONE?

## Preparation

JDBC source connector & mysql:
- https://docs.confluent.io/kafka-connect-jdbc/current/source-connector/index.html
- Notice: mysql driver (`mysql-connector-java-x.x.xx.jar`) is not included, please donwload it by yourself. 

Download JDBC source connector
```
mkdir confluent-hub-components

# safe to ignore CP license errors
confluent-hub install --component-dir confluent-hub-components --no-prompt confluentinc/kafka-connect-jdbc:10.4.1
```

Setup mysql server configuration
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

## Inside docker-compose.yaml

- leave `KSQL_CONNECT_VALUE_CONVERTER` as json.
- leave `KSQL_CONNECT_KEY_CONVERTER` as string. (going to overwrite this setting when submitting connect.)

```
# start containers
docker-compose up -d
```

## Init mysql and demo data

```
# initialize mysql users
docker exec -i mysql mysql -uroot -pmysql-pw < ./mysql/init.sql

# create tables
docker exec -i mysql mysql -uroot -pmysql-pw demo < ./mysql/create_table.sql

# import dummy data
docker exec -i mysql mysql -uroot -pmysql-pw demo < ./mysql/add_data.sql

# check tables creation
docker exec -it mysql mysql -uroot -pmysql-pw demo -e "show tables;"
```

## Init connect

```
docker exec -it ksqldb-cli ksql http://ksqldb-server:8088

SET 'auto.offset.reset' = 'earliest';

# submit connectors
RUN SCRIPT '/tmp/scripts/create_connect.txt';

# create streams
RUN SCRIPT '/tmp/scripts/create_stream.txt';
```

## Create dim tables

```
# submit connectors for dim 
RUN SCRIPT '/tmp/scripts/create_dim_connect.txt';

# create tables
RUN SCRIPT '/tmp/scripts/create_dim_table.txt';
```

## Query

```
# join single column
create stream t_join_single_avro as
    select * from S_SINGLE_AVRO_STR s left join T_DIM_USER_AVRO t on s.user_id = t.rowkey emit changes;

create stream t_join_single_str as
    select * from S_SINGLE_AVRO_STR s left join T_DIM_USER_STRING t on s.user_id = t.rowkey emit changes;

# join multiple column
create stream t_join_multiple_avro as
    select * from S_SINGLE_AVRO_STR s left join T_DIM_USER_REASON_AVRO t on STRUCT(user_id:=s.user_id, reason_id:=s.reason) = t.rowkey emit changes;
```

## Fin

```
docker-compose down -v
```


## Toolbox:

How to generate ksql connector creation scripts.
```
cd tools
python3 create_connect_ksqls.py
```

How to check message key format.
```
cd tools
python3 consumer.py multiple_string_event_int

# console output
# it will prints out key bytes, value bytes, schema_id, schema_api_url, schema.

topic=single_jsonschema_event_str
key=b'\x00\x00\x00\x00\x06"BBB"'
value=b'\x00\x00\x00\x00\x03\x02\x06BBB\x02\x08help\x02\xc0\x03'
schema_id=6
schema_api_url=http://localhost:8081/schemas/ids/6
schema={'schemaType': 'JSON', 'schema': '{"oneOf":[{"type":"null"},{"type":"string"}]}'}
```

## References:
Confluent tutorials & connect guides
- https://docs.ksqldb.io/en/latest/tutorials/materialized/
- https://docs.confluent.io/platform/6.2.0/connect/userguide.html
- https://docs.confluent.io/platform/6.2.0/connect/concepts.html#converters
- https://www.confluent.io/blog/ksqldb-0-15-reads-more-message-keys-supports-more-data-types/#upgrading-and-compatibility

SMT
- https://docs.confluent.io/kafka-connect-jdbc/current/source-connector/index.html#message-keys
- https://docs.confluent.io/platform/current/connect/transforms/valuetokey.html#valuetokey
- https://docs.confluent.io/platform/current/connect/transforms/extractfield.html
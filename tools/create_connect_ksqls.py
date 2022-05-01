
import os

"""
Try different converter class for key.

- AvroConverter `io.confluent.connect.avro.AvroConverter`: use with Schema Registry
- ProtobufConverter `io.confluent.connect.protobuf.ProtobufConverter`: use with Schema Registry
- JsonSchemaConverter `io.confluent.connect.json.JsonSchemaConverter`: use with Schema Registry
- JsonConverter `org.apache.kafka.connect.json.JsonConverter` (without Schema Registry): use with structured data
- StringConverter `org.apache.kafka.connect.storage.StringConverter`: simple string format
- ByteArrayConverter `org.apache.kafka.connect.converters.ByteArrayConverter`: provides a “pass-through” option that does no conversion
"""

CONVERTER_MAPPING = {
    'AvroConverter': 'io.confluent.connect.avro.AvroConverter',
    'ProtobufConverter': 'io.confluent.connect.protobuf.ProtobufConverter',
    'JsonSchemaConverter': 'io.confluent.connect.json.JsonSchemaConverter',
    'JsonConverter': 'org.apache.kafka.connect.json.JsonConverter',
    'StringConverter': 'org.apache.kafka.connect.storage.StringConverter',
    
    # ByteArrayConverter does not work with this use case.
    # 'ByteArrayConverter': 'org.apache.kafka.connect.converters.ByteArrayConverter',
}

# (xxx)Converter -> KSQL format types
KSQL_FORMAT_MAPPING = {
    'avro': 'AVRO',
    'jsonschema': 'JSON_SR',
    'json': 'JSON',
    'string': 'KAFKA',
    'protobuf': 'PROTOBUF',
}

ksql_mst_single_column = """
    'transforms'='createKey,extractFieldAskey',
    'transforms.createKey.type'='org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.createKey.fields'='user_id',
    'transforms.extractFieldAskey.type'='org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractFieldAskey.field'='user_id'"""

ksql_mst_multiple_column = """
    'transforms'='createKey',
    'transforms.createKey.type'='org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.createKey.fields'='user_id,reason'"""

if __name__ == '__main__':

    base_dirs = '/'.join(os.getcwd().split('/')[:-1] + ['ksql'])
    
    target_create_fp = os.path.join(base_dirs, 'create_connect.txt')
    target_drop_fp = os.path.join(base_dirs, 'drop_connect.txt')
    target_create_stream_fp = os.path.join(base_dirs, 'create_stream.txt')
    target_drop_stream_fp = os.path.join(base_dirs, 'drop_stream.txt')

    with open(target_create_fp, 'w') as fc, \
            open(target_drop_fp, 'w') as fd, \
            open(target_create_stream_fp, 'w') as fcs, \
            open(target_drop_stream_fp, 'w') as fds:
        for is_single_column in [True, False]:
            for converter_name, converter_path in CONVERTER_MAPPING.items():
                # make names shorter and to lower()
                short_converter_name = converter_name.replace('Converter', '').lower()

                for table_name in ['demo.event_str','demo.event_int']:
                    # str or int, to lower()
                    short_table_name = table_name.split('.')[-1].split('_')[-1].lower()

                    column_type = 'single' if is_single_column else 'multiple'
                    connector_id = f'connect_{column_type}_{short_converter_name}_{short_table_name}'
                    topic_prefix = column_type + '_' + short_converter_name
                    
                    stream_id = f's_{column_type}_{short_converter_name}_{short_table_name}'
                    dest_topic_name = f'{topic_prefix}_{table_name.split(".")[-1]}'
                    ksql = f"""
CREATE SOURCE CONNECTOR {connector_id} WITH (
    'connector.class'='io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url'='jdbc:mysql://mysql:3306/demo',
    'connection.user'='example-user',
    'connection.password'='example-pw',
    'topic.prefix'='{topic_prefix}_',

    'key.converter.schema.registry.url' = 'http://schema-registry:8081',
    'key.converter' = '{converter_path}',

    'poll.interval.ms'=5000,
    'table.whitelist'='{table_name}',
    'mode'='incrementing',
    'incrementing.column.name'='id',
"""

                    if is_single_column:
                        ksql += ksql_mst_single_column
                    else:
                        ksql += ksql_mst_multiple_column

                    fc.write(ksql)
                    fc.write('\n);\n')

                    fd.write(f"""DROP CONNECTOR {connector_id};\n""")


                    # create stream s_str with (kafka_topic='single_string_event_str', key_format='KAFKA', value_format='AVRO');
                    if short_converter_name != 'protobuf':
                        """
                        todo: protobuf error? let's skip protobuf.

                        Unable to verify if the key schema for topic: single_protobuf_event_str is compatible with ksqlDB.
                        Reason: Key schemas are always unwrapped.
                        Please see https://github.com/confluentinc/ksql/issues/ to see if this particular reason is already known.
                        If not, please log a new issue, including this full error message.
                        """
                        fcs.write(f"""CREATE STREAM {stream_id} WITH (kafka_topic='{dest_topic_name}', key_format='{KSQL_FORMAT_MAPPING[short_converter_name]}', value_format='AVRO');\n""")
                        fds.write(f"""DROP STREAM {stream_id};\n""")
                    else:
                        pass
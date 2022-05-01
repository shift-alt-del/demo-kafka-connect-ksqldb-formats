
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

    target_create_fp = '/'.join(os.getcwd().split('/')[:-1] + ['connect', 'auto_generated_create.txt'])
    target_drop_fp = '/'.join(os.getcwd().split('/')[:-1] + ['connect', 'auto_generated_drop.txt'])

    with open(target_create_fp, 'w') as fc, open(target_drop_fp, 'w') as fd:
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

                    fd.write(f'DROP CONNECTOR {connector_id};\n')
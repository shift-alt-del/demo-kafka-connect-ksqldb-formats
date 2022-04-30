import sys
from io import BytesIO
from struct import unpack
import requests
from confluent_kafka import DeserializingConsumer, Consumer

# schema_id: schema_str
# to avoid calling schema-registry too much.
schema_cache = {}

# consumer configurations
# for full list of configurations, see:
# https://docs.confluent.io/platform/current/clients/confluent-kafka-python/#serializingproducer
conf = {
    'bootstrap.servers': 'localhost:29092',
    'auto.offset.reset': 'earliest',
    'group.id': 'groupidfortest',
}

# initialize consumer instance
consumer = Consumer(conf)
consumer.subscribe([sys.argv[1]])

while True:
    try:
        msg = consumer.poll(1.0)
        if msg is None:
            print(".")
            continue
        elif msg.error():
            print('error: {}'.format(msg.error()))
        else:
            key_bytes = msg.key()
            value_bytes = msg.value()

            print('---')
            print(f'topic={msg.topic()}')
            print(f'key={key_bytes}')
            print(f'value={value_bytes}')

            # there are schemas inside
            if len(key_bytes) >= 5 and key_bytes[0] == 0:
                buffer = BytesIO(key_bytes)
                magic, schema_id = unpack('>bI', buffer.read(5))

                # query schema-registry to get the schema by given schema_id
                sr_schema_url = f'http://localhost:8081/schemas/ids/{schema_id}'

                # if not exist in cache, reload schema to cache.
                if schema_id not in schema_cache:
                    schema_cache[schema_id] = requests.get(sr_schema_url).json()
                schema_str = schema_cache[schema_id]
                print(f'schema_id={schema_id}')
                print(f'schema_api_url={sr_schema_url}')
                print(f'schema={schema_str}')
            else:
                print('schema=None')
                

    except KeyboardInterrupt:
        break
import argparse
import json
from pathlib import Path
from typing import Optional

try:
    from kafka import KafkaConsumer
except Exception:
    KafkaConsumer = None

try:
    from pymongo import MongoClient
except Exception:
    MongoClient = None


def build_consumer(topic: str, bootstrap_servers: str):
    if KafkaConsumer is None:
        return None

    return KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        auto_offset_reset="latest",
        enable_auto_commit=True,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )


def build_mongo(uri: str, database: str, collection: str):
    if MongoClient is None:
        return None

    client = MongoClient(uri, serverSelectionTimeoutMS=2000)
    try:
        client.admin.command("ping")
    except Exception:
        return None
    return client[database][collection]


def persist_payload(payload: dict, output_file: Path, mongo_collection=None) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")

    if mongo_collection is not None:
        mongo_collection.insert_one(payload)


def consume_from_local(input_file: Path, output_file: Path, mongo_collection=None, max_messages: Optional[int] = None) -> int:
    if not input_file.exists():
        print(f"Local input file not found: {input_file}")
        return 0

    count = 0
    with input_file.open("r", encoding="utf-8") as f:
        for line in f:
            payload = json.loads(line.strip())
            persist_payload(payload, output_file, mongo_collection)
            count += 1
            if max_messages and count >= max_messages:
                break
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Consume stock ticks from Kafka/local and persist")
    parser.add_argument("--topic", default="stock_ticks")
    parser.add_argument("--bootstrap-servers", default="localhost:9092")
    parser.add_argument("--mongo-uri", default="mongodb://localhost:27017")
    parser.add_argument("--mongo-db", default="stock_intelligence")
    parser.add_argument("--mongo-collection", default="ticks")
    parser.add_argument("--local-input", default="data/raw/stream_ticks.jsonl")
    parser.add_argument("--local-output", default="data/raw/consumed_ticks.jsonl")
    parser.add_argument("--max-messages", type=int, default=200)
    args = parser.parse_args()

    output_file = Path(args.local_output)
    input_file = Path(args.local_input)
    mongo_collection = build_mongo(args.mongo_uri, args.mongo_db, args.mongo_collection)

    consumer = None
    try:
        consumer = build_consumer(args.topic, args.bootstrap_servers)
    except Exception as ex:
        print(f"Kafka unavailable, falling back to local input: {ex}")

    if consumer is None:
        count = consume_from_local(input_file, output_file, mongo_collection, args.max_messages)
        print(f"Consumed {count} messages from local file")
        return

    count = 0
    for message in consumer:
        persist_payload(message.value, output_file, mongo_collection)
        count += 1
        if count >= args.max_messages:
            break

    print(f"Consumed {count} messages from Kafka")


if __name__ == "__main__":
    main()

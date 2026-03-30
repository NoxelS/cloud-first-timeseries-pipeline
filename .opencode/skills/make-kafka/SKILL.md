---
name: make-kafka
description: Manage local Kafka topics, consumer groups, and view lags via Makefile
compatibility: opencode
---

## What I do
Provides wrapper commands to interact with the local dockerized Kafka broker.

## When to use me
Use this when you need to inspect messages, debug consumer lag, create topics, or manage consumer groups.

## Available Commands
- `make bootstrap` - Runs the python bootstrap script for Kafka topics.
- `make kafka-topics` - Lists all Kafka topics.
- `make kafka-topic-describe TOPIC=<name>` - Describes a specific topic.
- `make kafka-topic-create TOPIC=<name>` - Creates a topic with 3 partitions and replication factor 1.
- `make kafka-consumer-groups` - Lists all consumer groups.
- `make kafka-consumer-lag` - Describes all groups to view consumer lag.
- `make kafka-consumer-group-describe GROUP=<name>` - Describes a specific consumer group.
- `make kafka-consumer-group-delete GROUP=<name>` - Deletes a specific consumer group.
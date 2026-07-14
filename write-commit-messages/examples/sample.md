## example 1
feat(masros-gui): display flow description instead of flow code

flowCodes are immutable UUIDs, making them hard to identify at a
glance. Replaced affected views to show the human-readable flow
description so operators can identify flows without decoding a UUID.

## example 2 — subject line too long (corrected)

❌ refactor(ros-common): extract shared step-log publishing into a dedicated KafkaStepLogPublisher facade
✅ refactor(ros-common): extract step-log into KafkaStepLogPublisher

The four former callsites opened their own KafkaTemplate handles.
Consolidating into a single facade removes the duplication and
makes it easier to add cross-cutting concerns (retries, tracing).

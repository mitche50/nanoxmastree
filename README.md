# Nano Xmas Tree

A messaging system that enables users to control animations on a christmas tree via sending Nano to a provided address.

Requirements: Redis server, RabbitMQ, Python 3.x

- Server monitors blockchain for 'send' to monitoring address.
- On send, creates message with the amount (in raw) and sending address and publishes to Redis
- On message, client creates a delay task and pushes to RabbitMQ queue
- Celery worker processes tasks in FIFO manner to animate on tree
# Nano Xmas Tree

A messaging system that enables users to control animations on a christmas tree via sending Nano to a provided address.

Requirements: Redis server, Python 3.x

- Server monitors blockchain for 'send' to monitoring address.
- On send, creates message with the amount (in raw) and sending address and publishes to Redis
- On message, client pushes the address and amount to the 'XmasQueue' redis list - animation selected by amount of raw provided.
- Worker monitors the 'XmasQueue' for tasks and processes synchronously.  Each task the worker will send a post with the current address and a list of the next 10 pending requests to the webserver and then process the animation.
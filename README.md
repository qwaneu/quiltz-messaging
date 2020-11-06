# quiltz-messaging

python (email) messaging package 

## Purpose

At QWAN we're building some applications in python. We collect usefull stuff in
quiltz packages:

* **quiltz-domain** contains domain level modules like, entity id's, results, an
  email anonymizer, validators and parsers
* **quiltz-testsupport** contains test support modules, that supports mainly non
  unit tests, like integrating with smtp,  probing asynchronous results and
  asserting log statements
* **quiltz-messaging** (this module) contains a messaging domain concept and an
  engine(s) to send the messages. Currently only smtp sending is supported.

## installing 

```bash
pip install quitlz-messaging
```

see [documentatio](doc/index.md)

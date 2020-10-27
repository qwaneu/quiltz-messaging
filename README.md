# quiltz-messaging

python (email) messaging package 

## Purpose

At QWAN we're building some applications in python. We collect usefull stuff in quiltz packages:

* **quiltz_domain**
  contains domain level modules like, entity id's, results, an email anonymizer, validators and parsers
* **quiltz_testsupport**
  contains test support modules, that supports mainly non unit tests, like integrating with smtp,  probing asynchronous results and asserting log statements
* **quilts_messaging**
  contains a messaging domain concept and an engine(s) to send the messages. Currently only smtp sending is supported.

## modules in this package

The 2 modules in this package work together, but _can_ be used separately as well. 

<div hidden>
```
@startuml messaging-component
class engine.smtp.SMTPBasedMessageEngine
class engine.smtp.NoMessageEngine
class engine.smtp.SMTPBasedMessageEngineForTest
class messenger.Messenger
class messenger.Message
engine.smtp.SMTPBasedMessageEngine -down[hidden]-> engine.smtp.SMTPBasedMessageEngineForTest
engine.smtp.SMTPBasedMessageEngineForTest -right[hidden]-> engine.smtp.NoMessageEngine
engine.smtp.SMTPBasedMessageEngine -right-> messenger.Messenger
messenger.Messenger o-right-> messenger.Message	
@enduml
```
</div>

![messaging-component](doc/images/messaging-component.png)

* **Messenger** is a domain level concept that collects messages
* **SMTPBasedMessageEngine** is an smtp adapter that sends the messages in messenger on `commit`
* **SMTPBasedMessageEngineFor** is an smtp adapter useful for test that ommits tls connections and works fine with the SMTPServer from [quiltz-testsupport](https://github.com/qwaneu/quiltz-testsupport)


### messenger

In your domain code, send messages like this:

```
from quiltz.messaging import 
...
```
## installing 

```bash
pip install quitlz-messaging
```


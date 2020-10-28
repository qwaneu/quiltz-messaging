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
* **quiltz-messaging** contains a messaging domain concept and an engine(s) to
  send the messages. Currently only smtp sending is supported.

## installing 

```bash
pip install quitlz-messaging
```

## modules in this package

The 2 modules in this package work together, but _can_ be used separately as well. 

See [design considerations](doc/design-considerations.md)

<!--
@startuml messaging-component
skinparam {
  handwritten true
  monochrome true
}
package quiltz {
  package messenger {
    class Messenger {
      messages
      send(message)
    }
    class Message {
      static for_unnamed_recepient()
      static for_named_recepient()
    }
  }
  package engine.smtp {        
    class SMTPBasedMessageEngine {
      commit(messenger)
    }
    class NoMessageEngine {
      commit(messenger)
    }
    class SMTPBasedMessageEngineForTest {
      commit(messenger)
    }
  }
}
SMTPBasedMessageEngine -down[hidden]-> SMTPBasedMessageEngineForTest
SMTPBasedMessageEngineForTest -right[hidden]-> NoMessageEngine
SMTPBasedMessageEngine .right.> Messenger
Messenger o-right-> Message
@enduml

-->

![messaging-component](doc/images/messaging-component.png)

* **Messenger** is a domain level concept that collects messages
* **SMTPBasedMessageEngine** is an smtp adapter that sends the messages in messenger on `commit`
* **SMTPBasedMessageEngineFor** is an smtp adapter useful for test that ommits tls connections and works fine with the SMTPServer from [quiltz-testsupport](https://github.com/qwaneu/quiltz-testsupport)

### messenger

In your domain code, send messages like this:

```python
from quiltz.messaging import Message, Messenger

def send_a_message_from_somewhere():
    messenger = Messenger('sender@mail.org', None)
    message = Message.for_unnamed_recipient(
        to='recepient@email.org', 
        subject="Hi Facilitator", 
        body='My message')
    messenger.send(message)
```

### SMTPBasedMessageEngine

Then, anywhere else in the code you can commit all created messages

```python
from quiltz.engine.smtp import SMTPBasedMessageEngine

def commit_sending_messages():
    engine = SMTPBasedMessageEngine(
        host='somehost', 
        port=9992, 
        user='someuser', 
        password='s3cr3t')
    engine.commit(messenger) # really sends all messages 
```



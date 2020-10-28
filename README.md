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

## Design considerations

### Hexagons
We use hexagonal architecture for our applications to separate business logic
from integrations with the outside world. Typically our applications use command
and query separation (at least conceptually), and we tend to model commands (and queries) explicitly as classes.

A command coordinates command execution. It typically uses repositories to fetch domain object, delegate some behaviour to it, saves the result in a repository and responds to its caller. You may think of this as: We separate the domain logic from integrating with the outside world and the command coordinates the split.

<!--
@startuml command-execution
skinparam {
  handwritten true
  monochrome true
}
hide footbox
box "domain"
participant command order 10
participant domainobject order 20
end box
box "adaper"
participant repository order 30
end box
command -> repository: byId(12123)
note right
get domain object dat from some storage
and map it to a domain object
end note
create domainobject
repository -> domainobject: create
command -> domainobject: do the business
command -> repository: save(domainobject)
@enduml
-->
![messaging-component](doc/images/command-execution.png)


## Sending messages
If the business logic (as modelled in the domain object) needs to notify someone or something of something (i.e. send a message) we want to model that in an how-to-send-a-message-agnostic manner. 
The domain object should then be able to say to a messenger concept: 'send some message'
<!--
@startuml domain-messenger-interaction
skinparam {
  handwritten true
  monochrome true
}
hide footbox
actor actor
box "domain"
actor -> domainobject: do your business
domainobject -> messenger: send some message
end box
@enduml
-->
![messaging-component](doc/images/domain-messenger-interaction.png)

Also we'd like all integrations with the outside world to be in a controlled place; an adapter. Therefore we decided to separate the creating and collecting the messages from actually sending it, coordinated by the command.

<!--
@startuml command-execution-with-message
skinparam {
  handwritten true
  monochrome true
}
hide footbox
box "adapters"
participant messageengine order 30
end box
box "domain"
participant command order 10
participant domainobject order 20
participant messenger order 20
end box
actor smtpserver order 40
command -> domainobject: do the business
domainobject -> messenger: send some message
messenger -> messenger: create some message  
command -> messageengine: commit(messenger)
messageengine -> messenger: get messages
note right
map all messages to email messages
send to smtp server
end note
messageengine -> smtpserver: send message
@enduml
-->
![messaging-component](doc/images/command-execution-with-message.png)

a complete interaction with a some repository and mesaging could look like:

<!--
@startuml command-execution-with-repo-and-message
skinparam {
  handwritten true
  monochrome true
}
hide footbox
box "adapters"
participant repository order 30
participant messageengine order 30
end box
box "domain"
participant command order 10
participant domainobject order 20
participant messenger order 20
end box
command -> repository: byId(12123)
create domainobject
repository -> domainobject: create
command -> domainobject: do the business
domainobject -> messenger: send some message
messenger -> messenger: create some message  
command -> repository: save(domainobject)
command -> messageengine: commit(messenger)
@enduml
-->
![messaging-component](doc/images/command-execution-with-repo-and-message.png)


## modules in this package

The 2 modules in this package work together, but _can_ be used separately as well. 

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



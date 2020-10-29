from testing import *
from quiltz.testsupport.smtp import StubSmtpServer
import logging 
from dataclasses import dataclass
from quiltz.testsupport import probe_that, log_collector
from quiltz.messaging.engine.smtp import SMTPBasedMessageEngine, as_smtp_message
from quiltz.messaging.messenger import Message, Messenger
from quiltz.domain.results import Success, Failure
from quiltz.domain.anonymizer import anonymize

class TestSMTPBasedMessageEngine:
    @pytest.fixture(autouse=True)
    def setup(self):
        logging.getLogger('mail.log').setLevel(logging.WARN)
        self.SMTP_HOST = 'localhost'
        self.SMTP_PORT = '9925'
        self.FOR_TEST  = True
        self.server = StubSmtpServer(hostname='localhost', port=9925)
        self.message_engine = SMTPBasedMessageEngine.from_config(self)
        self.messenger = Messenger(sender='no-reply@messenger.bla', context=None)
        self.server.start()
        yield
        self.server.stop()

    def test_sends_message_to_recipient(self):        
        self.messenger.send(aValidMessage(to=ValidRecepient(), subject="Hi Facilitator", body='My message'))
        self.message_engine.commit(self.messenger)

        probe_that(lambda: assert_that(self.server.messages, equal_to([
            stringified_message(self.messenger.messages[0])
        ])))

    def test_returns_success(self):        
        self.messenger.send(aValidMessage(to=ValidRecepient(), subject="Hi Facilitator", body='My message'))
        assert_that(self.message_engine.commit(self.messenger), equal_to(Success()))

    def test_sends_multiple_message_to_recipient(self):        
        self.messenger.send(aValidMessage(to=ValidRecepient(email="rob@mail.com"), subject="Hi Facilitator", body='My message'))
        self.messenger.send(aValidMessage(to=ValidRecepient(email="marc@mail.com"), subject="Hi Facilitator", body='My message'))
        self.message_engine.commit(self.messenger)

        probe_that(lambda: assert_that(self.server.messages, equal_to([
            stringified_message(message) for message in self.messenger.messages 
        ])))

    def test_logs_sending(self, log_collector):
        self.messenger.send(aValidMessage(to=ValidRecepient(email="rob@mail.com"), subject="Hi Facilitator", body='My message'))
        self.messenger.send(aValidMessage(to=ValidRecepient(email="marc@mail.com"), subject="Hi Facilitator", body='My message'))
        self.message_engine.commit(self.messenger)
        log_collector.assert_info('Flushed messages to {}, {}'.format(anonymize("rob@mail.com"), anonymize("marc@mail.com")))

class TestSMTPBasedMessageEngineThatFails:
    @pytest.fixture(autouse=True)
    def setup(self):
        logging.getLogger('mail.log').setLevel(logging.WARN)
        self.SMTP_HOST = 'localhost'
        self.SMTP_PORT = '9925'
        self.FOR_TEST  = True
        self.message_engine = SMTPBasedMessageEngine.from_config(self)
        self.messenger = Messenger(sender='no-reply@messenger.bla', context=None)

    def test_returns_success(self):        
        self.messenger.send(aValidMessage(to=ValidRecepient(), subject="Hi Facilitator", body='My message'))
        assert_that(self.message_engine.commit(self.messenger), equal_to(Failure(message='[Errno 111] Connection refused')))

class TestSmtpMessageMapping:
    def test_message_contains_to_from_body(self):
        facilitator = ValidRecepient(email='henk@qwan.eu', name='Henk Wijngaard')
        message = aValidMessage(to=facilitator, subject="Hi Facilitator", body='My message')
        smtp_message = as_smtp_message(message)
        assert_that(smtp_message['To'], equal_to(message.recipient))
        assert_that(smtp_message['From'], equal_to(message.sender))
        assert_that(smtp_message['Subject'], equal_to(message.subject))
        assert_that(smtp_message.as_string().split('\n\n', 1)[1].strip(), equal_to(message.body))

def stringified_message(message):
    return '\r\n'.join(as_smtp_message(message).as_string().splitlines())

@dataclass
class ValidRecepient:
    name: str = 'F. Facilitator'
    email: str = 'henk@facilitators.com'

def aValidMessage(**kwargs):
    validArgs = dict(to= ValidRecepient(), subject= "Hi There", sender= "af@dop.eu", body= 'Hello Facilitator')
    return Message.for_named_recipient(**{**validArgs, **kwargs})


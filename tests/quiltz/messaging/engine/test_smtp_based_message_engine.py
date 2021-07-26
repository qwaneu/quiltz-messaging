from testing import *
from quiltz.testsupport.smtp import StubSmtpServer
import logging 
from dataclasses import dataclass
from quiltz.testsupport import probe_that, log_collector
from quiltz.messaging.engine.smtp import SMTPBasedMessageEngine, as_smtp_message
from quiltz.messaging.messenger import Message, Messenger
from quiltz.domain.results import Success, Failure, PartialSuccess
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
        self.messenger.send(aValidMessage(to=ValidRecipient(), subject="Hi Facilitator", body='My message'))
        self.message_engine.commit(self.messenger)

        probe_that(lambda: assert_that(self.server.messages, equal_to([
            stringified_message(self.messenger.messages[0])
        ])))

    def test_returns_success(self):        
        self.messenger.send(aValidMessage(to=ValidRecipient(), subject="Hi Facilitator", body='My message'))
        assert_that(self.message_engine.commit(self.messenger), equal_to(Success()))

    def test_sends_multiple_message_to_recipient(self):        
        self.messenger.send(aValidMessage(to=ValidRecipient(email="rob@mail.com"), subject="Hi Facilitator", body='My message'))
        self.messenger.send(aValidMessage(to=ValidRecipient(email="marc@mail.com"), subject="Hi Facilitator", body='My message'))
        self.message_engine.commit(self.messenger)

        probe_that(lambda: assert_that(self.server.messages, equal_to([
            stringified_message(message) for message in self.messenger.messages 
        ])))

    def test_logs_sending(self, log_collector):
        self.messenger.send(aValidMessage(to=ValidRecipient(email="rob@mail.com"), subject="Hi Facilitator", body='My message'))
        self.messenger.send(aValidMessage(to=ValidRecipient(email="marc@mail.com"), subject="Hi Facilitator", body='My message'))
        self.message_engine.commit(self.messenger)
        log_collector.assert_info('Flushed messages to {}, {}'.format(anonymize("rob@mail.com"), anonymize("marc@mail.com")))

    def test_logs_sending_failure(self, log_collector):
        self.server.send_message_returns('554 Transaction failed: Local address contains control or whitespace')
        self.messenger.send(aValidMessage(to=ValidRecipient(email="rob@mail.com"), subject="Hi Facilitator", body='My message'))
        self.message_engine.commit(self.messenger)
        log_collector.assert_warning('Failed sending message to {}: {}'.format(anonymize("rob@mail.com"), '[554] Transaction failed: Local address contains control or whitespace'))

    def test_returns_failure_when_message_fails_to_send(self):
        self.server.send_message_returns('554 Transaction failed: Local address contains control or whitespace', '554 Transaction failed: Local address contains control or whitespace')
        message = aValidMessage(to=ValidRecipient(), subject="Hi Facilitator", body='My message')
        self.messenger.send(message)
        self.messenger.send(message)
        assert_that(self.message_engine.commit(self.messenger), equal_to(PartialSuccess(message='Sending messages failed for: {}, {}'.format(message.recipient, message.recipient))))

    def test_returns_failure_when_only_one_message_fails_to_send(self):
        self.server.send_message_returns('554 Transaction failed: Local address contains control or whitespace')
        message1 = aValidMessage(to=ValidRecipient(email="failure@facilitators.com"), subject="Hi Facilitator", body='My message')
        message2 = aValidMessage(to=ValidRecipient(email="success@facilitators.com"), subject="Hi Facilitator", body='My message')
        self.messenger.send(message1)
        self.messenger.send(message2)
        self.messenger.send(message2)
        assert_that(self.message_engine.commit(self.messenger), equal_to(PartialSuccess(message='Sending messages failed for: {} and succeeded for: {}, {}'.format(message1.recipient, message2.recipient, message2.recipient))))


class TestSMTPBasedMessageEngineThatFailsOnNotBeinAbleToConnectToSMTPServer:
    @pytest.fixture(autouse=True)
    def setup(self):
        logging.getLogger('mail.log').setLevel(logging.WARN)
        self.SMTP_HOST = 'localhost'
        self.SMTP_PORT = '9925'
        self.FOR_TEST  = True
        self.message_engine = SMTPBasedMessageEngine.from_config(self)
        self.messenger = Messenger(sender='no-reply@messenger.bla', context=None)

    def test_returns_success(self):        
        self.messenger.send(aValidMessage(to=ValidRecipient(), subject="Hi Facilitator", body='My message'))
        assert_that(self.message_engine.commit(self.messenger), equal_to(Failure(message='[Errno 111] Connection refused')))


class TestSmtpMessageMapping:
    def test_message_contains_to_from_body(self):
        facilitator = ValidRecipient(email='henk@qwan.eu', name='Henk Wijngaard')
        message = aValidMessage(to=facilitator, subject="Hi Facilitator", body='My message')
        smtp_message = as_smtp_message(message)
        assert_that(smtp_message['To'], equal_to(message.recipient))
        assert_that(smtp_message['From'], equal_to(message.sender))
        assert_that(smtp_message['Subject'], equal_to(message.subject))
        assert_that(smtp_message.as_string().split('\n\n', 1)[1].strip(), equal_to(message.body))


def stringified_message(message):
    return '\r\n'.join(as_smtp_message(message).as_string().splitlines())


@dataclass
class ValidRecipient:
    name: str = 'F. Facilitator'
    email: str = 'henk@facilitators.com'


def aValidMessage(**kwargs):
    valid_args = dict(to=ValidRecipient(), subject="Hi There", sender="af@dop.eu", body='Hello Facilitator')
    return Message.for_named_recipient(**{**valid_args, **kwargs})


from testing import *
from quiltz.messaging.messenger import UnnamedRecipient, NamedRecipient
from dataclasses import dataclass

@dataclass
class SomeOneWithEMailAndName:
    email: str
    name: str

class TestNamedParticipant:
    def test_email_is_person_email(self):
        facilitator = SomeOneWithEMailAndName(email='henk@qwan.eu', name='Henk Wijngaard')
        assert_that(NamedRecipient(facilitator).email, equal_to('henk@qwan.eu'))

    def test_as_string_is_name_and_email(self):
        facilitator = SomeOneWithEMailAndName(email='henk@qwan.eu', name='Henk Wijngaard')
        assert_that(NamedRecipient(facilitator).as_string(), equal_to('Henk Wijngaard <henk@qwan.eu>'))

class TestUnNamedParticipant:
    def test_email_is_recepient(self):
        assert_that(UnnamedRecipient("henk@qwan.eu").email, equal_to('henk@qwan.eu'))

    def test_as_string_is_email(self):
        assert_that(UnnamedRecipient("henk@qwan.eu").as_string(), equal_to('henk@qwan.eu'))

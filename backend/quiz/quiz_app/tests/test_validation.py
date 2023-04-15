import unittest
from .. import validators


class TestValidator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.email_set = {
            'test@mail.ru': 'test@mail.ru',
            'test123@mail.ru': 'test123@mail.ru',
            'test!@mail.ru': None,
            'test@mail.!ru': None,
            'testmail.ru': None,
            'test!m!ail.ru': None,
            't-est.12_3@mail.ru': 't-est.12_3@mail.ru',
            'test@gmail.org.com': 'test@gmail.org.com',
            'test@gmail.orgcom': None,
            'test@123@gmail.com': None,
            'test@-gmail.com': None,
            'test@g-mail.com': 'test@g-mail.com',
        }
        cls.phone_set = {
            '375333333333': '375333333333',
            '+37533333': None,
            '375293333333': '375293333333',
            '375253333333': '375253333333',
            '375443333333': '375443333333',
            '375553333333': None,
            'abc': None,
            '123': None,
            '375333333333333333333': None,
            '+375(33)-33-33-876': '375333333876',
            '+7 953 3333333': '79533333333',
            '79943333333': '79943333333',
            '79993333333': '79993333333',
            '79333333333': '79333333333',
            '73333333333': None,
            '7999333333333333': None,
            '7999333333': None,
        }
        cls.name_set = {
            'Александра': 'Александра',
            'андрей': 'Андрей',
            'дмитрий': 'Дмитрий',
            'василий1': None,
            '1': None,
            'Игнат2454': None,
            'lyalya': 'Lyalya',
            'АлександраСергеевна': None,
            'Ol': None,
        }
        cls.username_set = {
            'Санюта14': 'Санюта14',
            'BAM-20': 'BAM-20',
            'lyalya_17': 'lyalya_17',
            '12345': '12345',
            'LuLu!': None,
            'bam@': None,
            'U': None,
        }

        cls.password_set = {
            'User58@!': 'User58@!',
            'BAMBAm-20': 'BAMBAm-20',
            'Lyalya%8': 'Lyalya%8',
            '12345678': None,
            'Lu!10': None,
            'bamparam@32': None,
            'USER254564&%!': None,
            'TratatiRA254564': None,
        }

    # @unittest.skip('already tested')
    def test_email(self):
        for fact_email, valid_email in self.email_set.items():
            with self.subTest(fact_email=fact_email, valid_email=valid_email):
                self.assertEqual(validators.validate_email(fact_email), valid_email)

    def test_username(self):
        for fact_username, valid_username in self.username_set.items():
            with self.subTest(fact_username=fact_username, valid_username=valid_username):
                self.assertEqual(validators.validate_username(fact_username), valid_username)

    # @unittest.skip('already tested')
    def test_password(self):
        for fact_password, valid_password in self.password_set.items():
            with self.subTest(fact_password=fact_password, valid_password=valid_password):
                self.assertEqual(validators.validate_password(fact_password), valid_password)

    # @unittest.skip('already tested')
    def test_phone(self):
        for fact_phone, valid_phone in self.phone_set.items():
            with self.subTest(fact_phone=fact_phone, valid_phone=valid_phone):
                self.assertEqual(validators.validate_phone(fact_phone), valid_phone)

    # @unittest.skip('already tested')
    def test_name(self):
        for fact_name, valid_name in self.name_set.items():
            with self.subTest(fact_name=fact_name, valid_name=valid_name):
                self.assertEqual(validators.validate_name(fact_name), valid_name)



if __name__ == "__main__":
    unittest.main()

from faker.providers import BaseProvider


class UkrainePhoneProvider(BaseProvider):
    def ukrainian_phone(self):
        operator = self.random_element(["39", "50", "63", "66", "67", "68", "73", "91", "92", "93", "94", "95", "96", "97", "98", "99"])
        number = self.random_number(digits=7, fix_len=True)
        print(f"+380{operator}{number}")
        return f"+380{operator}{number}"
class Filters:
    phone_number: str
    name: str
    last_name: str

    def __int__(self, name=None):
        self.name = name

    @classmethod
    def phone_number(cls):
        return cls.phone_number


def g(ftr: Filters, **kwargs):
    print(f"GGG::: {ftr.phone_number}: {kwargs}")

    # for kw, name in kwargs.items():
    #     print(f"GGG::: {ftr.phone_number}: {name}")
    # # try:
    #     for kw, name in kwargs.items():
    #         print(f"GGG::: {ftr[kw]}: {name}")
    # except TypeError as e:
    #     print(e)
    # else:
    #     return ftr


if __name__ == '__main__':
    f = Filters()
    payload = dict(
        dateFrom='2022-05-01',
        dateTo='2022-08-15',
        phoneNumber='+79162047558')
    print(f.phone_number)
    # o = dict(phone_number='foo')
    # g(ftr=f, **o)

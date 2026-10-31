class Money:
    __slots__ = ('amount', 'currency')

    def __init__(self, amount, currency):
        object.__setattr__(self, 'amount', amount)
        object.__setattr__(self, 'currency', currency)

    def __setattr__(self, name, value):
        raise AttributeError('Money is immutable')

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __hash__(self):
        return hash((self.amount, self.currency))

    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError('cannot add different currencies')
        return Money(self.amount + other.amount, self.currency)

    def __repr__(self):
        return f"Money({self.amount}, {self.currency!r})"


def total_by_currency(payments):
    result = {}
    for m in payments:
        if m.currency in result:
            result[m.currency] = result[m.currency] + m
        else:
            result[m.currency] = m
    return result

if __name__ == '__main__':
    assert len({Money(100, 'RUB'), Money(100, 'RUB'), Money(100, 'USD')}) == 2
    prices = {Money(100, 'RUB'): 'сто рублей'}
    assert prices[Money(100, 'RUB')] == 'сто рублей'
    assert Money(100, 'RUB') + Money(50, 'RUB') == Money(150, 'RUB')
    for action in (lambda m: setattr(m, 'amount', 5), lambda m: setattr(m, 'extra', 1)):
        try:
            action(Money(1, 'RUB'))
            assert False, 'ожидали AttributeError'
        except AttributeError:
            pass
    try:
        Money(1, 'RUB') + Money(1, 'USD')
        assert False, 'ожидали ValueError'
    except ValueError:
        pass
    pays = [Money(100, 'RUB'), Money(5, 'USD'), Money(250, 'RUB')]
    assert total_by_currency(pays) == {'RUB': Money(350, 'RUB'), 'USD': Money(5, 'USD')}

    # Вопрос: что сломалось бы, если бы поля можно было менять после того,
    # как объект положили в множество или использовали как ключ?
    #
    # Если бы поля Money можно было менять после того, как объект положили в set
    # или сделали ключом dict, то сломался бы контракт a == b  =>  hash(a) == hash(b).
    # После изменения поля хэш тоже поменяется, хоть и физически объект останется
    # в старой корзине.
    # В лекции это показано на Point: когда мы добавили __hash__, объект стало можно
    # класть в set. Но при попытке написать A.x = 5 - A оказался бы не в той корзине,
    # в какой бы его искали. По сути python его просто не найдет. Поэтому мы делаем
    # неизменяемыми поля, чтобы хэш не менялся после того, как объект создан.
import time

class MyDict:
    def __init__(self, size=8):
        self._buckets = [[] for _ in range(size)]
        self._len = 0

    def _bucket_for(self, key):
        return self._buckets[hash(key) % len(self._buckets)]
                             
    def __setitem__(self, key, value):
        bucket = self._bucket_for(key)
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value
                return
        bucket.append([key, value])
        self._len += 1
        if self._len > 2 * len(self._buckets) / 3:
            self._resize()

    def __getitem__(self, key):
        bucket = self._bucket_for(key)
        for pair in bucket:
            if pair[0] == key:
                return pair[1]
        raise KeyError(key)

    def __delitem__(self, key):
        bucket = self._bucket_for(key)
        for i in range(len(bucket)):
            if bucket[i][0] == key:
                del bucket[i]
                self._len -= 1
                return
        raise KeyError(key)

    def __contains__(self, key):
        bucket = self._bucket_for(key)
        for pair in bucket:
            if pair[0] == key:
                return True
        return False

    def __len__(self):
        return self._len

    def get(self, key, default=None):
        bucket = self._bucket_for(key)
        for pair in bucket:
            if pair[0] == key:
                return pair[1]
        return default

    def _resize(self):
        old = self._buckets
        new_size = len(old) * 2
        self._buckets = [[] for _ in range(new_size)]
        for bucket in old:
            for key, value in bucket:
                self._buckets[hash(key) % new_size].append([key, value])

    def stats(self):
        longest = 0
        for bucket in self._buckets:
            if len(bucket) > longest:
                longest = len(bucket)
        return (len(self._buckets), self._len, longest)

    def __repr__(self):
        parts = []
        for bucket in self._buckets:
            for key, value in bucket:
                parts.append(f'{key!r}: {value!r}')
        return 'MyDict({' + ', '.join(parts) + '})'

if __name__ == '__main__':
    d = MyDict()
    for i in range(1000):
        d[f'key{i}'] = i
    assert len(d) == 1000
    assert d['key42'] == 42
    assert 'key7' in d and 'nope' not in d
    d['key42'] = -1
    assert d['key42'] == -1 and len(d) == 1000
    del d['key42']
    assert 'key42' not in d and len(d) == 999
    assert d.get('nope') is None and d.get('nope', 0) == 0
    for bad in (lambda: d['nope'], lambda: d.__delitem__('nope')):
        try:
            bad()
            assert False, 'ожидали KeyError'
        except KeyError:
            pass
    buckets, size, longest = d.stats()
    assert size == 999 and size <= buckets * 2 / 3
    print(d.stats())


    # --- эксперимент ---

    # 1) обычные строковые ключи
    d = MyDict()
    start = time.perf_counter()
    for i in range(1000):
        d[f'key{i}'] = i
    print('строки:')
    print('  время:', time.perf_counter() - start)
    print('  stats:', d.stats())

    # 2) ключи, у которых hash всегда 42
    class Bad:
        def __hash__(self):
            return 42

    d = MyDict()
    keys = []
    for i in range(1000):
        keys.append(Bad())
    start = time.perf_counter()
    for i in range(1000):
        d[keys[i]] = i
    print('hash=42:')
    print('  время:', time.perf_counter() - start)
    print('  stats:', d.stats())

# Вопрос 1: почему при увеличении таблицы пары нельзя просто скопировать в корзины с теми же номерами?
#
# Номер корзины считается как hash(key) % len(self._buckets). Когда увеличивается количество корзин,
# увеличивается и len(self._buckets), то есть остаток от деления для того же ключа может измениться.
# Поэтому в _resize мы заново считаем hash(key) % new_size и раскладываем пары в новые корзины.

# Вопрос 2: Что показывает stats() для 1000 строковых ключей и что он покажет, если ключами будут объекты,
# у которых __hash__ всегда возвращает 42? Проверьте экспериментом и замерьте вставки 1000 таких ключей.
#
# Для обычных строковых ключей stats() выведет что-то вроде (2048, 1000, 4). Количество корзин 2048 из-за
# того, что количество корзин увеличивается, когда количество пар больше 2/3 корзин, то есть зависимость
# только от количества пар, а не от того, сколько корзин заполнено. Может быть и такое,
# что в корзине 3-4 ключа, а в другой корзине нет ничего. Если ключами будут объекты, у которых
# __hash__ всегда возвращает 42, то корзин тоже будет 2048, но все пары будут в одной корзине.
# Тогда stats() покажет (2048, 1000, 1000). Я добавила немного кода, чтобы замерить время и проверить 
# stats() - как результат время с обычными ключами: 0.00206, а с hash=42: 0.02447, то есть второй вариант
# в 10 раз дольше.
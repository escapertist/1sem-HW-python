import functools


def memoize(func):
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            key = (args, tuple(sorted(kwargs.items())))
            hash(key)
        except TypeError:
            return func(*args, **kwargs)

        if key in cache:
            wrapper.hits = wrapper.hits + 1
            return cache[key]

        wrapper.misses = wrapper.misses + 1
        result = func(*args, **kwargs)
        cache[key] = result
        return result

    def cache_clear():
        cache.clear()
        wrapper.hits = 0
        wrapper.misses = 0

    wrapper.hits = 0
    wrapper.misses = 0
    wrapper.cache_clear = cache_clear

    return wrapper


if __name__ == '__main__':
    calls = []

    def slow_square(x, power=2):
        '''Возводит в степень.'''
        calls.append(x)
        return x ** power

    sq = memoize(slow_square)
    assert sq(3) == 9 and sq(3) == 9 and sq(3, power=3) == 27
    assert calls == [3, 3]
    assert (sq.hits, sq.misses) == (1, 2)
    assert sq.__name__ == 'slow_square' and sq.__doc__ == 'Возводит в степень.'
    total = memoize(sum)
    assert total([1, 2, 3]) == 6 and total([1, 2, 3]) == 6   # нехешируемый аргумент: вызов без кэша
    assert (total.hits, total.misses) == (0, 0)
    sq.cache_clear()
    assert (sq.hits, sq.misses) == (0, 0)
    sq(3)
    assert calls[-1] == 3
    print('ok')

    # Эксперимент с рекурсией
    # Сравним оба варианта и для каждого выведем misses после вызова с n = 30 и время работы
    
    import time

    # Вариант A (fast_fib = memoize(fib))
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    print('\nЭксперимент с рекурсией:')
    
    fast_fib = memoize(fib)
    start = time.perf_counter()
    result = fast_fib(30)
    end = time.perf_counter()
    print('Вариант A:')
    print('- result:', result)
    print('- misses:', fast_fib.misses)
    print('- time:', round(end - start, 4), 'сек')

    # Вариант B (fib = memoize(fib)). Здесь создаем чистую fib заново
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    fib = memoize(fib)
    start = time.perf_counter()
    result = fib(30)
    end = time.perf_counter()
    print('Вариант B:')
    print('- result:', result)
    print('- misses:', fib.misses)
    print('- time:', round(end - start, 4), 'сек')


# Комментарий к эксперименту с рекурсией:
#
# В варианте A (fast_fib = memoize(fib)) рекурсивный вызов fib(n - 1) ищет имя 
# fib по правилу LEGB, то есть в глобальной области лежит исходная, 
# некэшированная функция. Поэтому рекурсия идет мимо кэша и misses = 1, 
# а время работы n=30 составило примерно 0.18 секунд.
# В варианте B (fib = memoize(fib)) глобальное имя fib перезаписано.
# Теперь рекурсивный вызов находит именно кэшированную версию, поэтому 
# вычисление n=30 требует всего 31 промаха, а время падает в разы, до 0.0001 секунд.
class SearchIndex:
    """
    Структуры данных, чтобы не перебирать весь индекс:
    - index: словарь {слово: set(doc_id)}. Нужен для быстрого поиска.
    - doc_words: словарь {doc_id: set(слов)}. Позволяет remove брать
      слова только этого документа и чистить их в индексе.
    - word_count: словарь {слово: количество}. Нужен для top_words.
    """

    def __init__(self):
        self.index = {}
        self.doc_words = {}
        self.word_count = {}

    def add(self, doc_id, text):
        if doc_id in self.doc_words:
            self.remove(doc_id)

        words = []
        for w in text.lower().split():
            clean_w = w.strip(".,!?;:()[]{}'\"")
            if clean_w != "":
                words.append(clean_w)

        self.doc_words[doc_id] = set(words)

        for w in words:
            if w not in self.index:
                self.index[w] = set()
            self.index[w].add(doc_id)
            
            self.word_count[w] = self.word_count.get(w, 0) + 1

    def search_all(self, *words):
        if len(words) == 0:
            return set()

        first = words[0].lower()
        if first not in self.index:
            return set()
        result = set(self.index[first])

        i = 1
        while i < len(words):
            w = words[i].lower()
            if w not in self.index:
                return set()

            new_result = set()
            for doc_id in result:
                if doc_id in self.index[w]:
                    new_result.add(doc_id)
            result = new_result
            i = i + 1

        return result

    def search_any(self, *words):
        result = set()
        for w in words:
            w = w.lower()
            if w in self.index:
                for doc_id in self.index[w]:
                    result.add(doc_id)
        return result

    def remove(self, doc_id):
        if doc_id not in self.doc_words:
            return

        words = self.doc_words[doc_id]
        del self.doc_words[doc_id]

        for w in words:
            self.index[w].remove(doc_id)
            if len(self.index[w]) == 0:
                del self.index[w]

            self.word_count[w] = self.word_count[w] - 1
            if self.word_count[w] == 0:
                del self.word_count[w]

    def top_words(self, n):
        pairs = []
        for w in self.word_count:
            pairs.append((w, self.word_count[w]))


        def sort_key(pair):
            word = pair[0]
            count = pair[1]
            return (-count, word)

        pairs.sort(key=sort_key)

        result = []
        i = 0
        while i < len(pairs) and i < n:
            result.append(pairs[i])
            i = i + 1
        return result


if __name__ == '__main__':
    idx = SearchIndex()
    idx.add(1, 'Python is a programming language.')
    idx.add(2, 'A dict is a hash table; a set is a hash table too!')
    idx.add(3, 'Python dict and set are fast.')
    assert idx.search_all('python') == {1, 3}
    assert idx.search_all('dict', 'set') == {2, 3}
    assert idx.search_all('python', 'hash') == set()
    assert idx.search_any('language', 'fast') == {1, 3}
    assert idx.search_all('PYTHON') == {1, 3}
    assert idx.search_all('nothing') == set()
    assert idx.top_words(2) == [('a', 5), ('is', 3)]
    idx.remove(1)
    assert idx.search_all('python') == {3}
    assert idx.search_any('language', 'programming') == set()
    idx.add(3, 'Totally new text')
    assert idx.search_all('python') == set()
    assert idx.search_all('new') == {3}
    print('ok')

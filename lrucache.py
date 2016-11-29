# -*- coding:utf-8 -*-
import threading


class CacheNode(object):

    def __init__(self, key=None, value=None):
        self.prev = None
        self.next = None
        self.key = key
        self.value = value

    def escape(self):
        self.prev.next = self.next
        self.next.prev = self.prev
        self.prev = None
        self.next = None

    def link(self, node):
        self.next = node
        node.prev = self


class LruCache(object):

    def __init__(self, item_limit):
        self.item_limit = item_limit
        self.virtual_head = CacheNode()
        self.virtual_tail = CacheNode()
        self.virtual_head.link(self.virtual_tail)
        self.cache = {}
        self.lock = threading.Lock()

    def set(self, key, value):
        if self.item_limit <= 0:
            return

        with self.lock:
            if key in self.cache:
                node = self.cache[key]
                node.escape()
                self.__set_head(node)
                node.value = value
            else:
                if len(self.cache) >= self.item_limit:
                    node = self.virtual_tail.prev
                    node.escape()
                    self.cache.pop(node.key)

                node = CacheNode(key, value)
                self.__set_head(node)
                self.cache[key] = node

    def get(self, key, default=None):
        with self.lock:
            if key in self.cache:
                node = self.cache[key]
                node.escape()
                self.__set_head(node)
                return node.value
            else:
                return default

    def __set_head(self, node):
        old_head = self.virtual_head.next
        self.virtual_head.link(node)
        node.link(old_head)

    def __repr__(self):
        ret = []

        ret.append('cache:')
        for key, node in self.cache.items():
            ret.append('  %r => %r' % (key, node.value))

        ret.append('queue:')
        node = self.virtual_head.next
        while node != self.virtual_tail:
            ret.append('  %r => %r' % (node.key, node.value))
            node = node.next

        ret.append('--')

        return '\n'.join(ret)


def main():
    lru = LruCache(4)
    lru.set(1, 'one')
    lru.set(2, 'two')
    lru.set(3, 'three')
    print lru

    lru.set(2, 'TWO')
    print lru

    lru.set(4, 'four')
    print lru

    lru.set(5, 'five')
    print lru

    lru.set(5, 'FIVE')
    print lru

    lru.set(3, '??')
    print lru

    ret = lru.get(2)
    print ret
    print lru


if __name__ == '__main__':
    main()

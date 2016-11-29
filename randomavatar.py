# -*- coding:utf-8 -*-
import struct
import StringIO
import PIL
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import lrucache

from PIL import Image, ImageOps, ImageDraw
from tornado.options import define, options


define("port", default=8888, help="run on the given port", type=int)
define('color_config_file', default='color.conf')
define('colors', multiple=True)
define('min_avatar_size', default=1, type=int)
define('max_avatar_size', default=300, type=int)
define('default_avatar_size', default=72, type=int)
define('cache_items', default=1000, type=int)


def hex2rgb(hex_code):
    return struct.unpack('BBB', hex_code.decode('hex'))


def select_by_mod(arr, i):
    return arr[i % len(arr)]


def generate_colors(key):
    color_group = select_by_mod(options.colors, key)
    order = select_by_mod(((0, 1, 2), (1, 2, 3), (3, 2, 1), (2, 1, 0)), key) # 相邻三色较协调
    return [hex2rgb(color_group[i*6 : (i+1)*6]) for i in order]


def generate_avatar(key, size):
    colors = generate_colors(key)

    b = int(size * 0.06) # border width
    r1 = int(size * 0.24)
    r2 = r1 - b
    m = size / 2

    board = Image.new('RGB', (size, size), colors[1])

    draw = ImageDraw.Draw(board)
    draw.ellipse((b, b, size-b, size-b), fill=colors[0])
    draw.rectangle((0, m-b, size, m+b), fill=colors[1])
    draw.ellipse((m-r1, m-r1, m+r1, m+r1), fill=colors[1])
    draw.ellipse((m-r2, m-r2, m+r2, m+r2), fill=colors[2])

    mask = Image.new('L', (size, size), 0)

    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)

    avatar = ImageOps.fit(board, (size, size))
    avatar.putalpha(mask)
    return avatar


class RandomAvatarHandler(tornado.web.RequestHandler):

    def initialize(self, avatar_cache):
        self.avatar_cache = avatar_cache

    def parse_avatar_size(self, raw_size):
        if raw_size is None:
            size = options.default_avatar_size
        else:
            size = 0
            try:
                size = int(raw_size)
            except:
                size = options.default_avatar_size

        if size < options.min_avatar_size:
            size = options.min_avatar_size

        if size > options.max_avatar_size:
            size = options.max_avatar_size

        return size

    def get(self, **params):
        key = hash(params['avatar_name'])
        avatar_size = self.parse_avatar_size(self.get_argument("size", None))
        avatar_file = self.avatar_cache.get(key ^ avatar_size)

        if avatar_file is None:
            avatar = generate_avatar(key, avatar_size)
            output = StringIO.StringIO()
            avatar.save(output, format='PNG')
            avatar_file = output.getvalue()
            self.avatar_cache.set(key ^ avatar_size, avatar_file)

        self.set_header('Content-type', 'image/png')
        self.set_header('Content-length', len(avatar_file))
        self.write(avatar_file)


def main():
    tornado.options.parse_command_line()
    tornado.options.parse_config_file(options.color_config_file)
    avatar_cache = lrucache.LruCache(options.cache_items)
    application = tornado.web.Application([
        (r"/(?P<avatar_name>[^\/]+)\.png", RandomAvatarHandler, {'avatar_cache': avatar_cache}),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()

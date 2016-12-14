#coding=utf-8
from __future__ import print_function, unicode_literals

import pyte


# if __name__ == "__main__":
#     stream = pyte.Stream()
#     screen = pyte.Screen(80, 24)
#     stream.attach(screen)
#     stream.feed("Hello World!")
#
#     #screen.display是个列表
#     #enumerate(screen.display, 1) 返回一个类似带索引的东西
#
#     for idx, line in enumerate(screen.display, 1):
#         # print (idx,"#",line)
#         #format通过位置来替换字符
#         print("{0:2d} {1}#".format(idx, line,'hehe'))

#------------------------------
#反转遍历
# for i in reversed([2, 3, 4, 5]):
#     print(i)

#--------------------------------------

from operator import *


class MyObj(object):
    def __init__(self, arg):
        super(MyObj, self).__init__()
        self.arg = arg

    def __repr__(self):
        return 'MyObj(%s)' % self.arg


objs = [MyObj(i) for i in xrange(5)]
print ("Object:", objs)
# print (type(objs[0]))
g = attrgetter("arg")

vals = [g(i) for i in objs]
print ("arg values:", vals)



objs.reverse()
print ("reversed:", objs)
print ("sorted:", sorted(objs, key=g))

obj1 = MyObj('test')
print (g(obj1))
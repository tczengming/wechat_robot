# -*- coding: utf-8 -*-

import os
import sys

BASE_DIR = './小助手'

#遍历文件夹
def find_from_dir(dirname, name):
    print('find ', name, ' from', dirname)
    ret = {}
    ret['path'] = ''
    ret['type'] = ''
    for root, dirs, files in os.walk(dirname):

        # root 表示当前正在访问的文件夹路径
        # dirs 表示该文件夹下的子目录名list
        # files 表示该文件夹下的文件list

        # 遍历文件
        for f in files:
            #print(f.split('.')[0:-1][0])
            if name == f.split('.')[0:-1][0]:
                ret['path'] = os.path.join(root, f)
                ret['type'] = 'file'
                return ret

        # 遍历所有的文件夹
        for d in dirs:
            if name == d:
                ret['path'] = (os.path.join(root, d))
                ret['type'] = 'dir'
                return ret
    return ret

def get_help(name):
    print('get_help:', name)
    if name == '小助手':
        print('hit help')
        cmd = 'tree -L 1 --noreport -d ' + BASE_DIR
        #print('cmd:', cmd)
        tree = os.popen(cmd)
        return tree.read()
    else:
        print('hit find dir')
        ret = find_from_dir(BASE_DIR, name)
        print(ret)
        if len(ret['path']) > 0:
            if ret['type'] == 'dir':
                tree = os.popen('tree --noreport ' + ret['path'])
                return tree.read()
            else:
                return ret['path']
        else:
            print('find_from_dir failed')
            return '不支持'


if __name__ == '__main__':
    print(get_help(sys.argv[1]))
    #print(len('小助手'.split('：')))

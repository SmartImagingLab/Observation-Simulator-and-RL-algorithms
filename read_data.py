import random
import ephem
import numpy as np
random.seed(1314)
"""
卫星的数据批量读取
"""
def judge_Input(line: str, modify: str, initial: str or list):
    if type(initial) == str:
        if len(initial) != len(modify):
            raise TypeError("initial和modify的长度不一致！！")
        elif line.count(initial) != 1:
            raise TypeError("没有满足要求的字符串，或者满足要求的不止一个！！建议使用列表指定修改区间。")
        else:
            pass
    elif type(initial) == list:
        if len(initial) != 2:
            raise TypeError("initial的列表长度不合法，应该为2！！")
        elif initial[1] - initial[0] != len(modify):
            print(initial[0],initial[1],initial[1] - initial[0])
            print(modify,len(modify))
            print(line)
            print(list(line)[initial[1]:initial[0]])
            print(modify)
            raise TypeError("initial设定的区间长度和modify的长度不一致！！")
        else:
            pass
    else:
        pass

def get_modify_location(line: str, initial: str or list):
    if type(initial) == list:
        return initial[0], initial[1]
    elif type(initial) == str:
        return line.find(initial), line.find(initial) + len(initial)
    else:
        raise TypeError("Input输入格式不合法")

def modify_tle(line: str, modify: str, start: int, end: int = None):
    line_list = list(line)
    if end != None:
        line_list[start:end] = list(modify)
    else:
        line_list[start] = str(modify)
    line_new = ''.join(line_list)
    return line_new

def cal_check_num(line: str):
    line_list = list(line)
    res = 0
    for i in line_list[:-2]:
        if 48 <= ord(i) <= 57:
            res += int(i)
        elif ord(i) == 45:
            res += 1
        else:
            pass
    return res % 10


def tle_new(line, modify, initial):
    '''1.输入格式判断'''
    judge_Input(line, modify, initial)
    '''2.返回修改位置'''
    start, end = get_modify_location(line, initial)
    '''3.修改tle的函数'''
    line = modify_tle(line, modify, start, end)
    '''4.计算校验码'''
    check_num = cal_check_num(line)
    '''5.修改校验码(可以和3一样)'''
    line = modify_tle(line, str(check_num), -2)
    return line

def judge_len(nums):
    nums = str(nums)
    if nums.count(".") > 1:
        raise TypeError()
    elif nums.count(".") == 0:
        return len(nums), 0
    else:
        s = len(nums)
        z = nums.find(".")
        d = s - z - 1
    return s, z, d

def modify_nums(nums, s,the_range):
    n1, z1, d1 = judge_len(nums)
    new_nums = round(np.clip(float(np.random.normal(float(nums), s, 1)),the_range[0],the_range[1]),d1)
    n2, z2, d2 = judge_len(new_nums)
    if n1 == n2:
        d = '.' + str(d1) + "f"
        return str(format(new_nums, d))
    elif n2 > n1:
        d = '.' + str(d1+n1-n2) + "f"
        return str(format(new_nums, d))
    elif n2 < n1:
        return str(new_nums).zfill(n1)
    else:pass


'''
读轨道数据
'''
def read_tle(flie_name):
    with open(flie_name,"r") as f :
        linenumber = 0
        star_tle = []
        the_tle = dict()
        for line in f.readlines():
            linenumber += 1
            if linenumber % 3 == 1:
                the_tle.update({'line1': line})
            if linenumber % 3 == 2:
                the_tle.update({'line2': line})
            if linenumber % 3 == 0:
                the_tle.update({'line3': line})
                star_tle.append(the_tle.copy())
                the_tle.clear()
    return star_tle


"""
彗星的数据批量读取
"""
def read_ddb(flie_name):
    with open(flie_name,"r") as f :
        linenumber = 0
        star_ddb = []
        the_ddb = dict()
        for line in f.readlines():
            linenumber += 1
            if linenumber % 2 == 0:
                the_ddb.update({'ddb': line})
                star_ddb.append(the_ddb.copy())
                the_ddb.clear()
    return star_ddb

"""
恒星的数据批量读取
"""
def read_fix(file_name):
    with open(file_name,"r") as f :
        star_fix = []
        the_ddc = dict()
        for line in f.readlines():
            the_ddc.update({'ddc': line})
            star_fix.append(the_ddc.copy())
            the_ddc.clear()
    return star_fix

"""
小行星（Bright and CritList and Distant and Unusual）的数据批量读取
"""
def read_minorplanet(flie_name):
    with open(flie_name,"r") as f :
        linenumber = 0
        star_dde = []
        the_dde = dict()
        for line in f.readlines():
            linenumber += 1
            if linenumber % 2 == 0:
                the_dde.update({'dde': line})
                star_dde.append(the_dde.copy())
                the_dde.clear()
    return star_dde








# -*- coding: utf-8 -*-
import numpy as np
import geatpy as ea
from global_land_mask import globe
from WorldLight import world_lightness
from Environment_simulator import Environment_simulator
import os

def bool_to_int(x):return int(x)
def is_land(lat, lon):
    is_on_land = globe.is_land(lat, lon)
    if type(lat) == "float" or "int":
        return is_on_land
    else:
        return np.array(list(map(bool_to_int,is_on_land)))

"""
目的：优化光学望远镜观测位置
限制条件：灯光，陆地，云量(?)
"""

curr_path = os.path.dirname(os.path.abspath(__file__))  # 当前文件所在绝对路径
parent_path = os.path.dirname(curr_path)  # 父路径
class MyProblem(ea.Problem):  # 继承Problem父类
    def __init__(self):
        name = 'MyProblem'  # 初始化name（函数名称，可以随意设置）
        M = 1  # 初始化M（目标维数）
        maxormins = [-1]  # 初始化目标最小最大化标记列表，1：min；-1：max
        Dim = 2  # 初始化Dim（决策变量维数）
        varTypes = [0] * Dim  # 初始化决策变量类型，0：连续；1：离散
        lb = [-65, -175]  # 决策变量下界
        ub = [65, 175]  # 决策变量上界
        lbin = [0, 0]  # 决策变量下边界
        ubin = [0, 0]  # 决策变量上边界
        # 调用父类构造方法完成实例化
        ea.Problem.__init__(self, name, M, maxormins, Dim, varTypes, lb,
                        ub, lbin, ubin)
        self.wl = world_lightness()
        self.ini_path = "/config/env.ini "
        self.env = Environment_simulator(ini_path=curr_path + self.ini_path)

    def aimFunc(self, pop):  # 目标函数，pop为传入的种群对象
         Vars = pop.Phen  # 得到决策变量矩阵
         x1 = Vars[:, [0]]  # 取出第一列得到所有个体的x1组成的列向量
         x2 = Vars[:, [1]]  # 取出第二列得到所有个体的x2组成的列向量

         ObjV = []
         for i in range(pop.sizes):
             lat = x1[i][0]
             lon = x2[i][0]

             for ob in self.env.Monitoring_Center.Observatorys:
                 ob.lat = lat
                 ob.lon = lon
             self.env.reset()
             for i in range(24 * 60):
                 self.env.step()
             ObjV.append([len(self.env.Monitoring_Center.know_object["satellite"])])
         pop.ObjV = np.array(ObjV)

         # TODO 目标函数值（观测效能）
         # 采用可行性法则处理约束，生成种群个体违反约束程度矩阵
         pop.CV = np.hstack([is_land(x1, x2)- 1,  # TODO 约束1：海岸线
                             self.wl.read_light(x1,x2) - 1])  # TODO 约束2：光污染


if __name__ == '__main__':
    """================================实例化问题对象==========================="""
    problem = MyProblem() # 生成问题对象
    """==================================种群设置==============================="""
    Encoding = 'RI'       # 编码方式
    NIND = 50            # 种群规模
    Field = ea.crtfld(Encoding, problem.varTypes, problem.ranges, problem.borders) # 创建区域描述器
    population = ea.Population(Encoding, Field, NIND) # 实例化种群对象（此时种群还没被初始化，仅仅是完成种群对象的实例化）
    """================================算法参数设置============================="""
    myAlgorithm = ea.soea_DE_rand_1_bin_templet(problem, population) # 实例化一个算法模板对象
    myAlgorithm.MAXGEN = 200 # 最大进化代数
    myAlgorithm.mutOper.F = 0.5 # 差分进化中的参数F
    myAlgorithm.recOper.XOVR = 0.7 # 重组概率
    """===========================调用算法模板进行种群进化======================="""
    [population, obj_trace, var_trace] = myAlgorithm.run() # 执行算法模板
    population.save() # 把最后一代种群的信息保存到文件中
    # 输出结果
    best_gen = np.argmin(problem.maxormins * obj_trace[:, 1]) # 记录最优种群个体是在哪一代
    best_ObjV = obj_trace[best_gen, 1]
    print('最优的目标函数值为：%s'%(best_ObjV))
    print('最优的决策变量值为：')
    for i in range(var_trace.shape[1]):
        print(var_trace[best_gen, i])
    print('有效进化代数：%s'%(obj_trace.shape[0]))
    print('最优的一代是第 %s 代'%(best_gen + 1))
    print('评价次数：%s'%(myAlgorithm.evalsNum))
    print('时间已过 %s 秒'%(myAlgorithm.passTime))

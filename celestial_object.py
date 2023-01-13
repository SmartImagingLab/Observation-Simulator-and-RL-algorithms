import ephem
import numpy as np
from numpy import exp,nan,inf
import random
import observatory
from read_data import *

class celestical_object():
    def __init__(self, signal: int, orbital: dict):
        self.signal = signal  # 目标编号
        self.orbital = orbital

    def orbital_upgrade(self) -> None:
        '''
        根据天体可能发生的变化，对天体的轨道进行进行调整
        :return:
        '''
        pass

    def status_upgrade(self, time:ephem.Date = None, observatory:observatory = None) -> None:
        '''
        根据轨道数据，计算天体在当前时间的位置和星等
        :param time:时间，type(？)
        param observatory:观测站
        :return:返回一个实例，可以
        '''
        pass


class satellite(celestical_object):
    def __init__(self, signal: int, orbital : dict, unormal_epoch:list = None,scale: float = 1.0) -> None:
        celestical_object.__init__(self, signal, orbital)
        self.scale = scale
        self.tle = orbital
        self.unormal_epoch = unormal_epoch
        self.first_derivative, self.second_derivative, self.round, self.all_rounds = self.tle_data()
        self.cycle = 24 * 60 * 60 / self.round / 4
        self.type = 1  # 代表卫星
        self.ephem_body = ephem.readtle(self.tle['line1'], self.tle['line2'], self.tle['line3'])

    def orbital_upgrade(self, time = None,step_time = None,normal=True) -> None:
        if self.unormal_epoch is None:
            normal = True
        elif self.unormal_epoch[0] <= time <= self.unormal_epoch[0]:
            normal = False
        else:
            normal = True
        if normal == True:
            s = 0.2 * step_time
        else:
            s = 5 * step_time
        inc = self.tle['line3'][8:16]
        inc_modify = modify_nums(inc, s,[0.001,180])
        line = tle_new(self.tle['line3'], inc_modify, [8, 16])
        raan = line[17:25]
        raan_modify = modify_nums(raan, s,[0.001,360])
        self.tle['line3'] = tle_new(line, raan_modify, [17, 25])
        self.ephem_body = ephem.readtle(self.tle['line1'], self.tle['line2'], self.tle['line3'])

    def status_upgrade(self, time:ephem.Date = None, observatory:observatory = None) :
        if time is None and observatory is None:
            self.ephem_body.compute()
        elif time is not None and observatory is None:
            self.ephem_body.compute(time)
        elif time is None and observatory is not None:
            self.ephem_body.compute(observatory)
        else:
            raise StopIteration("neither time nor observer is none.")
        return self.ephem_body


    def tle_data(self) -> (float, float, float, float):
        '''
        根据tle数据提取卫星的一阶运动导数，二阶运动倒数，周期和发射以来的周期总数
        :return:一阶运动导数，二阶运动倒数，周期和发射以来的周期总数
        '''
        line1 = self.tle['line1']
        line2 = self.tle['line2']
        line3 = self.tle['line3']
        first_derivative = float(line2[33:43])
        # second_derivative = float(line2[44:52])
        round = float(line3[52:63])
        all_round = float(line3[63:68])
        return first_derivative, 0.0, round, all_round

class Body(celestical_object):
    def __init__(self, signal, orbital):
        celestical_object.__init__(self, signal, orbital)
        self.type = 2

        self.ephem_body = self.orbital

    def status_upgrade(self,time = None, observatory = None):
        if time == None and observatory == None:
            self.ephem_body.compute()
        elif time != None and observatory == None:
            self.ephem_body.compute(time)
        elif time == None and observatory != None:
            self.ephem_body.compute(observatory)
        else:
            raise StopIteration("neither time nor observer is none.")
        return self.ephem_body

class star(celestical_object):
    def __init__(self, signal, orbital):
        celestical_object.__init__(self, signal, orbital)
        self.ddc = orbital
        self.type = 3
        self.ephem_body = ephem.readdb(self.ddc['ddc'])

    def status_upgrade(self,time = None, observatory = None):
        if time == None and observatory == None:
            self.ephem_body.compute()
        elif time != None and observatory == None:
            self.ephem_body.compute(time)
        elif time == None and observatory != None:
            self.ephem_body.compute(observatory)
        else:
            raise StopIteration("neither time nor observer is none.")
        return self.ephem_body

class comet(celestical_object):
    def __init__(self, signal, orbital):
        celestical_object.__init__(self, signal, orbital)
        self.ddb = orbital
        self.type = 4

        self.ephem_body = ephem.readdb(self.orbital['ddb'])

    def status_upgrade(self,time = None, observatory = None):
        if time == None and observatory == None:
            self.ephem_body.compute()
        elif time != None and observatory == None:
            self.ephem_body.compute(time)
        elif time == None and observatory != None:
            self.ephem_body.compute(observatory)
        else:
            raise StopIteration("neither time nor observer is none.")
        return self.ephem_body

class bright_planet(celestical_object):
    def __init__(self, signal, orbital):
        celestical_object.__init__(self, signal, orbital)
        self.dde = orbital
        self.type = 5

        self.ephem_body = ephem.readdb(self.dde['dde'])

    def status_upgrade(self, time = None, observatory = None):
        if time == None and observatory == None:
            self.ephem_body.compute()
        elif time != None and observatory == None:
            self.ephem_body.compute(time)
        elif time == None and observatory != None:
            self.ephem_body.compute(observatory)
        else:
            raise StopIteration("neither time nor observer is none.")
        return self.ephem_body

class distant_planet(celestical_object):
    def __init__(self, signal, orbital):
        celestical_object.__init__(self, signal, orbital)
        self.dde = orbital
        self.type = 6

        self.ephem_body = ephem.readdb(self.dde['dde'])

    def status_upgrade(self, time = None, observatory = None):
        if time == None and observatory == None:
            self.ephem_body.compute()
        elif time != None and observatory == None:
            self.ephem_body.compute(time)
        elif time == None and observatory != None:
            self.ephem_body.compute(observatory)
        else:
            raise StopIteration("neither time nor observer is none.")
        return self.ephem_body

class critlist_planet(celestical_object):
    def __init__(self, signal, orbital):
        celestical_object.__init__(self, signal, orbital)
        self.dde = orbital
        self.type = 7

        self.ephem_body = ephem.readdb(self.dde['dde'])

    def status_upgrade(self, time=None, observatory=None):
        if time == None and observatory == None:
            self.ephem_body.compute()
        elif time != None and observatory == None:
            self.ephem_body.compute(time)
        elif time == None and observatory != None:
            self.ephem_body.compute(observatory)
        else:
            raise StopIteration("neither time nor observer is none.")
        return self.ephem_body

class unusual_planet(celestical_object):
    def __init__(self, signal, orbital):
        celestical_object.__init__(self, signal, orbital)
        self.dde = orbital
        self.type = 8

        self.ephem_body = ephem.readdb(self.dde['dde'])

    def status_upgrade(self, time=None, observatory=None):
        if time == None and observatory == None:
            self.ephem_body.compute()
        elif time != None and observatory == None:
            self.ephem_body.compute(time)
        elif time == None and observatory != None:
            self.ephem_body.compute(observatory)
        else:
            raise StopIteration("neither time nor observer is none.")
        return self.ephem_body
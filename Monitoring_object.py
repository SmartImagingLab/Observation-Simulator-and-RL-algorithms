import numpy as np
from celestial_object import *

class monitoring_object:
    def __init__(self,value,decay = 24 * 60 * 60):

        self.value = self.maximum_value = self.initial_value = value  # 目标的初始值即为最大值，即为未知值
        self.minimum_value = 0  # 目标的最小值
        self.decay = decay  # 目标的价值的衰减（上升）速率，decay越低，价值上升的越快
        self.value_sample = 0  # 目标价值衰减（上升）程度

        self.be_observabed = False  # 目标在当前时间是否正在被观测
        self.have_observabed = inf  # 表示已知目标多少个step没有被监测过,未知目标为inf
        self.observabed_time = 0  # 表示目标被看到（监测+探索）过多少次
        self.first_find_time = None
        self.last_find_time = None

        self.error_var = self.cal_error_var(telescope=None)  # 目标的测量误差,随着该目标被望远镜多次观测，产生的概率会逐步降低
        self.pre_ra, self.pre_dec, self.pre_mag = nan, nan, nan

        self.upgrade_time = 0

    def reset(self):
        '''
        按照虚拟环境中的时间更新，更新对象中的某些属性
        :return:
        '''
        self.value = self.initial_value
        self.value_sample = 0

        self.be_observabed = False
        self.have_observabed = inf
        self.observabed_time = 0
        self.first_find_time = None
        self.last_find_time = None

        self.error_var = self.cal_error_var(telescope=None)
        self.upgrade_time = 0

    def cal_error_var(self,telescope):
        '''
        计算因为天体和望远镜原因造成的测量误差
        :param telescope: 观测到该天体的望远镜对象
        :return: 测量误差，type(float)
        '''
        return 0

    def pre_status(self,time):
        '''
        因为测量误差，造成在网天体的测量位置和实际位置出现偏差，
        :param time:时间
        :return:测量位置
        '''
        pass

    def value_upgrade(self):
        '''
        更新目标的科研价值
        :return: value
        '''
        # 已知目标被观测后能上升的最高价值，观测一次为1，此后随着被观测次数的增加，最后价值在逐渐衰减到self.last_value
        # self.maximum_value = self.last_value + (self.initial_value - self.last_value) * exp(
        #     -1. * (self.upgrade_time) / 100)
        # self.upgrade_time += 1
        if self.value != self.minimum_value and self.value < self.maximum_value:
            self.value = exp((self.value_sample-self.decay)/(self.decay)) - 1
            self.value_sample += 1
        elif self.value != self.minimum_value and self.value >= self.maximum_value:
            self.value = self.maximum_value
            self.value_sample += 1
        elif self.value == self.minimum_value and self.value_sample < self.decay:
            self.value_sample += 1
        elif self.value == self.minimum_value and self.value_sample >= self.decay:
            self.value = exp((self.value_sample - self.decay) / (self.decay)) - 1
            self.value_sample += 1

class monitoring_satellite(satellite,monitoring_object):
    def __init__(self,signal, orbital,value,decay):
        satellite.__init__(self, signal, orbital, scale = 1)
        monitoring_object.__init__(self,value,decay)
        self.decay = self.cycle * 2

    def pre_status(self,observatory):
        self.status_upgrade(observatory=observatory)
        az, alt = self.ephem_body.ra,self.ephem_body.dec
        self.pre_az, self.pre_alt,pre_mag= np.random.normal(loc=az, scale=self.error_var,), \
                                                  np.random.normal(loc=alt, scale=self.error_var),self.ephem_body.mag
        return self.pre_az, self.pre_alt, pre_mag

class monitoring_Body(Body,monitoring_object):
    def __init__(self,signal, orbital,value,decay):
        Body.__init__(self,signal, orbital)
        monitoring_object.__init__(self,value,decay)

    def pre_status(self, observatory):
        self.status_upgrade(observatory=observatory)
        az, alt = self.ephem_body.ra, self.ephem_body.dec
        self.pre_az, self.pre_alt, pre_mag = np.random.normal(loc=az, scale=self.error_var, ), \
                                             np.random.normal(loc=alt, scale=self.error_var), self.ephem_body.mag
        return self.pre_az, self.pre_alt, pre_mag


class monitoring_star(star,monitoring_object):
    def __init__(self,signal, orbital,value,decay):
        star.__init__(self,signal, orbital)
        monitoring_object.__init__(self,value,decay)

    def pre_status(self, observatory):
        self.status_upgrade(observatory=observatory)
        az, alt = self.ephem_body.ra, self.ephem_body.dec
        self.pre_az, self.pre_alt, pre_mag = np.random.normal(loc=az, scale=self.error_var, ), \
                                             np.random.normal(loc=alt, scale=self.error_var), self.ephem_body.mag
        return self.pre_az, self.pre_alt, pre_mag


class monitoring_comet(comet,monitoring_object):
    def __init__(self,signal, orbital,value,decay):
        comet.__init__(self,signal, orbital)
        monitoring_object.__init__(self,value,decay)

    def pre_status(self, observatory):
        self.status_upgrade(observatory=observatory)
        az, alt = self.ephem_body.ra, self.ephem_body.dec
        self.pre_az, self.pre_alt, pre_mag = np.random.normal(loc=az, scale=self.error_var, ), \
                                             np.random.normal(loc=alt, scale=self.error_var), self.ephem_body.mag
        return self.pre_az, self.pre_alt, pre_mag


class monitoring_bright_planet(bright_planet,monitoring_object):
    def __init__(self,signal, orbital,value,decay):
        bright_planet.__init__(self,signal, orbital)
        monitoring_object.__init__(self,value,decay)

    def pre_status(self, observatory):
        self.status_upgrade(observatory=observatory)
        az, alt = self.ephem_body.ra, self.ephem_body.dec
        self.pre_az, self.pre_alt, pre_mag = np.random.normal(loc=az, scale=self.error_var, ), \
                                             np.random.normal(loc=alt, scale=self.error_var), self.ephem_body.mag
        return self.pre_az, self.pre_alt, pre_mag


class monitoring_distant_planet(distant_planet,monitoring_object):
    def __init__(self,signal, orbital,value,decay):
        distant_planet.__init__(self,signal, orbital)
        monitoring_object.__init__(self,value,decay)

    def pre_status(self, observatory):
        self.status_upgrade(observatory=observatory)
        az, alt = self.ephem_body.ra, self.ephem_body.dec
        self.pre_az, self.pre_alt, pre_mag = np.random.normal(loc=az, scale=self.error_var, ), \
                                             np.random.normal(loc=alt, scale=self.error_var), self.ephem_body.mag
        return self.pre_az, self.pre_alt, pre_mag


class monitoring_critlist_planet(critlist_planet,monitoring_object):
    def __init__(self,signal, orbital,value,decay):
        critlist_planet.__init__(self,signal, orbital)
        monitoring_object.__init__(self,value,decay)

    def pre_status(self, observatory):
        self.status_upgrade(observatory=observatory)
        az, alt = self.ephem_body.ra, self.ephem_body.dec
        self.pre_az, self.pre_alt, pre_mag = np.random.normal(loc=az, scale=self.error_var, ), \
                                             np.random.normal(loc=alt, scale=self.error_var), self.ephem_body.mag
        return self.pre_az, self.pre_alt, pre_mag


class monitoring_unusual_planet(unusual_planet,monitoring_object):
    def __init__(self,signal, orbital,value,decay):
        unusual_planet.__init__(self,signal, orbital)
        monitoring_object.__init__(self,value,decay)

    def pre_status(self, observatory):
        self.status_upgrade(observatory=observatory)
        az, alt = self.ephem_body.ra, self.ephem_body.dec
        self.pre_az, self.pre_alt, pre_mag = np.random.normal(loc=az, scale=self.error_var, ), \
                                             np.random.normal(loc=alt, scale=self.error_var), self.ephem_body.mag
        return self.pre_az, self.pre_alt, pre_mag

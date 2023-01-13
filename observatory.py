from Basic_knowledge import *
import os.path as op
import ephem
from numpy import pi
import numpy as np
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation
from astropy.coordinates import SkyCoord
from astropy.coordinates import AltAz
from datetime import datetime
import math
import random
from telescope import telescope
from ArScreens import ArScreens
from sky_brightness import sky_brightness
name = 'TIDO'
longitude=93.20
latitude=38.45
elevation=4200
Cloud_dir = op.dirname(op.abspath(__file__)) + "/data/cloud/"
telescope_list = [
                   {'signal': 1, 'caliber': 1, 'field': 3},
                   {'signal': 2, 'caliber': 1, 'field': 3},
                   {'signal': 3, 'caliber': 1, 'field': 3},
                   {'signal': 4, 'caliber': 1, 'field': 3},
                   {'signal': 5, 'caliber': 1, 'field': 3},
                   {'signal': 6, 'caliber': 1, 'field': 3},
                  ]

"记得把时间转换和角度转换写好"

class Observatory:
    def __init__(self, name, Longitude, Latitude, Elevation, telescope_list, Cloud_Cover,
                 is_observation,is_seeing,is_cal_value):

        self.name,self.Longitude,self.Latitude,self.Elevation = name, Longitude, Latitude, Elevation  # 台址信息

        self.Cloud_Cover,self.is_observation,self.is_seeing,self.is_cal_value \
            = Cloud_Cover,is_observation,is_seeing,is_cal_value

        if self.Cloud_Cover is True:
            paramcube = np.array([(0.2, 40, 0, 7600),
                                  (0.2, 5.7, 320, 16000),
                                  ])
            self.cal_cloud = ArScreens(36, 10, 8.4/(36*10), 300., paramcube, 0.99, ranseed=1)
            self.cal_cloud.run(1, verbose=False)
            self.cloud = np.array(np.sum(np.squeeze(self.cal_cloud.screens), 0))[0:360,0:75]
        if self.is_observation: self.observation = np.zeros(360*75).reshape(360,75)
        else: self.observation = None
        if self.is_seeing: self.seeing = np.zeros(360*75).reshape(360,75)
        else: self.seeing = None
        if self.is_cal_value: self.cal_value = np.zeros(360*75).reshape(360,75)
        else: self.cal_value = None

        self.ephem_observatory = ephem.Observer()
        self.ephem_observatory.lat, self.ephem_observatory.lon, self.ephem_observatory.elev = self.Longitude, \
                            self.Latitude, self.Elevation
        self.ephem_moon = ephem.Moon()
        self.ephem_Sun = ephem.Sun()

        self.telescope_list = telescope_list
        # self.telescopes = len(telescope_list) ? 1:0
        self.telescopes = list(map(self.create_telescope,telescope_list))  # 根据望远镜参数生成望远镜阵列对象

    def __repr__(self):
        return "{__class__.__name__}({name!r},{Longitude!r},{Latitude!r},{Elevation!r},{_telescopes!r})"\
            .format(__class__=self.__class__,_telescopes=",".join(map(repr, self.telescope_list)),**self.__dict__)

    def __str__(self):
        return "{__class__.__name__}({name!r},{Longitude!r},{Latitude!r},{Elevation!r})"\
            .format(__class__=self.__class__,**self.__dict__)

    def __eq__(self, other):
        return self.name == other.name and self.Longitude == other.Longitude and self.Latitude == other.Latitude and \
                self.Elevation == other.Elevation

    def reset(self):
        '''
        将对象所有属性重新设置为初始状态
        :return:
        '''
        pass

    def step(self,time,object_type,moni_object):
        '''
        按照虚拟环境中的时间更新，更新对象中的某些属性
        :return:
        '''
        self.ephem_observatory.date = time
        self.ephem_moon.compute(self.ephem_observatory)
        self.ephem_Sun.compute(self.ephem_observatory)
        if self.is_observation or self.is_cal_value or self.is_seeing or self.Cloud_Cover:
            self._get_ob_value(object_type, moni_object)
        for telescope in self.telescopes:
            telescope.step()

    def _get_ob_value(self,object_type,moni_object):
        if not self.is_night():
            if self.Cloud_Cover:self.cloud = np.array(np.sum(np.squeeze(self.cal_cloud.screens), 0))[0:360,0:75]
            if self.is_observation:self.observation = np.zeros(360*75).reshape(360,75)
            if self.is_cal_value:self.cal_value = np.zeros(360*75).reshape(360,75)
            if self.is_seeing:self.seeing = np.zeros(360*75).reshape(360,75)
        else:
            for object_type in object_type:
                for target_index, target in enumerate(moni_object[object_type]):
                    az,alt,mag = target.pre_status(observatory=self.ephem_observatory)
                    AZ,ALT = math.floor(az*180/pi),math.floor(alt*180/pi)
                    if 10 <= ALT < 85:
                        if self.is_observation:
                            # todo mag的选定应该和老师商量一下
                            self.observation[AZ][ALT-10] = min(mag,self.observation[AZ][ALT-10])
                        if self.is_cal_value:
                            self.cal_value[AZ][ALT-10] += target.value
            if self.is_seeing:
                mnp = self.ephem_moon.moon_phase  # 月相
                for i in range(len(self.seeing)):
                    for j in range(len(self.seeing[0])):
                        az, alt = ephem.degrees(str(i)), ephem.degrees(str(j + 10))
                        asg = ephem.separation((self.ephem_moon.ra, self.ephem_moon.dec), (az,alt))
                        self.seeing[i][j] = sky_brightness(180 - mnp * 180, abs(asg), abs(pi / 2 - float(alt)),
                                                           abs(pi / 2 - float(self.ephem_moon.alt)))
            if self.Cloud_Cover:
                self.cal_cloud.run(1, verbose=False)
                self.cloud = np.array(np.sum(np.squeeze(self.cal_cloud.screens), 0))[0:360, 0:75]

    def create_telescope(self,dict):
        '''
        生成一个望远镜对象
        :param dict: 望远镜参数
        :return: 望远镜对象
        '''
        telescope_I = telescope(dict['signal'], dict['caliber'], dict['field'], control = dict['control'])
        return telescope_I


    def solar_altitude(self):
        '''
        计算当前台址的太阳高度角
        :param time: 时间，type(astropy.time.Time)
        :return: 太阳高度角，type(astropy.u.deg)
        '''
        # TIDO = Observer(longitude=self.Longitude * u.deg, latitude=self.Latitude* u.deg,
        #                 elevation=self.Elevation * u.m)
        # solar_altitude = TIDO.altaz(time, target=astropy.coordinates.get_sun(time)).alt
        self.ephem_Sun.compute(self.ephem_observatory)
        return float(self.ephem_Sun.alt)

    def is_night(self):
        '''
        根据当前太阳高度角判断是否为夜晚
        :param time: 时间，type(ephem.Date)
        :return: bool
        '''
        if self.solar_altitude() < -6*pi/180 :
            return True
        else:
            return False

    def is_twilight(self,type = 1):
        '''
        根据当前太阳高度角判断是否处于晨昏线内
        :param time: 时间，type(ephem.Date)
        :param type: 三种晨昏方式
        :return: bool
        '''
        # time = str(ephem.Date(time))
        # time = Time(datetime.strptime(time, '%Y/%m/%d %H:%M:%S').isoformat(), format='isot')
        if type not in [1,2,3]:
            raise StopIteration("is_twilight type must be 1,2 or 3.")
        if -6*type*pi/180 <= self.solar_altitude() <= 0 *pi/180:
            return True
        else:
            return False

    def radec2azalt(self,time, ra, dec, lat, lon, height=0):
        '''输入输出必须全部是角度！！！'''
        if isinstance(ra, ephem.Angle):
            ra = float(math.degrees(ra))
        else:
            raise TypeError("输入的数据必须是ephem.Angle")
        if isinstance(dec, ephem.Angle):
            dec = float(math.degrees(dec))
        else:
            raise TypeError("输入的数据必须是ephem.Angle")
        if isinstance(lat, ephem.Angle):
            lat = float(math.degrees(lat))
        else:
            raise TypeError("输入的数据必须是ephem.Angle")
        if isinstance(lon, ephem.Angle):
            lon = float(math.degrees(lon))
        else:
            raise TypeError("输入的数据必须是ephem.Angle")
        # ra_1 = float(ra)
        # dec_1 = float(dec)
        # 转化将"2022/2/21 00:00:00"转化为2022-02-21T00:00:00.000
        a = datetime.strptime(str(time), '%Y/%m/%d %H:%M:%S').isoformat()
        obstime = Time(a, format='isot')
        location = EarthLocation.from_geodetic(lon, lat)
        local_altaz = AltAz(obstime=obstime, location=location)
        icrs = SkyCoord(ra * u.degree, dec * u.degree, frame='icrs')
        altaz = icrs.transform_to(local_altaz)
        az = (altaz.az * u.deg).value
        alt = (altaz.alt * u.deg).value
        return az, alt

    def azalt2radec(self,time, az, alt, lat, lon, height=0):
        '''输入输出必须全部是角度！！！'''
        if isinstance(az, ephem.Angle):
            az = math.degrees(az)
        else:
            raise TypeError("输入的数据必须是ephem.Angle")
        if isinstance(alt, ephem.Angle):
            alt = math.degrees(alt)
        else:
            raise TypeError("输入的数据必须是ephem.Angle")
        if isinstance(lat, ephem.Angle):
            lat = math.degrees(lat)
        else:
            raise TypeError("输入的数据必须是ephem.Angle")
        if isinstance(lon, ephem.Angle):
            lon = math.degrees(lon)
        else:
            raise TypeError("输入的数据必须是ephem.Angle")
        a = datetime.strptime(str(time), '%Y/%m/%d %H:%M:%S').isoformat()
        obstime = Time(a, format='isot')
        location = EarthLocation(lat=lat * u.deg, lon=lon * u.deg, height=height * u.m)
        crab = SkyCoord(obstime=obstime, location=location, az=az * u.deg, alt=alt * u.deg, frame='altaz')
        coord = crab.transform_to('icrs')
        ra = (coord.ra * u.deg).value
        dec = (coord.dec * u.deg).value
        return ra, dec

    def cal_Azalt(self,celestical_object,date):
        self.ephem_observatory.date = date
        try:
            celestical_object.ephem_body.compute(self.ephem_observatory.date)
            return celestical_object.ephem_body.az,celestical_object.ephem_body.alt
        except:
            print("Something else went wrong,你可能没有输入观测点的date")

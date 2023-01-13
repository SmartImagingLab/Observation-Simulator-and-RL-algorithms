from numpy import pi
from sky_brightness import sky_brightness
import random
from ExposureCalculation import *
import ephem
from control.scan import scan
# from agent import DQNConfig

class telescope:
    def __init__(self, signal, caliber, field,control = "rondom"):
        self.signal, self.caliber, self.field = signal, caliber, field*pi/180  # 望远镜的编号，口径和视场
        self.eff, self.CamDark, self.CamRead = 0.9, 1, 5  # 望远镜和CCD的属性

        self.observabing = False  # 在当前时间是否观测到目标
        self.observation_state = 0  # 观测状态，0：没有观测到；1：观测已知目标；2：观测未知目标
        self.observation_value = 0  # 当前观测所获得的价值
        # self.observation = np.zeros(360*75).reshape(360,75)

        self.az_axe, self.alt_axe = 0, pi / 3  # 望远镜在当前时间的指向，弧度
        self.alt_upper,self.alt_lower = 85*pi/180, 10*pi/180
        self.alt_Orientation = 1  # 望远镜轴移动方向
        self.Axis_speed, self.Axis_acceleration = 2*pi/180, 2*pi/180  # 望远镜的轴速度(度每秒)，轴加速度（度每平方秒）

        self.on_off = 0  # 望远镜的开关机状态，0代表开机，1代表关机
        self.start_up, self.next_s_u = 0, 0  # 望远镜的启动时间

        self.exposing = False  # 望远镜输出曝光状态
        self.moving = False   # 望远镜处于移动状态
        self.ex_time = 1    # 望远镜选择的曝光时间
        self.control_method = control

    def reset(self):
        '''
        将对象所有属性重新设置为初始状态
        :return:
        '''
        self.observabing = False
        self.observation_state = 0
        self.az_axe, self.alt_axe = 0, pi/3
        self.on_off = 0
        self.start_up, self.next_s_u = 0, 0

    def step(self):
        '''
        按照虚拟环境中的时间更新，更新对象中的某些属性:实时更新望远镜的下次启动时间
        :return:
        '''
        self.observation_value = 0
        self.observation_state = 0
        if self.next_s_u > 0 :
            self.next_s_u -= 1
        else:
            self.next_s_u = 0
            self.control()

    def control(self):

        if self.control_method == "random":
            self.az_axe,self.alt_axe = random.uniform(0,pi*250/180),random.uniform(10*pi/180,85*pi/180)
            self.next_s_u += 10 + self.ex_time
        elif self.control_method == "scan":
            change_Degrees = self.change_axe(5)
            self.az_axe,self.alt_axe,self.alt_Orientation = scan(self.az_axe,self.alt_axe,self.alt_upper,
                                                                 self.alt_lower,change_Degrees,self.alt_Orientation)
            self.next_s_u += self.ex_time + 5
        else:
            pass

    def operation_status(self): return not(self.is_exposing or self.is_moving)

    @property
    def is_exposing(self):
        self.exposing = False if self.next_s_u == 0 else True
        return self.exposing

    @property
    def is_moving(self):
        self.moving = False if self.next_s_u == 0 else True
        return self.moving

    def change_axe(self,period):
        '''
        计算指向轴移动度数
        :param period: 运动时间，type(int)
        :param direction: 运动方向，1 or -1
        :return: 改变的度数，type(?)
        '''
        # if abs(direction) != 1 :
        #     raise StopIteration("The movement direction must be 1 or -1. ")
        # else:
        t1 = (self.Axis_speed / self.Axis_acceleration) * 2  # 指向轴启动和稳定所需时间
        Degrees = (period - t1) * self.Axis_speed #  * direction
        return Degrees

    def change_azaxe(self,period):
        '''
        改变az轴指向
        :param ceita: 改变的度数
        :return: 改变后的轴指向
        '''
        ceita = self.change_axe(period)
        if 0 <= self.az_axe+ceita <= 2*pi:
            self.az_axe = self.az_axe+ceita
        else:
            self.az_axe = (self.az_axe+ceita)%(2*pi)

    def change_altaxe(self,period):
        '''
        改变alt轴指向
        :param fai: 改变的度数
        :return: 改变后的轴指向
        '''
        fai = self.change_axe(period)
        if pi*10/180 <= self.alt_axe+fai <= pi*85/180:
            self.alt_axe = self.alt_axe+fai
        elif self.alt_axe+fai < pi*10/180:
            self.alt_axe = pi*10/180
        elif self.alt_axe+fai > pi*85/180:
            self.alt_axe = pi*85/180

    def next_start_up(self,period):
        '''
                计算下次启动时间
                :param period: 运动/曝光时间
                :return: 望远镜下次启动时间
        '''
        if self.next_s_u != 0:
            raise StopIteration("if the telescope is operating,the period input should set None.")
        else:
            self.next_s_u = abs(period)
        self.operation_status()
        return self.next_s_u

    def Visualization_Analysis(self, observatory, celestical_object,step_time = 1,date = None,cal_type=1,location_status = False,
                               Cloud_Cover = False,Exposure = False):
        # 判断天体在不在视野范围内
        def Visualization(celestical_object):
            az,alt = float(celestical_object.ephem_body.az),float(celestical_object.ephem_body.alt)
            if abs(az - self.az_axe) <= self.field and abs(alt - self.alt_axe) <= self.field:
                return True
            else:
                return False

        # 判断观测站位置
        def cal_location_status(observatory,celestical_object,date,cal_type=cal_type,location_status = location_status):
            if location_status == False:
                return True
            else:
                if celestical_object.type == 1 :
                    return observatory.is_twilight()
                else:
                    return observatory.is_night()

        # 判断天体有没有被遮蔽
        def cal_cloud_cover(observatory,celestical_object,Cloud_Cover = Cloud_Cover):
            if Cloud_Cover == False:
                return True
            else:
                ALT,AZ = int(celestical_object.ephem_body.alt *180/pi),int(celestical_object.ephem_body.az *180/pi)
                if observatory.cloud[AZ][ALT-15] > 0 :
                    return False
                else :
                    return True

        # 判断曝光时间
        def cal_Exposure(celestical_object,ex_time,step_time = step_time,Exposure = Exposure):
            if Exposure == False:
                return True
            else:
                observatory.ephem_observatory.date = date
                observatory.ephem_moon.compute(observatory.ephem_observatory)
                celestical_object.status_upgrade(observatory.ephem_observatory)
                moon_phase = observatory.ephem_moon.moon_phase
                m_T_separation = ephem.separation((observatory.ephem_moon.ra,observatory.ephem_moon.dec),
                                                  (celestical_object.ephem_body.ra,celestical_object.ephem_body.dec))
                T_alt = celestical_object.ephem_body.alt
                T_mag = celestical_object.ephem_body.mag
                moon_alt = observatory.ephem_moon.alt
                SkyBack = sky_brightness(180 - moon_phase * 180, abs(m_T_separation), abs(pi / 2 - float(T_alt)),
                               abs(pi / 2 - float(moon_alt)), k=0.0084, B_zen=79.0)
                TelEff, TelAper, CamDark, CamRead = self.eff, self.caliber, self.CamDark, self.CamRead
                return observable(T_mag, SkyBack, TelEff, TelAper, CamDark, CamRead, Exposuretime=ex_time*step_time,
                                  PixelScale=1,Seeing=2, Wavelength=0.64, FullwellDepth=None, SnrCriterion=5)[0]

        if cal_location_status(observatory,celestical_object,date) is False:
            return False
        else:
            if Visualization(celestical_object) is False:
                return False
            else:
                if cal_cloud_cover(observatory,celestical_object) is False:
                    return False
                else:
                    return cal_Exposure(celestical_object,self.ex_time,step_time = step_time)

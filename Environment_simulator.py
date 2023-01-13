import ephem
from Monitoring_Center import Monitoring_Center
from celestial_object import *
from read_data import *
import configparser
import sys,os


curr_path = os.path.dirname(os.path.abspath(__file__))  # 当前文件所在绝对路径
parent_path = os.path.dirname(curr_path)  # 父路径
sys.path.append(parent_path)  # 添加父路径到系统路径sys.path

class Environment_simulator:
    def __init__(self, ini_path:str):
        env_config = configparser.ConfigParser()
        env_config.read(ini_path, encoding='utf-8')

        self.start_time = ephem.Date(eval(env_config.get('simulator_time', 'start_time')))
        self.end_time   = ephem.Date(eval(env_config.get('simulator_time', 'end_time')))
        self.step_time  = ephem.Date(eval(env_config.get('simulator_time', 'step_time')))
        self.time       = self.start_time

        self.trackdata = {
            'satellite'      : curr_path + eval(env_config.get('trackdata', 'satellite'))      ,
            'star'           : curr_path + eval(env_config.get('trackdata', 'star'))           ,
            'comet'          : curr_path + eval(env_config.get('trackdata', 'comet'))          ,
            'bright_planet'  : curr_path + eval(env_config.get('trackdata', 'bright_planet'))  ,
            'distant_planet' : curr_path + eval(env_config.get('trackdata', 'distant_planet'))  ,
            'critlist_planet': curr_path + eval(env_config.get('trackdata', 'critlist_planet')) ,
            'unusual_planet' : curr_path + eval(env_config.get('trackdata', 'unusual_planet'))  ,
            }
        self.object_numbers = {
            'satellite'      : eval(env_config.get('object_numbers', 'satellite'))     ,
            'star'           : eval(env_config.get('object_numbers', 'star'))          ,
            'comet'          : eval(env_config.get('object_numbers', 'comet'))         ,
            'bright_planet'  : eval(env_config.get('object_numbers', 'bright_planet')) ,
            'distant_planet' : eval(env_config.get('object_numbers', 'distant_planet')) ,
            'critlist_planet': eval(env_config.get('object_numbers', 'critlist_planet')),
            'unusual_planet' : eval(env_config.get('object_numbers', 'unusual_planet')) ,
        }
        self.select          = eval(env_config.get('object_numbers', 'select'))

        self.Display         = eval(env_config.get('Setting', 'Display'))
        self.Record          = eval(env_config.get('Setting', 'Record'))
        self.Exposure        = eval(env_config.get('Setting', 'Exposure'))
        self.location_status = eval(env_config.get('Setting', 'location_status'))
        self.satellite_error = eval(env_config.get('Setting', 'satellite_error'))
        self.error_range     = eval(env_config.get('Setting', 'error_range'))


        self.Monitoring_Center = Monitoring_Center(ini_path)   # 创建监测中心对象

        self.all_object = {'satellite': [], 'star': [], 'comet': [], 'bright_planet': [],
                        'distant_planet': [], 'critlist_planet': [], 'unusual_planet': [], }
        self.object_type = ['satellite', 'star', 'comet', 'bright_planet',
                            'distant_planet', 'critlist_planet', 'unusual_planet']

        self.create_Enviroment_simulator()  # 完成环境的创建

    def reset(self) -> None:
        '''
        将对象所有属性重新设置为初始状态
        :return:
        '''
        self.time = self.start_time
        self.Monitoring_Center.reset()

    def step(self,update = True) -> None:
        '''
        按照模拟器中的时间更新,更新对象中的某些属性,在一个时间步内的对象的属性更新和互相交互
        值得注意的是，我们需要做一个“真更新”和“假更新”来辅助完成仿真并加快时间。
        '''
        if self.Display:
            print("%s的环境正在被模拟..."%(str(ephem.Date(self.time))))
        if update:
            self.Monitoring_Center.step(self.time)
            self.observation_process()
        if self.satellite_error:
            # todo 仍然有很多问题
            for satellite in self.all_object["satellite"]:
                satellite.orbital_upgrade(self.time,float(self.step_time))
        self.time += self.step_time

    def create_Enviroment_simulator(self) -> None:
        '''
        通过参数文件中各目标的轨道文件地址和目标数创建目标天体
        '''
        for object_type in self.object_type:
            trackdata = self.trackdata[object_type]
            numbers = self.object_numbers[object_type]
            if object_type == 'satellite':
                all_track = read_tle(trackdata)
                if self.select == "random":
                    select_track = random.sample(all_track, numbers)
                elif self.select == "preorder":
                    select_track = all_track[:numbers]
                else:
                    raise TypeError
                signal = 0
                for track_index,track in enumerate(select_track):
                    signal += 1
                    if track_index < numbers*self.error_range/100:
                        object_i = satellite(signal, track,unormal_epoch=[self.start_time,self.end_time])
                    else:
                        object_i = satellite(signal, track)
                    self.all_object[object_type].append(object_i)
            elif object_type == 'star':
                all_track = read_fix(trackdata)
                if self.select == "random":
                    select_track = random.sample(all_track, numbers)
                elif self.select == "preorder":
                    select_track = all_track[:numbers]
                else:
                    raise TypeError
                signal = 0
                for track in select_track:
                    signal += 1
                    object_i = star(signal, track)
                    self.all_object[object_type].append(object_i)
            elif object_type == 'comet':
                all_track = read_ddb(trackdata)
                if self.select == "random":
                    select_track = random.sample(all_track, numbers)
                elif self.select == "preorder":
                    select_track = all_track[:numbers]
                else:
                    raise TypeError
                signal = 0
                for track in select_track:
                    signal += 1
                    object_i = comet(signal, track)
                    self.all_object[object_type].append(object_i)
            elif object_type == 'bright_planet':
                all_track = read_minorplanet(trackdata)
                if self.select == "random":
                    select_track = random.sample(all_track, numbers)
                elif self.select == "preorder":
                    select_track = all_track[:numbers]
                else:
                    raise TypeError
                signal = 0
                for track in select_track:
                    signal += 1
                    object_i = bright_planet(signal, track)
                    self.all_object[object_type].append(object_i)
            elif object_type == 'distant_planet':
                all_track = read_minorplanet(trackdata)
                if self.select == "random":
                    select_track = random.sample(all_track, numbers)
                elif self.select == "preorder":
                    select_track = all_track[:numbers]
                else:
                    raise TypeError
                signal = 0
                for track in select_track:
                    signal += 1
                    object_i = distant_planet(signal, track)
                    self.all_object[object_type].append(object_i)
            elif object_type == 'critlist_planet':
                all_track = read_minorplanet(trackdata)
                if self.select == "random":
                    select_track = random.sample(all_track, numbers)
                elif self.select == "preorder":
                    select_track = all_track[:numbers]
                else:
                    raise TypeError
                signal = 0
                for track in select_track:
                    signal += 1
                    object_i = critlist_planet(signal, track)
                    self.all_object[object_type].append(object_i)
            elif object_type == 'critlist_planet':
                all_track = read_minorplanet(trackdata)
                if self.select == "random":
                    select_track = random.sample(all_track, numbers)
                elif self.select == "preorder":
                    select_track = all_track[:numbers]
                else:
                    raise TypeError
                signal = 0
                for track in select_track:
                    signal += 1
                    object_i = unusual_planet(signal, track)
                    self.all_object[object_type].append(object_i)

    def observation_process(self) -> None:
        """
        模拟器的观测交互过程
        """
        for observatory in self.Monitoring_Center.Observatorys:
            if observatory.solar_altitude() < 0 :
                for tele_index,telescope in enumerate(observatory.telescopes):
                    if telescope.next_s_u != 0:
                        continue
                    else:
                        self.Monitoring_Center.observationTimes += 1
                        for object_type in self.object_type:
                            for target_index, target in enumerate(self.all_object[object_type]):
                                target.status_upgrade(observatory = observatory.ephem_observatory)
                                if telescope.Visualization_Analysis(observatory,target,int(self.step_time*60*60*24),
                                                                    date=self.time,
                                                                    location_status = self.location_status,
                                                                    Cloud_Cover = observatory.Cloud_Cover,
                                                                    Exposure = self.Exposure):
                                    if target.signal in self.Monitoring_Center.know_object[object_type]:
                                        telescope.observation_state = 1 if telescope.observation_state != 2 else 2
                                    else:
                                        self.Monitoring_Center.Catalog(target)
                                        telescope.observation_state = 2
                                        self.Monitoring_Center.moni_object[object_type][-1].first_find_time = None
                                    index = self.Monitoring_Center.know_object[object_type].index(target.signal)
                                    telescope.observabing = True
                                    telescope.observation_value += self.Monitoring_Center.moni_object[object_type][index].value
                                    self.Monitoring_Center.moni_object[object_type][index].value = 0
                                    self.Monitoring_Center.moni_object[object_type][index].value_sample = 0
                                    self.Monitoring_Center.moni_object[object_type][index].cal_error_var(telescope)
                                    self.Monitoring_Center.moni_object[object_type][index].last_find_time = None
                                    if self.Display is True:
                                        print("%s观测台的第%d个望远镜观测到%s%d(类型编号)的目标"%(observatory.name,telescope.signal,
                                                                             object_type,target.signal))
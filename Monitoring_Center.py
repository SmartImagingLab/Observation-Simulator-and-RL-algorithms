from Monitoring_object import *
from observatory import Observatory
from telescope import *
from Monitoring_object import *
import configparser
import os

curr_path = os.path.dirname(os.path.abspath(__file__))  # 当前路径

class Monitoring_Center:
    def __init__(self, ini_path):
        env_config = configparser.ConfigParser()
        env_config.read(ini_path, encoding='utf-8')

        self.object_value = {
            'satellite'      : eval(env_config.get('object_value', 'satellite'))      ,
            'star'           : eval(env_config.get('object_value', 'star'))           ,
            'comet'          : eval(env_config.get('object_value', 'comet'))          ,
            'bright_planet'  : eval(env_config.get('object_value', 'bright_planet'))  ,
            'distant_planet' : eval(env_config.get('object_value', 'distant_planet')) ,
            'critlist_planet': eval(env_config.get('object_value', 'critlist_planet')),
            'unusual_planet' : eval(env_config.get('object_value', 'unusual_planet')) ,
        }


        self.know_object = {'satellite': [], 'body': [], 'star': [], 'comet': [], 'bright_planet': [],
                            'distant_planet': [], 'critlist_planet': [], 'unusual_planet': [], }
        self.moni_object = {'satellite': [], 'body': [], 'star': [], 'comet': [], 'bright_planet': [],
                            'distant_planet': [], 'critlist_planet': [], 'unusual_planet': [], }
        self.Observatorys = self.read_Observatorys(env_config)
        self.GrossKnowTarget, self.GrossMoniTarget = 0, 0
        self.observationTimes = 0

    def reset(self):
        self.know_object = {'satellite': [], 'body': [], 'star': [], 'comet': [], 'bright_planet': [],
                            'distant_planet': [], 'critlist_planet': [], 'unusual_planet': [], }
        self.moni_object = {'satellite': [], 'body': [], 'star': [], 'comet': [], 'bright_planet': [],
                            'distant_planet': [], 'critlist_planet': [], 'unusual_planet': [], }
        for observatory in self.Observatorys:
            observatory.reset()
        self.observationTimes,self.GrossKnowTarget, self.GrossMoniTarget = 0,0,0


    def step(self,time):
        object_type = ['satellite','star','comet','bright_planet','distant_planet','critlist_planet','unusual_planet']
        for Observatory in self.Observatorys:
            Observatory.step(time,object_type,self.moni_object)
        self.GrossKnowTarget, self.GrossMoniTarget = self.calGrossTarget()

    def calGrossTarget(self):
        GrossKnowTarget,GrossMoniTarget = 0,0
        for knowObj in self.know_object:
            GrossKnowTarget += len(self.know_object[knowObj])
        for moniObj in self.know_object:
            GrossMoniTarget += len(self.know_object[moniObj])
        return GrossKnowTarget,GrossMoniTarget

    def read_Observatorys(self,env_config):
        ob = configparser.ConfigParser()
        ob_config_path = eval(env_config.get('Observatory_config', 'path'))
        ob.read(ob_config_path, encoding='utf-8')

        Observatorys = []
        for observatory in env_config.options("Observatorys"):
            section = eval(env_config.get("Observatorys", observatory))
            telescopes, signal = [], 0
            for tele in eval(ob.get(section, 'telescope')):
                signal += 1
                telescopes.append(
                    {'signal': signal,
                     'caliber': eval(ob.get(tele, 'caliber')),
                     'field': eval(ob.get(tele, 'field')),
                     'control': eval(ob.get(tele, 'control'))}
                )
            Observatorys.append(
                Observatory(eval(ob.get(section, 'name')), eval(ob.get(section, 'longitude')),
                            eval(ob.get(section, 'latitude')),eval(ob.get(section, 'elevation')),
                            telescopes, eval(ob.get(section, 'Cloud_cover')),eval(ob.get(section, 'is_seeing')),
                            eval(ob.get(section, 'is_observation')),eval(ob.get(section, 'is_cal_value'))
            ))
        return Observatorys

    def create_Observatorys(self,observatory):
        Observatory_i = observatory(observatory["name"], observatory["Longitude"], observatory["Latitude"],
                                    observatory["Elevation"], observatory["telescope_list"], observatory["Cloud_dir"]
                                    )
        return Observatory_i

    def Catalog(self,celestial_object):
        signal = celestial_object.signal
        orbital = celestial_object.orbital
        object_type = celestial_object.type
        if object_type == 1:
            self.know_object["satellite"].append(signal)
            self.moni_object["satellite"].append(monitoring_satellite(signal,orbital,4,decay = 24*60*60))
        elif object_type == 2:
            self.know_object["body"].append(signal)
            self.moni_object["body"].append(monitoring_Body(signal,orbital,4,decay = 24*60*60))
        elif object_type == 3:
            self.know_object["star"].append(signal)
            self.moni_object["star"].append(monitoring_star(signal,orbital,4,decay = 24*60*60))
        elif object_type == 4:
            self.know_object["comet"].append(signal)
            self.moni_object["comet"].append(monitoring_comet(signal,orbital,4,decay = 24*60*60))
        elif object_type == 5:
            self.know_object["bright_planet"].append(signal)
            self.moni_object["bright_planet"].append(monitoring_bright_planet(signal,orbital,4,decay = 24*60*60))
        elif object_type == 6:
            self.know_object["distant_planet"].append(signal)
            self.moni_object["distant_planet"].append(monitoring_distant_planet(signal,orbital,4,decay = 24*60*60))
        elif object_type == 7:
            self.know_object["critlist_planet"].append(signal)
            self.moni_object["critlist_planet"].append(monitoring_critlist_planet(signal,orbital,4,decay = 24*60*60))
        elif object_type == 8:
            self.know_object["unusual_planet"].append(signal)
            self.moni_object["unusual_planet"].append(monitoring_unusual_planet(signal,orbital,4,decay = 24*60*60))




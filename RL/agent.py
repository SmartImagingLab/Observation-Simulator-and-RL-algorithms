from DQN import DQN
import os,sys
import datetime
from numpy import inf
from gym import spaces
import configparser
import numpy as np
import random
from Environment_simulator import Environment_simulator
import ephem

random.seed(5)
curr_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")  # 获取当前时间
curr_path = os.path.dirname(os.path.abspath(__file__))  # 当前文件所在绝对路径
parent_path = os.path.dirname(curr_path)  # 父路径
sys.path.append(parent_path)  # 添加父路径到系统路径sys.path

class DQNConfig:
    def __init__(self,ini_path):
        config = configparser.ConfigParser()
        config.read(ini_path, encoding='utf-8')
        self.gamma           = eval(config.get('DQN', 'gamma'))  # 强化学习中的折扣因子
        self.epsilon_start   = eval(config.get('DQN', 'epsilon_start'))  # e-greedy策略中初始epsilon
        self.epsilon_end     = eval(config.get('DQN', 'epsilon_end'))  # e-greedy策略中的终止epsilon
        self.epsilon_decay   = eval(config.get('DQN', 'epsilon_decay'))  # e-greedy策略中epsilon的衰减率
        self.lr              = eval(config.get('DQN', 'lr'))  # 学习率
        self.memory_capacity = eval(config.get('DQN', 'memory_capacity'))  # 经验回放的容量
        self.batch_size      = eval(config.get('DQN', 'batch_size'))  # mini-batch SGD中的批量大小 #1600
        self.target_update   = eval(config.get('DQN', 'target_update'))  # 目标网络的更新频率
        self.hidden_dim      = eval(config.get('DQN', 'hidden_dim'))  # hidden size of net

class actor:
    def __init__(self,index):
        self.index = index  # 用index指定actor属于哪一个

    def reset(self,ob,tele):
        self.start_up = 0  # 距离下一次能够采样的时间点
        self.a = 0  # 动作
        self.a_type = 0  # 望远镜做哪一类动作，0：曝光，1：az移动，2：alt移动
        self.a_period = 0  # 望远镜本次动作的动作时长
        self.r = 0  # 奖励
        self.s = []  # 当前状态
        self._s = []  # 上一个状态
        self.done = False
        self.s = self.get_s(ob,tele)


    def choose_action(self,strategy):
        self.a = strategy.choose_action(self.s)
        return self.a

    def predict(self,strategy):
        self.a = strategy.predict(self.s)
        return self.a

    def memory_push(self,strategy):
        strategy.memory.push(self.s,self.a,self.r,self._s,self.done)
        return strategy

    def have_done(self,ENV):
        if len(ENV.Monitoring_Center.know_object['satellite']) > ENV.object_numbers["satellite"]*0.8:return True
        else:return False

    def cal_r(self, ENV, tele):
        r = 0
        if self.have_done(ENV):
            r += 1000
        else:
            r += tele.observation_value
        return r

    def get_s(self,OB,tele):
        state = []
        _shape = np.shape(np.array(OB.observation))
        state.append(OB.observation)
        state.append(OB.cloud)
        state.append(OB.seeing)
        state.append(OB.cal_value)
        state.append(np.ones(_shape)*tele.az_axe)
        state.append(np.ones(_shape) * tele.alt_axe)
        return np.array(state)

class Agent():
    # todo 要写好state_dim, action_dim
    def __init__(self,strategy_cfg,state_dim, action_dim,n_actor=1):
        self.n_actor = n_actor
        self.strategy = DQN(DQNConfig(strategy_cfg),state_dim, action_dim)
        self.observation_space, self.action_space = self._space(state_dim, action_dim)

        self.actors = []
        for i in range(self.n_actor):
            action_i = actor(i)
            self.actors.append(action_i)

        self.R = 0  # 智能体的总体奖励

    def _space(self,state_dim,action_dim):
        return spaces.Box(low=0,high=inf, shape=(state_dim,),dtype=np.float32),\
               spaces.Box(low=0,high=inf, shape=(action_dim,),dtype=np.float32)

    def analysis_action(self,action):
        if action < 10:
            return 0,action
        elif 10 <= action < 20:
            return 1,-(action-10)
        elif 20 <= action < 30:
            return 1,action-20
        elif 30 <= action < 40:
            return 2,-(action-30)
        elif 40 <= action < 50:
            return 2,action-40
        else:
            raise TypeError

    def reset(self,Env):
        Env.reset()
        for index,actor in enumerate(self.actors):
            # todo 这里的问题需要讲actor抽象出来，以后在做
            actor.reset(Env.Monitoring_Center.Observatorys[0],Env.Monitoring_Center.Observatorys[0].telescopes[index])
        return Env,self

    def have_done(self,ENV):
        if len(ENV.Monitoring_Center.know_object['satellite']) > ENV.object_numbers["satellite"]*0.8:return True
        else: return False

    def getGrossReward(self):
        grossReward = 0
        for actor in self.actors:
            grossReward += actor.r
        return grossReward

    def step(self,ENV,stepType = "train"):
        entities = ENV.Monitoring_Center.Observatorys[0].telescopes
        for index in range(len(self.actors)):
            if entities[index].next_s_u == 0:
                if stepType == "train":
                    action = self.actors[index].choose_action(self.strategy)
                else:
                    action = self.actors[index].predict(self.strategy)
                self.a_type, self.a_period = self.analysis_action(action)
                # print("%s时，第%s个观测台选择的动作为%s,即动作类型是%s,时间长度为%s,望远镜的冷却启动时间为%s。"% (ephem.Date(ENV.time), index, action, self.a_type, self.a_period, self.actors[index].start_up))
                self.actors[index].start_up = entities[index].next_start_up(self.a_period)
                # print("                     望远镜的冷却启动时间为%s。"% (self.actors[index].start_up))
                if self.a_type == 0:
                    entities[index].ex_time = self.a_period
                elif self.a_type == 1 :
                    entities[index].change_azaxe(self.a_period)
                elif self.a_type ==2:
                    entities[index].change_azaxe(self.a_period)
        ENV.step()
        entities = ENV.Monitoring_Center.Observatorys[0].telescopes
        for index in range(len(self.actors)):
            if entities[index].start_up == 0:
                self.actors[index]._s = self.actors[index].s
                self.actors[index].s = self.actors[index].get_s(ENV.Monitoring_Center.Observatorys[0],entities[index])
                self.actors[index].r = self.actors[index].cal_r(ENV,entities[index])
                if stepType == "train":
                    self.actors[index].memory_push(self.strategy)
        if stepType == "train":
            self.strategy.update()

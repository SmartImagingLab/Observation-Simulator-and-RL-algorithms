import sys, os
from agent import Agent
from Environment_simulator import Environment_simulator
import random
import datetime
import configparser
from utils import save_results, make_dir
from plot import plot_res
import torch
import ephem


random.seed(5)
curr_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")  # 获取当前时间
curr_path = os.path.dirname(os.path.abspath(__file__))  # 当前文件所在绝对路径
parent_path = os.path.dirname(curr_path)  # 父路径
sys.path.append(parent_path)  # 添加父路径到系统路径sys.path

class RLconfig:
    def __init__(self, ini_path):
        config = configparser.ConfigParser()
        config.read(ini_path, encoding='utf-8')
        self.block       = eval(config.get('RL', 'block'))
        self.algo        = eval(config.get('RL', 'algo'))
        self.env         = eval(config.get('RL', 'env'))
        self.result_path = eval(config.get('RL', 'result_path'))
        self.model_path  = eval(config.get('RL', 'model_path'))
        self.train_eps   = eval(config.get('RL', 'train_eps'))
        self.eval_eps    = eval(config.get('RL', 'eval_eps'))
        self.device      = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def createAgent():
    return Agent(curr_path + "/config/DQN.ini", 500, 20, 6)

def createEnv():
    return Environment_simulator(ini_path=curr_path + "/config/env.ini")

def createCfg():
    return RLconfig(curr_path + "/config/DQN.ini")

def train(cfg,Env,agent):
    print('training!')
    print(f'env：{cfg.env}, algo：{cfg.algo}, Device：{cfg.device}')
    rewards, ma_rewards, lens, mlens, = [], [], [], []
    for i_ep in range(cfg.train_eps):
        Env,agent = agent.reset(Env)
        ep_reward, step = 0, 0
        while True:
            if agent.have_done(Env) or step >= 60:break
            agent.step(Env,stepType="train")  # 动作选择
            ep_reward += agent.getGrossReward()
            step += 1
        if (i_ep + 1) % agent.strategy.target_update == 0:
            agent.strategy.target_net.load_state_dict(agent.strategy.policy_net.state_dict())
        if (i_ep + 1) % 1 == 0:
            print('ep：%d/%d, reward：%.5f，epsilon:%.5f,object(find/moni)：%d/%d，star(find/moni)：%d/%d,observationtime:%d'
                  % (i_ep + 1, cfg.train_eps, ep_reward,agent.strategy.epsilon(agent.strategy.frame_idx),
                  Env.Monitoring_Center.GrossKnowTarget,Env.Monitoring_Center.GrossMoniTarget,
                  len(Env.Monitoring_Center.moni_object["star"]),len(Env.Monitoring_Center.know_object["star"]),
                     Env.Monitoring_Center.observationTimes))
        rewards.append(ep_reward)
        lens.append(len(Env.Monitoring_Center.know_object["star"]))
        mlens.append(len(Env.Monitoring_Center.moni_object["star"]))

        if ma_rewards:
            ma_rewards.append(0.9 * ma_rewards[-1] + 0.1 * ep_reward)
        else:
            ma_rewards.append(ep_reward)
    return rewards, ma_rewards,lens,mlens

if __name__ == "__main__":
    cfg, env, agent = createCfg(),createEnv(),createAgent()
    #　训练
    rewards, ma_rewards, lens, mlens = train(cfg, env, agent)
    make_dir(cfg.result_path, cfg.model_path)
    agent.strategy.save(path=cfg.model_path)
    save_results(rewards,ma_rewards,'rewards',tag='train', path=cfg.result_path)
    save_results(lens, mlens, 'lens', tag='train', path=cfg.result_path)
    plot_res(rewards,ma_rewards,'rewards', tag="train", algo=cfg.algo, path=cfg.result_path)
    plot_res(lens, mlens, 'lens', tag="train", algo=cfg.algo, path=cfg.result_path)
from agent import DQNConfig,agent
from Environment_simulator import Environment_simulator
import os,sys,time

ini_path = "/config/DQN.ini "

def equip_agent(MC,DQN):
    for observatory in MC.Observatorys:
        for telescope in observatory.telescope_array:
            telescope.agent = agent(500,20,DQN)

def get_s(tele):
    tele.agent.s = tele.observation
def get_r(tele):
    tele.agent.r = tele.observation_value


curr_path = os.path.dirname(os.path.abspath(__file__))  # 当前文件所在绝对路径
parent_path = os.path.dirname(curr_path)  # 父路径
sys.path.append(parent_path)  # 添加父路径到系统路径sys.path
def run_simulator():
    start = time.time()
    ini_path = "/config/env.ini "
    Env = Environment_simulator(ini_path=curr_path + ini_path)
    equip_agent(Env.Monitoring_Center,DQNConfig(curr_path + "/config/DQN.ini "))
    for observatory in Env.Monitoring_Center.Observatorys:
        for telescope in observatory.telescope_array:
            telescope.agent.r = telescope.observation
            print(telescope.agent.s)
            print(telescope.agent.have_done())

if __name__ == "__main__":
    run_simulator()
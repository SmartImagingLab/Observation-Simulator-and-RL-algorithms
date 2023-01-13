import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
from matplotlib.font_manager import FontProperties
# matplotlib.rc("font",family='YouYuan')
# matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 微软雅黑
# matplotlib.rcParams['font.serif'] = ['Microsoft YaHei']
# matplotlib.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题,或者转换负号为字符串

def chinese_font():
    return FontProperties(fname='C:\Windows\Fonts\simsun.ttc',size=15)  # 系统字体路径

def plot_res(rewards,ma_rewards,res,tag="train",env='Space target monitoring system',algo = "DQN",save=True,path='./'):
    sns.set()
    plt.figure()
    plt.title("average learning curve of {} for {}".format(algo, env))
    plt.xlabel('epsiodes')
    plt.plot(rewards, label='{}'.format(res))
    plt.plot(ma_rewards, label='ma_{}'.format(res))
    plt.legend()
    if save:
        plt.savefig(path + "{}_{}_curve".format(res,tag))
    # plt.show()

def plot_rewards(rewards,ma_rewards,tag="train",env='Space target monitoring system',algo = "DQN",save=True,path='./'):
    sns.set()
    plt.figure()
    plt.title("average learning curve of {} for {}".format(algo,env))
    plt.xlabel('epsiodes')
    plt.plot(rewards,label='rewards')
    plt.plot(ma_rewards,label='ma rewards')
    plt.legend()
    if save:
        plt.savefig(path+"{}_rewards_curve".format(tag))
    # plt.show()

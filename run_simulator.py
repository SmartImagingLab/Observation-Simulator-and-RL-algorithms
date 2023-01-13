from Environment_simulator import Environment_simulator
import os,sys,random
import time
from numpy import pi
import psutil
import os
import objgraph



curr_path = os.path.dirname(os.path.abspath(__file__))  # 当前文件所在绝对路径
parent_path = os.path.dirname(curr_path)  # 父路径
sys.path.append(parent_path)  # 添加父路径到系统路径sys.path

def run_simulator():
    start = time.time()
    ini_path = "/config/env.ini "
    Env = Environment_simulator(ini_path=curr_path + ini_path)
    Env.Display = True

    for i in range(24*60):
        Env.step()

    print("satellite", len(Env.Monitoring_Center.know_object["satellite"]), Env.Monitoring_Center.know_object["satellite"])
    print("star", len(Env.Monitoring_Center.know_object["star"]), Env.Monitoring_Center.know_object["star"])
    print("comet", len(Env.Monitoring_Center.know_object["comet"]), Env.Monitoring_Center.know_object["comet"])
    print("bright_planet", len(Env.Monitoring_Center.know_object["bright_planet"]), Env.Monitoring_Center.know_object["bright_planet"])
    print("distant_planet", len(Env.Monitoring_Center.know_object["distant_planet"]), Env.Monitoring_Center.know_object["distant_planet"])
    print("critlist_planet", len(Env.Monitoring_Center.know_object["critlist_planet"]), Env.Monitoring_Center.know_object["critlist_planet"])
    print("unusual_planet", len(Env.Monitoring_Center.know_object["unusual_planet"]), Env.Monitoring_Center.know_object["unusual_planet"])

    print("当前程序用时：%s" %(time.time() - start))
    print(u'当前进程的内存使用：%.4f GB' % (psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024 / 1024))


if __name__ == "__main__":
    run_simulator()

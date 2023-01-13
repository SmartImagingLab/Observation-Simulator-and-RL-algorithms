import os
import numpy as np
from pathlib import Path

def save_results(rewards,ma_rewards,res,tag='train',path='./results'):
    '''save rewards and ma_rewards
    '''
    np.save(path+'{}_{}.npy'.format(res,tag), rewards)
    np.save(path+'{}_ma_{}.npy'.format(res,tag), ma_rewards)
    print('结果保存完毕！')

def make_dir(*paths):
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)
def del_empty_dir(*paths):
    '''del_empty_dir delete empty folders unders "paths"
    '''
    for path in paths:
        dirs = os.listdir(path)
        for dir in dirs:
            if not os.listdir(os.path.join(path, dir)):
                os.removedirs(os.path.join(path, dir))
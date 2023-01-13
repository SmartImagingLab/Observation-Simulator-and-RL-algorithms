# 导入需要的包
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from itertools import chain

# 以下三行是为了让matplot能显示中文
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['FangSong']
mpl.rcParams['axes.unicode_minus'] = False

# 以下是读取参数文件数据
import configparser
import os
curr_path = os.path.dirname(os.path.abspath(__file__))  # 当前文件所在绝对路径
parent_path = os.path.dirname(curr_path)  # 父路径

def draw_point(m, x, y, name,color="red"):
    # 这里的经纬度是：(经度, 纬度)
    x, y = m(x, y)
    plt.plot(x, y, 'ok', markersize=5)
    plt.text(x, y, name, fontsize=12, color=color)
    plt.title("望远镜台址位置信息",fontdict={'weight':'normal','size': 20})

def draw_map(m, scale=0.2):
    # 绘制带阴影的浮雕图像
    m.shadedrelief(scale=scale)

    # 根据经纬度切割，每13度一条线
    lats = m.drawparallels(np.linspace(-90, 90, 13))
    lons = m.drawmeridians(np.linspace(-180, 180, 13))

    # 集合所有线条
    lat_lines = chain(*(tup[1][0] for tup in lats.items()))
    lon_lines = chain(*(tup[1][0] for tup in lons.items()))
    all_lines = chain(lat_lines, lon_lines)

    # 循环画线
    for line in all_lines:
        line.set(linestyle='-', alpha=0.3, color='w')

def draw(locations):
    # 　绘制地图
    fig = plt.figure(figsize=(8, 6), edgecolor='w')
    m = Basemap(projection='cyl', resolution=None,
                llcrnrlat=-90, urcrnrlat=90,
                llcrnrlon=-180, urcrnrlon=180, )
    draw_map(m)
    for loc in locations:
        print(locations[loc])
        draw_point(m, locations[loc][1], locations[loc][0], loc)
    plt.show()

if __name__ == '__main__':

    # 读取观测站的位置
    env = configparser.ConfigParser()
    env.read(parent_path + '\config\env.ini', encoding='utf-8')
    ob = configparser.ConfigParser()
    ob.read(parent_path+'\config\Observatorys.ini', encoding='utf-8')

    # 将观测站的位置写入
    locations = {}
    for observatory in env.options("Observatorys"):
        section = eval(env.get("Observatorys", observatory))
        locations.update({eval(ob.get(section, 'name')):(eval(ob.get(section, 'latitude')),
                            eval(ob.get(section, 'longitude')))})

    #　绘制地图
    draw(locations)
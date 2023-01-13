from libtiff import TIFF
import matplotlib.pyplot as plt
import numpy as np


# 读取夜间灯光数据
tif = TIFF.open('F182013.v4c.avg_lights_x_pct\F182013.v4c.avg_lights_x_pct.tif', mode='r')
img = tif.read_image()
height = img.shape[0]
width = img.shape[1]
# plt.imshow(img)
# plt.show()
# 提取包含中国东部范围的夜间灯光数据画图
# 夜灯数据覆盖范围为-65~75oN,-180-180oN，分辨率是30’
lons = 100
lone = 137
lats = -15
late = 15
lons_grid = int((lons+180) / (30.0 / 3600))
lone_grid = int((lone+180) / (30.0 / 3600))
lats_grid = int((70 + lats) / (30.0 / 3600))
late_grid = int((70 + late) / (30.0 / 3600))
print(lats_grid,late_grid, lons_grid,lone_grid)
print(lats_grid*(30.0 / 3600),late_grid*(30.0 / 3600), lons_grid*(30.0 / 3600),lone_grid*(30.0 / 3600))
img2 = img[lats_grid:late_grid, lons_grid:lone_grid]
plt.imshow(img2)
plt.show()
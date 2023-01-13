import numpy as np
import os
a = np.load(r'')
c = a
for i in range(a.shape[0]):
    for j in range(a.shape[0]):
        center = np.array([int(a.shape[0]/2), int(a.shape[1]/2)])
        t = np.array([i, j])
        if (sum((t-center)**2))**(1/2) < int((a.shape[0]-2)/2):
            c[i, j] = a[i, j]
        else:
            c[i, j] = 0



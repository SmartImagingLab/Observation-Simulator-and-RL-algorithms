import numpy as np
import numpy.random as ra
import scipy.fftpack as sf
from astropy.io import fits
from create_multilayer_arbase import create_multilayer_arbase
import time
import psutil
import os


class ArScreens(object):
    """
    Class to generate atmosphere phase screens using an autoregressive
    process to add stochastic noise to an otherwise frozen flow.
    @param n          Number of subapertures across the screen
    @param m          Number of pixels per subaperature
    @param pscale     Pixel scale
    @param rate       A0 system rate (Hz)
    @param paramcube  Parameter array describing each layer of the atmosphere
                      to be modeled.  Each row contains a tuple of 
                      (r0 (m), velocity (m/s), direction (deg), altitude (m))
                      describing the corresponding layer.
    @param alpha_mag  magnitude of autoregressive parameter.  (1-alpha_mag)
                      is the fraction of the phase from the prior time step
                      that is "forgotten" and replaced by Gaussian noise.
    """
    def __init__(self, n, m, pscale, rate, paramcube, alpha_mag, ranseed=None):

        self.pl, self.alpha = create_multilayer_arbase(n, m, pscale, rate, paramcube, alpha_mag)
        self._phaseFT = None
        self.screens = [[] for x in paramcube]
        ra.seed(ranseed)

    def get_ar_atmos(self):
        shape = self.alpha.shape
        newphFT = []
        newphase = []
        for i, powerlaw, alpha in zip(range(shape[0]), self.pl, self.alpha):
            noise = ra.normal(size=shape[1:3])
            noisescalefac = np.sqrt(1. - np.abs(alpha**2))
            noiseFT = sf.fft2(noise)*powerlaw
            if self._phaseFT is None:
                newphFT.append(noiseFT)
            else:
                newphFT.append(alpha*self._phaseFT[i] + noiseFT*noisescalefac)
            newphase.append(sf.ifft2(newphFT[i]).real)
        return np.array(newphFT), np.array(newphase)

    def run(self, nframes, verbose=False):
        for j in range(nframes):
            if verbose:
                print('time step', j)
            self._phaseFT, screens = self.get_ar_atmos()
            for i, item in enumerate(screens):
                # self.screens[i].append(item)
                self.screens[i] = item
    def write(self, outfile, clobber=True):
        output = fits.HDUList()
        output.append(fits.PrimaryHDU())
        for i, screen in enumerate(self.screens):
            output.append(fits.ImageHDU(np.array(screen)))
            output[-1].name = "Layer %i" % i
        output.writeto(outfile, clobber=clobber)


if __name__ == '__main__':
    # n = 48
    n = 36
    m = 10
    # 图像的大小 = m * n
    bigD = 8.4
    pscale = bigD/(n*m)
    rate = 300.
    alpha_mag = 0.99
    paramcube = np.array([(0.2, 40, 0, 7600),
                          (0.2, 5.7, 320, 16000),
                          ])
    path = r'G:/phase8/myscreens'
    # 循环生成很多张
    # time1 = time.time()
    # for i in range(1):
    #     my_screens = ArScreens(n, m, pscale, rate, paramcube, alpha_mag, ranseed=i)
    #     my_screens.run(200, verbose=True)
    #     my_screens.write('./myscreens/' + str(i+1) + '.npy')
    # time2 = time.time()
    # time = time2-time1
    # print(time)
    # 生成一张
    my_screens = ArScreens(n, m, pscale, rate, paramcube, alpha_mag, ranseed=1)
    my_screens.run(1, verbose=True)
    cloud = np.array(np.sum(np.squeeze(my_screens.screens),0))
    print(cloud)
    print(cloud.shape)
    # print("##############")
    for i in range(100):
        ff = time.time()
        my_screens.run(1, verbose=False)
        # print(time.time() - ff)
        cloud = np.array(np.sum(np.squeeze(my_screens.screens), 0))

        # print(u'当前进程的内存使用：%.4f GB' % (psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024 / 1024))
    # my_screens.write('G:/phase8/ARcircle_data/' + '2' + '.fits')

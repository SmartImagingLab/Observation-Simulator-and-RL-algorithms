# from ast import AugStore
# from curses.ascii import SI
# from queue import Full
from sky_brightness import sky_brightness
import numpy as np
from numpy import inf
from math import ceil
import warnings

def observable(Tarmag,SkyBack,TelEff,TelAper,CamDark,CamRead,Exposuretime,PixelScale,Seeing=None,Wavelength=0.64,FullwellDepth=None,SnrCriterion=5):
    import numpy as np
    from scipy import signal
    #Tarmag is the magnitude of the target, we assume the magnitude is in in R (640 nm)
    #and therefore the photon density would be: 493485/s/cm^2
    #SkyBack is the magnitude of the sky back ground, asssumption is that it has the same
    #magnitude there
    #TelEff is the efficiency of telescope (percentage of photons that would finally arrive
    # the camera)
    #TelAPer is the aperture of the telescope (Calculates the total photons that would get)
    #CamDark is the number of electrons in the camera, in electrons/s
    #CamRead is the number of electrons when read out signal, in electrons/frame
    #Pixelscale is the size of pixels in the camera in arcsec
    #Seeing is the seeing condition, which is the main limitation for ground observation,
    #None for Space telescope
    #FullWellDepth stands for the Full well depth of camera, None for infinite
    #First calculate the size of PSF in one dimension
    if Seeing is None:
        Seeing = 1.22*Wavelength*10**(-6)/TelAper*206265 #206265 helps you to swith from rad to arcsec
        FWHM = ceil(Seeing/PixelScale)
        PSFsize = 3*FWHM
    else:
        FWHM = ceil(Seeing/PixelScale)
        PSFsize = 3*FWHM
    if Seeing/PixelScale < 1 :
        PSFsize = 3
        FWHM = 1
        warnings.warn('PSFsize < 1 ,set PSFsize = 3')
    #Then we calculate the total number of photon
    Targetelectron = 493485*Exposuretime*np.pi*(TelAper*100/2)**2*10**(-1*Tarmag/2.5)*TelEff
    #Calculate the background noise
    Backtelectron = 493485*Exposuretime*np.pi*(TelAper*100/2)**2*10**(-1*SkyBack/2.5)*TelEff
    #Calculate the camera noise
    Camelectron = CamDark*Exposuretime+CamRead
    #We generate the observation data
    Signaleimg = Targetelectron*generateGauss(PSFsize,FWHM)
    #Generate a 2d Possion random matrix, check if this OK
    try:
        Noiseimg = np.random.poisson(Backtelectron,[PSFsize,PSFsize])\
                    + np.random.poisson(Camelectron,[PSFsize,PSFsize])
    except:
        Noiseimg = inf
        # print(Tarmag,SkyBack,Exposuretime)
    Obsimg = Noiseimg + Signaleimg
    if FullwellDepth is not None:
        Obsimg[Obsimg>FullwellDepth] = FullwellDepth
        Signaleimg[Signaleimg>FullwellDepth] = FullwellDepth
    Snr = np.sum(np.sum(Signaleimg))/(np.sum(np.sum(Obsimg)))**(0.5)
    #Check if we can observer
    if Snr>SnrCriterion:
        observable=True
        #TODO:#Do not very clear to that just set as 0.01 of pixel
        astrometrysigma = 0.01*PixelScale
    else:
        observable=False
        astrometrysigma = None
    return observable,astrometrysigma

from scipy import signal
def generateGauss(matsize,sigma):
    gkern1d = signal.gaussian(matsize,std=sigma).reshape(matsize,1)
    gkern2d = np.outer(gkern1d,gkern1d)
    gkern2d = gkern2d/np.sum(np.sum(gkern2d))
    return gkern2d

def calculation_exposure(Tarmag,SkyBack,TelEff,TelAper,CamDark,CamRead,):
    for exposuretime in range(100):
        Exposuretime = 4**exposuretime
        if observable(Tarmag,SkyBack,TelEff,TelAper,CamDark,CamRead,Exposuretime=Exposuretime,PixelScale=1,Seeing=2,Wavelength=0.64,FullwellDepth=None,SnrCriterion=5)[0]:
            return Exposuretime
    return inf

# for SkyBack in range(17,25):
#     for tarmag in range(0,34):
#         print(SkyBack,tarmag,calculation_exposure(tarmag,SkyBack,0.9,10,1,5))

# from numpy import inf
# for SkyBack in range(18,21):
#     Exposuretime = 0
#     for tarmag in range(0,36):
#         if Exposuretime == inf:
#             break
#         Exposuretime = 0
#         while True:
#             flag = observable(Tarmag=tarmag,SkyBack=SkyBack,TelEff=0.9,TelAper=1,CamDark=1,CamRead=5,Exposuretime=Exposuretime,PixelScale=1,Seeing=2,Wavelength=0.64,FullwellDepth=None,SnrCriterion=5)[0]
#             if flag == False and Exposuretime <= 60*20:
#                 Exposuretime += 1
#             else:
#                 if Exposuretime >= 60*20:
#                     Exposuretime = inf
#                 print("天光背景为%d的夜空看到%d的星等需要%.3f的时间" % (SkyBack, tarmag, Exposuretime))
#                 break

# import ephem
# import numpy as np
# from numpy import pi
# # from astro import angular_separation
# Observer = ephem.Observer()
# Observer.lat,Observer.lon,Observer.date = '42.37', '-71.03','2022/4/1 0:00:00'
# moon = ephem.Moon()
# Mars = ephem.Mars()
# while True:
#     moon.compute(Observer)
#     Mars.compute(Observer)
#     tarmag = 22
#     Angular_separation = ephem.separation((moon.a_ra, moon.a_dec), (Mars.a_ra, Mars.a_dec))
#     SkyBack = sky_brightness(180-moon.moon_phase*180,abs(Angular_separation),abs(pi/2-float(Mars.alt)),abs(pi/2-float(moon.alt)),k=0.0084, B_zen=79.0)
#     for i in range(0,100):
#         Exposuretime = 2 ** i
#         flag = \
#         observable(Tarmag=tarmag, SkyBack=SkyBack, TelEff=0.9, TelAper=1, CamDark=1, CamRead=5, Exposuretime=Exposuretime,
#                    PixelScale=1, Seeing=2, Wavelength=0.64, FullwellDepth=None, SnrCriterion=5)[0]
#         if flag == True :
#             print("天光背景为%d的夜空看到%d的星等需要%.3f的时间" % (SkyBack, tarmag, Exposuretime))
#             break
#     Observer.date += 0.2
#     if Observer.date > ephem.Date('2022/5/15 0:00:00'):
#         break

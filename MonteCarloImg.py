"""It is a Monte Carlo Simulator code to generate an observation image according to the RA, DEC, Star catalog and
moving targets catalog for Training of the Simulator"""
#Basic Packages to import
import astropy
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
from pyia import GaiaData
import os
import pyia
import subprocess
from astroquery.gaia import Gaia
import astropy.units as u
from astropy.coordinates import SkyCoord
from astroquery.gaia import Gaia
from astropy.wcs import WCS
from astropy.wcs import utils
import pandas as pd
#We use all the coordinates defined in astropy SkyCoord for calculation of a celestial object
class Simulator:
    """Parameter Definition:
    Ra and Dec are used to define the point direction of the telescope (do not consider feasibility of the telescope in deg
    Fov is used to describe the field of view of the observation in deg
    Aperture is used to describe the aperture of the telescope in metre
    Secondary Aperture is used to describe the aperture size of the secondary mirror in metre
    Pixelscale is used to describe the pixlescale of the detector in arcsec/pixel
    Seeing is used to describe the atmospheric turbulence induced PSF
    Efficiency is used to describe the efficiency of all the optical telescope in percentage
    SkyBack is used to describe the sky background level in mag/s/arcsec^2
    DetectorBack is used describe the background noise of the detector counts/s
    FullwellDepth is the Full Well Depth of the detector
    ReadNoise is used to describe the readout noise counts
    Arm_n is the number of the arms
    Arm_t is the thickness of the arms
    Obstime is the observation time in UTC time (Not sure, follow astropy definition)
    Exptime is the total exposure time in seconds
    TODO: So many parameters, it would be better to use yaml as default configuration files and load the file for simulation
    """
    def __init__(self, Ra, Dec, Fov, Aperture, SecAper, Pixelscale, Seeing, Efficiency, SkyBack, DetectorBack, ReadNoise, FullWell, Obstime, Exptime, Arm_n = 3, Arm_T = 0.1, frame='icrs'):
        "Generate the Variables according to given pointing direction and field of view"
        "Set scales of variables first"
        """Ra and Dec are pointing direction
        Fov is the field of view"""
        #Maximal row limitation is set as 1,000,000
        Gaia.ROW_LIMIT = 1000000
        #Using Gaia Table DR3
        Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"
        #Define reference frame of simulation
        self.frame = frame
        #We will generate the coordinate according to observation condition
        self.Fov_deg = u.Quantity(Fov, u.deg)
        #define the pointing direction
        self.coord = SkyCoord(ra=Ra, dec=Dec, unit=(u.degree, u.degree), frame=self.frame)
        #Define the image size from arcsec to degree
        self.Pixelscale=Pixelscale/3600.
        self.imgsize = Fov/Pixelscale
        #Generate World Coordinate System
        #TODO: This part needs to mended according to Fits defintion Peng20230115
        racentpix = self.Fov_deg.value/self.Pixelscale/2
        deccentpix = self.Fov_deg.value/self.Pixelscale/2
        self.wcs = self.construct_wcs(Ra, Dec, racentpix,deccentpix)
        #End of wcs coordinate definition here (this part needs to be modified later)
        #Now we define simulation parameters
        #Aperture size
        self.Aperture = Aperture
        #Secondary mirror size
        self.SecAper = SecAper
        #Number of arms
        self.Arm_n = Arm_n
        #Thickness of arms
        self.Arm_T = Arm_T
        #Fwhm of seeing condition
        self.Seeing = Seeing
        #Efficiency of all the telescope
        self.Efficiency = Efficiency
        #Sky Background level
        self.SkyBack = SkyBack
        #Detector Efficiency
        self.DetectorBack = DetectorBack
        #Read out Noise
        self.ReadNoise = ReadNoise
        #Fullwell depth
        self.Fullwell = FullWell
        #Observation time
        self.Obstime = Obstime
        #Exposure time length in seconds
        self.Exptime = Exptime

    def construct_wcs(self,racent,deccent,racentpix,deccentpix):
        #Built WCS coordinate according to a similar function
        print("Constructing WCS from a dictionary header: \n")
        header = {'NAXIS': 2,
                  'NAXIS1': self.Fov_deg.value / self.Pixelscale,
                  'CTYPE1': 'RA---TAN',
                  'CRVAL1': racent,
                  'CRPIX1': racentpix,
                  'CDELT1': self.Pixelscale,
                  'NAXIS2': self.Fov_deg.value / self.Pixelscale,
                  'CTYPE2': 'DEC--TAN',
                  'CRVAL2': deccent,
                  'CRPIX2': deccentpix,
                  'CDELT2': self.Pixelscale}
        wcs = WCS(header)
        return wcs

    def query_celestial_objects(self,coordinate,width,height,columns=['ra','dec','phot_g_mean_flux','phot_g_mean_mag']):
        #We use the Gaia catalog to obtain celestial objects coordinate and magnitudes from gaia DR3
        print('Load catalog from Gaia DR3 \n')
        #Set parameters
        width = u.Quantity(width, u.deg)
        height = u.Quantity(height, u.deg)
        #We could generate lists according to different requirements here
        r_list = Gaia.query_object_async(coordinate=coordinate,width=width,height=height,temcolumn=columns)
        return r_list

    def coord_trans(self,ralist,declist,racent,deccent,racentpix,deccentpix):
        #It would transfrom coordinate of celestial objects from celestial coordinate to pixel coordinate
        wcs = self.construct_wcs(racent,deccent,racentpix,deccentpix)
        #We generate list for x and y coordinate in the system
        newxlist=np.zeros(np.shape(ralist))
        newylist=np.zeros(np.shape(declist))
        #We define the maximal size of the coordinate
        maxsize = self.Fov_deg/self.Pixelscale
        #TODO, the speed could be accelerated with parallel with jit
        for ind in range(np.shape(newylist)[0]):
            coord = SkyCoord(ra=ralist[ind]*u.deg,dec=declist[ind]*u.deg)
            temtarget = utils.skycoord_to_pixel(coord,wcs)
            newxlist[ind] = temtarget[0]
            newylist[ind] = temtarget[1]
        #It is a problem that final results would be much larger than we expected, therefore, I will modify the
        #results accordingly
        #Besides, Here we assume the image has many stars, if we do not consider many targets there would also be problem
        newxlist=(newxlist-np.min(newxlist))/(np.max(newxlist)-np.min(newxlist))*2*maxsize
        newylist=(newylist-np.min(newylist))/(np.max(newylist)-np.min(newylist))*2*maxsize
        return newxlist,newylist

    def img_generation(self,listname,filename,wavelength='600',conffolder='./usr',filefolder='./data'):
        #It would modify skymaker configuration files and generate fits images for further processing
        #Load default configuration file NAME: me.conf in this code
        defaultskyfile = open(conffolder+'/me.conf', 'r')
        conf = defaultskyfile.readlines()
        defaultskyfile.close()
        #Now we modify these files
        conf[6] = 'IMAGE_NAME      ' + str(filename) + '        # Name of the output frame\n'
        conf[7] = 'IMAGE_SIZE     ' + str(self.imgsize) + '            # width of the simulated frame\n'
        conf[19] = 'SATUR_LEVEL     ' + str(self.Fullwell) + '           # saturation level (ADU)\n'
        conf[20] = 'READOUT_NOISE   ' + str(self.ReadNoise) + '             # read-out noise (e-)\n'
        conf[21] = 'EXPOSURE_TIME   ' + str(self.Exptime) + '           # total exposure time (s)\n'
        #Pixel scale reshift back to pixel scale here according to Skymaker def
        conf[26] = 'PIXEL_SIZE      ' + str(self.Pixelscale*3600) + '           # pixel size in arcsec.\n'
        conf[34] = 'SEEING_FWHM     ' + str(self.Seeing) + '             # FWHM of seeing in arcsec (incl. motion)\n'
        conf[46] = 'M1_DIAMETER     ' + str(self.Aperture) + '             # Diameter of the primary mirror (in meters)\n'
        conf[47] = 'M2_DIAMETER     ' + str(self.SecAper) + '             # Obstruction diam. from the 2nd mirror in m.\n'
        conf[48] = 'ARM_COUNT       ' + str(self.Arm_n) + '               # Number of spider arms (0 = none)\n'
        conf[49] = 'ARM_THICKNESS   ' + str(self.Arm_T) + '            # Thickness of the spider arms (in mm)\n'
        conf[64] = 'WAVELENGTH      ' + str(wavelength) + '             # average wavelength analysed (microns)\n'
        conf[65] = 'BACK_MAG        ' + str(self.SkyBack) + '            # background surface brightness (mag/arcsec2)\n'
        # We will open the file for image generation
        homefolder = os.getcwd()
        os.chdir(filefolder)
        temskyfile = open(filename + '.conf', 'w')
        temskyfile.writelines(conf)
        temskyfile.close()
        subprocess.call(['sky', '-c ', filename + '.conf ', listname])
        # subprocess.run('rm -rf '+filename+'.conf', shell=True)
        os.chdir(homefolder)
        print('The '+str(filename)+' has been successfully generated')
        return 0














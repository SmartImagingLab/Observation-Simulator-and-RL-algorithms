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
import pandas as pd
#We use all the coordinates defined in astropy SkyCoord for calculation of a celestial object
class Simulator:
    """Parameter Definition:
    Ra and Dec are used to define the point direction of the telescope (do not consider feasibility of the telescope in deg
    Fov is used to describe the field of view of the observation in deg
    Aperture is used to describe the aperture of the telescope in metre
    Pixelscale is used to describe the pixlescale of the detector in arcsec/pixel
    Seeing is used to describe the atmospheric turbulence induced PSF
    Efficiency is used to describe the efficiency of all the optical telescope in percentage
    SkyBack is used to describe the sky background level in mag/s/arcsec^2
    DetectorBack is used describe the background noise of the detector counts/s
    ReadNoise is used to describe the readout noise counts
    Obstime is the observation time in UTC time (Not sure, follow astropy definition)
    Exptime is the total exposure time in seconds
    """
    def __init__(self, Ra, Dec, Fov, Aperture, Pixelscale, Seeing, Efficiency, SkyBack, DetectorBack, ReadNoise, Obstime, Exptime, frame='galactic'):
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
        #Observation time
        self.Obstime = Obstime
        #Exposure time length in seconds
        self.Exptime = Exptime
        return None

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
        temcolumn = columns
        r_list = Gaia.query_object_async(coordinate=coordinate,width=width,height=height,temcolumn)
        return r_list













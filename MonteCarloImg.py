"""It is a Monte Carlo Simulator code to generate an observation image according to the RA, DEC, Star catalog and
moving targets catalog for Training of the Simulator"""
#Basic Packages to import
import astropy
import numpy as np
import matplotlib.pyplot as plt
#We use all the coordinates defined in astropy SkyCoord for calculation of a celestial object
from astropy.coordinates import SkyCoord as skycoor
class Simulator (Ra, Dec, Fov, Aperture, Pixelscale, Seeing, Efficiency, SkyBack, DetectorBack, ReadNoise, Obstime,Exptime, frame='galactic'):
    """Parameter Definition:
    Ra and Dec are used to define the point direction of the telescope (do not consider feasibility of the telescope in deg
    Fov is used to describe the field of view of the observation is deg
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
    def __init__(self, Ra, Dec, Fov):
        "Generate the Variables according to given pointing direction and field of view"






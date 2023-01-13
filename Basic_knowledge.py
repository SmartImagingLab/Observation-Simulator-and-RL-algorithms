import numpy as np
import ephem
from astropy.coordinates import AltAz
from numpy import pi
from astropy.io import fits
import astropy.units as u
from astropy.coordinates import SkyCoord, EarthLocation
from astropy.time import Time
from datetime import datetime
import math

def radec2azalt(time, ra, dec, lat, lon, height=0):
    '''输入输出必须全部是角度！！！'''
    if isinstance(ra,ephem.Angle):
        ra = float(math.degrees(ra))
    else:
        raise TypeError("输入的数据必须是ephem.Angle")
    if isinstance(dec,ephem.Angle):
        dec = float(math.degrees(dec))
    else:
        raise TypeError("输入的数据必须是ephem.Angle")
    if isinstance(lat,ephem.Angle):
        lat = float(math.degrees(lat))
    else:
        raise TypeError("输入的数据必须是ephem.Angle")
    if isinstance(lon,ephem.Angle):
        lon = float(math.degrees(lon))
    else:
        raise TypeError("输入的数据必须是ephem.Angle")
    # ra_1 = float(ra)
    # dec_1 = float(dec)
    # 转化将"2022/2/21 00:00:00"转化为2022-02-21T00:00:00.000
    a = datetime.strptime(str(time), '%Y/%m/%d %H:%M:%S').isoformat()
    obstime = Time(a, format='isot')
    location = EarthLocation.from_geodetic(lon, lat)
    local_altaz = AltAz(obstime=obstime, location=location)
    icrs = SkyCoord(ra * u.degree, dec * u.degree, frame='icrs')
    altaz = icrs.transform_to(local_altaz)
    az = (altaz.az * u.deg).value
    alt = (altaz.alt * u.deg).value
    return az, alt

def azalt2radec(time, az, alt, lat, lon, height=0):
    '''输入输出必须全部是角度！！！'''
    if isinstance(az,ephem.Angle):
        az = math.degrees(az)
    else:
        raise TypeError("输入的数据必须是ephem.Angle")
    if isinstance(alt,ephem.Angle):
        alt = math.degrees(alt)
    else:
        raise TypeError("输入的数据必须是ephem.Angle")
    if isinstance(lat,ephem.Angle):
        lat = math.degrees(lat)
    else:
        raise TypeError("输入的数据必须是ephem.Angle")
    if isinstance(lon,ephem.Angle):
        lon = math.degrees(lon)
    else:
        raise TypeError("输入的数据必须是ephem.Angle")
    a = datetime.strptime(str(time), '%Y/%m/%d %H:%M:%S').isoformat()
    obstime = Time(a, format='isot')
    location = EarthLocation(lat=lat * u.deg, lon=lon * u.deg, height=height * u.m)
    crab = SkyCoord(obstime=obstime, location=location, az=az * u.deg, alt=alt * u.deg, frame='altaz')
    coord = crab.transform_to('icrs')
    ra = (coord.ra * u.deg).value
    dec = (coord.dec * u.deg).value
    return ra, dec

def angular_separation(lon1, lat1, lon2, lat2):
    if lon1 == None or lat1 == None or lon2 == None or lat2 == None :
        return None
    else:
        sdlon = np.sin(lon2 - lon1)
        cdlon = np.cos(lon2 - lon1)
        slat1 = np.sin(lat1)
        slat2 = np.sin(lat2)
        clat1 = np.cos(lat1)
        clat2 = np.cos(lat2)

        num1 = clat2 * sdlon
        num2 = clat1 * slat2 - slat1 * clat2 * cdlon
        denominator = slat1 * slat2 + clat1 * clat2 * cdlon

        return np.arctan2(np.hypot(num1, num2), denominator)

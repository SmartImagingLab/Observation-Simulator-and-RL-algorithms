from numpy import cos,sin,log,pi,e,log

def sky_brightness(moon_phase,angular_separation,zenith_distance,zenith_distance_moon,k = 0.0084,B_zen = 79.0):
    I = 10 ** (-0.4 * (3.84 + 0.026 * abs(moon_phase) + 4 * (10 ** - 9 * moon_phase ** 4)))
    f = 10**5.36*(1.06 +(cos(angular_separation))**2)+10**(6.15-angular_separation/40)
    def X(zenith_distance):
        return (1 - 0.96*(sin(zenith_distance))**2)**-0.5
    B_moon = f*I*10**(-0.4*k*X(zenith_distance_moon))*(1-10**(-0.4*k*X(zenith_distance)))
    B0 = B_zen*10**(-0.4*k*(X(zenith_distance)-1))*X(zenith_distance)
    return B_to_V(B_moon + B0)

def B_to_V(B):
    return (20.7233 - log(B/34.08))/0.92104

def B_moon(V,Z,K = 0.172,Bzen = 79):
    B = 34.08 * e ** (20.7233 - 0.92107 * V)
    X = (1 - 0.96 * sin(Z * pi / 180) ** 2) ** (-0.5)
    B0 = Bzen * 10 ** (-0.4 * K * (X - 1)) * K
    return B - B0


# import ephem
# import numpy as np
# from astro import angular_separation
# Observer = ephem.Observer()
# Observer.lat,Observer.lon,Observer.date = '42.37', '-71.03','2022/4/1 0:00:00'
# moon = ephem.Moon()
# Mars = ephem.Mars()
# while True:
#     moon.compute(Observer)
#     Mars.compute(Observer)
#     a,b,c,d = moon.a_ra, moon.a_dec, Mars.a_ra, Mars.a_dec
#     Angular_separation = angular_separation(moon.a_ra, moon.a_dec,Mars.a_ra, Mars.a_dec)
#     print(Observer.date,moon.moon_phase*180)
#     print(sky_brightness(180-moon.moon_phase*180,abs(Angular_separation),abs(pi/2-float(Mars.alt)),abs(pi/2-float(moon.alt)),k=0.0084, B_zen=79.0))
#     Observer.date += 0.2
#     if Observer.date > ephem.Date('2022/5/15 0:00:00'):
#         break

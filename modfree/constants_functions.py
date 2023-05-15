# file containing the used constants and useful functions:
import numpy as np

theta = 22 # angle between CSA and dd axis

gamma15N = -2.7126 * 1e7 # rad s-1 T-1
gamma1H = 2.6752219 * 1e8 # rad s-1 T-1
rNH = 1.015 * 1e-10 # 1.023e-10 is Average NH bond length cf Yao et al JACS 2008, in m
tCSA = -172.0 * 1e-6 # CSA cf Kroenke et al JACS 1999
mu_0 = 1.2566370614359173 * 1e-6 # vacuum permeability
h = 6.62607004e-34 # Planck constant
R = 8.31446261815324 # J.mol-1.K-1

d = mu_0*h*gamma1H*gamma15N/(8*(np.pi**2)*(rNH**3)) # NH dipolar coupling constant
theta = theta*np.pi/180 # in rad.


# Legendre 2
def P2(x):
    return (3*x*x - 1)/2


# MHz to Tesla
def MHz2T(field_MHz):
    return field_MHz*2*np.pi*1e6/gamma1H

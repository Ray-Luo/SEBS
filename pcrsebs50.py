#!/usr/bin/env python
# -*- coding: latin-1 -*-
import Tkinter, tkFileDialog, tkSimpleDialog
from Tkinter import *
from pcraster import *
from time import *
import string
import math

# Splash screen
main = Tk()
main.title('SEBS v.5.0')
#main.iconbitmap('f:/d/temp/globe.ico')
msg = Message(main, text="============================================\nPCRaster SEBS version 5.0 (January 28th 2010).\nCalculates surface energy fluxes\nBased on SEBS (Su, 2002)\n\nProgrammed by J. van der Kwast\nUnit Environmental Modelling\nFlemish Institute for Technological Research (VITO)\nhans.vanderkwast@vito.be\n============================================", width=500)
msg.pack()

button = Button(main, text="Continue", command=main.destroy)
button.pack()

mainloop()

# General functions
class parameterDialog(tkSimpleDialog.Dialog):

    def body(self, master):

        Label(master, text="Transmissivity:").grid(row=0)
        Label(master, text="Latitude [dd]: ").grid(row=1)
        Label(master, text="Day of Year:").grid(row=2)
        Label(master, text="Time of overpass [decimal hours]:").grid(row=3)
        Label(master, text="PBL height [m]:").grid(row=4)
        Label(master, text="Measurement height [m]:").grid(row=5)
        Label(master, text="Wind speed [m/s]:").grid(row=6)
        Label(master, text="Air temperature [Celcius]:").grid(row=7)
        Label(master, text="Air pressure [Pa]:").grid(row=8)
        Label(master, text="Relative humidity [0-1]:").grid(row=9)

        self.e1 = Entry(master)
        self.e2 = Entry(master)
        self.e3 = Entry(master)
        self.e4 = Entry(master)
        self.e5 = Entry(master)
        self.e6 = Entry(master)
        self.e7 = Entry(master)
        self.e8 = Entry(master)
        self.e9 = Entry(master)
        self.e10 = Entry(master)

        self.e1.grid(row=0, column=1)
        self.e1.insert(0,0.788606)
        self.e2.grid(row=1, column=1)
        self.e2.insert(0,33.9932)
        self.e3.grid(row=2, column=1)
        self.e3.insert(0,294.0)
        self.e4.grid(row=3, column=1)
        self.e4.insert(0,11.217)
        self.e5.grid(row=4, column=1)
        self.e5.insert(0,1000.0)
        self.e6.grid(row=5, column=1)
        self.e6.insert(0,2.5)
        self.e7.grid(row=6, column=1)
        self.e7.insert(0,4.313)
        self.e8.grid(row=7, column=1)
        self.e8.insert(0,27.35)
        self.e9.grid(row=8, column=1)
        self.e9.insert(0,100000.0)
        self.e10.grid(row=9, column=1)
        self.e10.insert(0,0.5055)
        return self.e1 # initial focus

    def apply(self):
        first = float(self.e1.get())
        second = float(self.e2.get())
        third = float(self.e3.get())
        fourth = float(self.e4.get())
        fifth = float(self.e5.get())
        sixth = float(self.e6.get())
        seventh = float(self.e7.get())
        eight = float(self.e8.get())
        nineth = float(self.e9.get())
        tenth = float(self.e10.get())
	
        self.result = first,second,third,fourth,fifth,sixth,seventh,eight,nineth,tenth 

def guiInputMap(map,default):
    root = Tkinter.Tk()
    root.withdraw()
    question = 'Choose '+ map + ' map'
    selectInputMap = tkFileDialog.askopenfilename(parent=root,title=question, filetypes=[('PCRaster Files','*.map'),],initialfile=default)
    return selectInputMap

def guiOutputMap(map,default):
    root = Tkinter.Tk()
    root.withdraw()
    question = 'Save '+ map + ' map'
    selectOutputMap = tkFileDialog.asksaveasfilename(parent=root,title=question,filetypes=[('PCRaster Files','*.map'),],initialfile=default)
    return selectOutputMap

def assertWithinRange(map, Lower, Upper):
   """ Checks the range of maps
   map Input PCRaster map"""
   Minimum = cellvalue(mapminimum(map), 0, 0)
   Maximum = cellvalue(mapmaximum(map), 0, 0)
   assert Minimum[0] >= Lower and Maximum[0] <= Upper

def writeVar(varName, varContent):
   """Writes the value of a variable to a file
   varName string name of variable
   varContent value of variable"""
   
   varContent = str(varContent)
   checkFile.write(varName+" = "+varContent+"\n")
   return

def writeLoc(varName, map):
   """Writes values of a variable at a specific location to a file
   varName string name of variable
   map name of map"""
   
   findLoc = cellvalue(map, rowy, colx)
   map = findLoc[0]
   writeVar(varName, map)
   return

def median(map):
   """Function to calculate median of a map

   map Input PCRaster map"""

   OrderMap = order(map)
   Mid = roundoff(mean(OrderMap))
   MidMap = ifthenelse(OrderMap == Mid, map, 0)
   Median = cellvalue(mapmaximum(MidMap), 0, 0)
   assert Median[0] > 0.0
   return Median[0]

def mean(map):
   """Calculates the mean value of a PCRaster map

   map Input PCRaster map"""
   
   Total = cellvalue(maptotal(map), 0, 0)
   NumCells = cellvalue(maparea(map) / cellarea(), 0, 0)
   assert NumCells[0] != 0
   mean = Total[0] / NumCells[0]
   return mean

# SEBS functions
def Rswd(DEM, Lat, Trans, DOY, Time):
   """ Potential Radiation Equator model
   (c) O. van Dam, UU, Tropenbos-Guyana
   Version 5, June 2000
   NOTE: Copyright: This program is free to use provided�
         you refer to the manualfor citation.
         Do not distribute without prior approval of the author.
         Manual and additional info: O.vanDam@geog.uu.nl

   -----------------------------------------------------
                   Model for calculation
               incoming potential light energy
   -----------------------------------------------------
   
   DEM Input Digital Elevation Model (spatial)
   Lat Latitude in decimal degrees (non-spatia)
   Trans Transmissivity tau (Gates, 1980) (non-spatial)
   DOY Day of Year (non-spatial)
   Time Time in hours (non-spatial)"""
   
   # constants
   pi       = 3.1415          # pi
   Sc       = 1367.0          # Solar constant (Gates, 1980) [W/m2]

#   SlopMap = scalar(atan(slope(DEM)))
   SlopMap = 20
#   AspMap  = scalar(aspect(DEM)) # aspect [deg]
   AspMap  = 60
   AtmPcor = ((288.0-0.0065*DEM)/288.0)**5.256 # atmospheric pressure correction [-]

   # Solar geometry
   # ----------------------------
   # SolDec  :declination sun per day  between +23 & -23 [deg]
   # HourAng :hour angle [-] of sun during day
   # SolAlt  :solar altitude [deg], height of sun above horizon
   SolDec  = -23.4*math.cos(360.0*(DOY+10.0)/365.0)
   HourAng = 15.0*(Time-12.01)
#   SolAlt  = scalar(math.asin(scalar(math.sin(Lat)*math.sin(SolDec)+math.cos(Lat)*math.cos(SolDec)*math.cos(HourAng))))
   SolAlt  = math.asin(math.sin(Lat)*math.sin(SolDec)+math.cos(Lat)*math.cos(SolDec)*math.cos(HourAng))

   # Solar azimuth
   # ----------------------------
   # SolAzi  :angle solar beams to N-S axes earth [deg]
#   SolAzi = scalar(math.acos((math.sin(SolDec)*math.cos(Lat)-math.cos(SolDec)*math.sin(Lat)*math.cos(HourAng))/math.cos(SolAlt)))
   SolAzi = math.acos((math.sin(SolDec)*math.cos(Lat)-math.cos(SolDec)*math.sin(Lat)*math.cos(HourAng))/math.cos(SolAlt))
#   SolAzi = ifthenelse(Time <= 12.0, SolAzi, 360.0 - SolAzi)
   if Time <= 12.0:
       SolAzi = SolAzi
   else:
       SolAzi = 360.0 - SolAzi
   # Additonal extra correction by R.Sluiter, Aug '99
#   SolAzi = ifthenelse(SolAzi > 89.994 and SolAzi < 90.0, 90.0, SolAzi)
   if SolAzi > 89.994 and SolAzi < 90.0:
       SolAzi = 90.0
   else:
       SolAzi = SolAzi
#   SolAzi = ifthenelse(SolAzi > 269.994 and SolAzi < 270.0, 270.0, SolAzi)
   if SolAzi > 269.994 and SolAzi < 270.0:
       SolAzi = 270.0
   else:
       SolAzi = SolAzi

   # Surface azimuth
   # ----------------------------
   # cosIncident :cosine of angle of incident; angle solar beams to angle surface
   cosIncident = math.sin(SolAlt)*math.cos(SlopMap)+math.cos(SolAlt)*math.sin(SlopMap)*math.cos(SolAzi-AspMap)

   # Critical angle sun
   # ----------------------------
   # HoriAng  :tan maximum angle over DEM in direction sun, 0 if neg·
   # CritSun  :tan of maximum angle in direction solar beams
   # Shade    :cell in sun 1, in shade 0
#   HoriAng   = horizontan(DEM,SolAzi)
   HoriAng = 0
#   HoriAng   = ifthenelse(HoriAng < 0.0, scalar(0.0), HoriAng)
   if HoriAng < 0.0:
       HoriAng = 0.0
   else:
       HoriAng = HoriAng
#   CritSun   = ifthenelse(SolAlt > 90.0, scalar(0.0), scalar(atan(HoriAng)))
   if SolAlt > 90.0:
       CritSun = 0.0
   else:
       CritSun = math.atan(HoriAng)
#   Shade   = ifthenelse(SolAlt > CritSun, scalar(1), scalar(0))
   if SolAlt > CritSun:
       Shade = 1
   else:
       Shade = 0
   
   # Radiation outer atmosphere
   # ----------------------------
   OpCorr = Trans**((math.sqrt(1229.0+(614.0*math.sin(SolAlt))**2.0)-614.0*math.sin(SolAlt))*AtmPcor)     # correction for air masses [-]·
   Sout   = Sc*(1.0+0.034*math.cos(360.0*DOY/365.0)) # radiation outer atmosphere [W/m2]
   Snor   = Sout*OpCorr                    # rad on surface normal to the beam [W/m2]

   # Radiation at DEM
   # ----------------------------
   # Sdir   :direct sunlight on a horizontal surface [W/m2] if no shade
   # Sdiff  :diffuse light [W/m2] for shade and no shade
   # Stot   :total incomming light Sdir+Sdiff [W/m2] at Hour
   # PotRad :avg of Stot(Hour) and Stot(Hour-HourStep)
#   Sdir   = ifthenelse(Snor*cosIncident*Shade < 0.0, 0.0, Snor*cosIncident*Shade)
   if (Snor*cosIncident*Shade < 0.0):
       Sdir = 0.0
   else:
       Sdir = Snor*cosIncident*Shade
#   Sdiff  = ifthenelse(Sout*(0.271-0.294*OpCorr)*sin(SolAlt) < 0.0, 0.0, Sout*(0.271-0.294*OpCorr)*sin(SolAlt))
   if Sout*(0.271-0.294*OpCorr)*math.sin(SolAlt) < 0.0:
       Sdiff = 0.0
   else:
       Sdiff = Sout*(0.271-0.294*OpCorr)*math.sin(SolAlt)
   #Rswd  = Sdir + Sdiff                                         # Rad [W/m2]
   Rswd = Snor
   return Rswd

def LAINDVI(NDVI):
   """ Calculates initial Leaf Area Index from NDVI (Su, 1996). Output is non-spatial
   
   NDVI Input Normalized Difference Vegetation Index Map (scalar, ratio between 0 and 1)"""

   #nd_max = cellvalue(mapmaximum(NDVI), 0, 0)
   nd_max = NDVI
   #cellvalue(mapminimum(NDVI), 0, 0)
   nd_min = NDVI
   #nd_mid = median(NDVI)
   nd_mid = NDVI
   #nd_df = nd_max[0] - nd_min[0]
   nd_df = 1.0
   if nd_df == 0.0:
      nd_df == 1.0

   LAI = math.sqrt(nd_mid * (1.0 + nd_mid) / (1.0 - nd_mid + 1.0E-6))
   if LAI > 6.0:
      LAI == 6.0
   return LAI, nd_max, nd_min, nd_mid, nd_df

def u_pbl(NDVI):
   """Calculates Planetary Boundary Layer wind speed [m s-1] from NDVI
   
   NDVI Input PCRaster NDVI map (scalar, ratio between 0 and 1)"""
   
   z0m = 0.005 + 0.5 * (nd_mid/nd_max) ** 2.5
   assert z0m >= 0.0
   fc = ((nd_mid - nd_min) / nd_df) ** 2.0    # fractional vegetation cover == Wfol (-)
   assert fc >= 0.0
   h = z0m / 0.136                            # total height of vegetation (m)
   print "h=",h
   d = 2.0/3.0 * h			      # zero plane displacement (m)
   u_c = math.log((z_pbl - d) / z0m) / math.log((z_ms - d) / z0m)
   print "u_c=", math.log((z_ms - d) / z0m)
   u_pbl = u_s * u_c
   return u_pbl, z0m, d, fc, h

# FUNCTIONS FOR DETERMINATION OF ROUGHNESS LENGTH FOR HEAT TRANSFER
def FKB_1(u_zref, zref, h, LAI, Wfol, Ta, pa):
   """Initial determination of roughness length for heat transfer (non-spatial)
   KB-1 function according to Massman, 1999
   Convention of variable names:
   f_z = f(z)
   d2h = d/h
   
   u_zref Input wind speed at reference height [m s-1]
   zref Input reference height [m]
   h Input canopy height [m]
   LAI Input canopy total Leaf Area Index [-]
   Wfol Input Fractional canopy cover [-]
   Ta Input ambient temperature [degrees Celsius]
   pa Input ambient air pressure [Pa]"""

   # Constants
   C_d = 0.2   # foliage drag coefficient
   C_t = 0.01  # heat transfer coefficient
   k = 0.41     # Von Karman constant
   Pr = 0.7    # Prandtl number
   hs = 0.009  # height of soil roughness obstacles (0.009-0.024)
   
   # Calculations
   Wsoil = 1.0 - Wfol
   if Wfol == 0.0: # for bare soil take soil roughness
      h = hs
   assert Wfol >= 0.0 and Wfol <= 1.0 and Wsoil >= 0.0 and Wsoil <= 1.0
   z0 = 0.136 * h   # Brutsaert (1982)
   u_h0 = u_zref * math.log(2.446) / math.log((zref - 0.667 * h)/z0) # wind speed at canopy height
#   u_h0 = cellvalue(u_h0, 0, 0)
#   u_h0 = u_h0[0]
   assert u_h0 >= 0.0
   ust2u_h = 0.32 - 0.264/math.exp(15.1 * C_d * LAI)
   ustarh = ust2u_h * u_h0
   nu0 = 1.327E-5 * (101325.0 / pa) * (Ta / 273.15 + 1.0) ** 1.81 # kinematic viscosity
   n_h = C_d * LAI / (2.0 * ust2u_h ** 2.0)
   # First term
   if n_h <> 0.0:
       F1st = k * C_d / (4.0 * C_t * ust2u_h * (1.0 - math.exp(n_h/2.0))) * Wfol ** 2.0
#      F1st = k * C_d / (4.0 * C_t * ust2u_h * (1.0 - math.exp(pcrumin(n_h)/2.0))) * Wfol ** 2.0
 
   else:
      F1st = 0.0
   # Second term
   print "nu0 = ",nu0,"ustarh=", ustarh, "h=", h 
   S2nd = k * ust2u_h * 0.136 * Pr ** (2.0/3.0) * math.sqrt(ustarh * h / nu0) * Wfol ** 2.0 * Wsoil ** 2.0
   # Third term
   T3rd = (2.46 * (u_zref * k / math.log(zref/hs) * hs / nu0) ** 0.25 - math.log(7.4)) * Wsoil ** 2.0
   
   return F1st + S2nd + T3rd

def z0h(KB_1, z0m):
   """Calculates the scalar roughness height for heat transfer (z0h)
   KB_1 Input KB_1 values
   z0m Input scalar roughness height for momentum"""
   
   z0h = z0m / math.exp(KB_1)
   return z0h

def GKB_1(u_zref, zref, h, LAI, Wfol, Ta, pa):
   """Same as FKB_1, but then for spatial in- and output"""
   
   # Constants
   C_d = 0.2   # foliage drag coefficient
   C_t = 0.05  # heat transfer coefficient
   k = 0.41     # Von Karman constant
   Pr = 0.7    # Prandtl number
   hs = 0.009  # height of soil roughness obstacles (0.009-0.024)
   
   # Calculations
   Wsoil = 1.0 - Wfol
#   h = ifthenelse(Wfol == 0.0, hs, h)
   if Wfol == 0.0:
       h = hs

   
   z0 = 0.136 * h   # Brutsaert (1982)
   u_h0 = u_zref * math.log(2.446) / math.log ((zref - 0.667 * h)/z0) # wind speed at canopy height
   ust2u_h = 0.32 - 0.264 / math.exp(15.1 * C_d * LAI)
   ustarh = ust2u_h * u_h0
   nu0 = 1.327E-5 * (101325.0/pa) * (Ta / 273.15 + 1.0) ** 1.81 # kinematic viscosity
   n_h = C_d * LAI / (2.0 * ust2u_h ** 2.0)
   # First term
   if n_h != 0.0:
       print "n_h=",n_h
       F1st = k * C_d / (4.0 * C_t * ust2u_h * (1.0 - math.exp(n_h/2.0))) * Wfol ** 2.0
   if n_h == 0.0:
       F1st = 0.0
#   F1st = ifthenelse(pcrne(n_h, 0.0), k * C_d / (4.0 * C_t * ust2u_h * (1.0 - math.exp(pcrumin(n_h)/2.0))) * Wfol ** 2.0, 0.0)
   # Second term
   S2nd = k * ust2u_h * 0.136 * Pr ** (2.0/3.0) * math.sqrt(ustarh * h / nu0) * Wfol ** 2.0 * Wsoil ** 2.0
   # Third term
   T3rd = (2.46 * (u_zref * k / math.log(zref/hs) * hs / nu0) ** 0.25 - math.log(7.4)) * Wsoil ** 2.0
   
   return F1st + S2nd + T3rd

def Rn(Alfa, Rswd, Eair, t_pbl, ems, T):
#def Rn(Alfa, Rswd, Eair, t_pbl, Eground):
   """ Calculation of surface net radiation [W m-2]
   Alfa Input albedo map [-]
   Rswd Input downward solar radiation [W m-2], PCRaster map from POTRAD
   Eair Input emissivity air [-]
   Eground Input PCRaster emissivity map [-]
   t_pbl Input PBL temperature map [K]
   T Surface Kinetic Temperature [K]"""
   
   print "Calculating Net Radiation map..."
   # constants
   sigma = 5.678E-8   #Stefan Boltzmann's constant (W m-2 K-4)
   
   # calculations
   Rn = (1.0 - Alfa) * Rswd + 5.678 * ems * (Eair * (t_pbl/100.0)**4.0 - (T/100.0)**4.0)
   return Rn

def G0(Rn, cover):
   """Calculates Soil Heat Flux [W m-2]
   Rn Input Surface Net Radiation [W m-2]
   cover Input fractional canopy cover [-]"""
   
   print "Calculating soil heat flux map..."
   # constants:
   Gamma_c = 0.05   # ratio of G0 to Rn for full vegetation canopy (Monteith, 1973)
   Gamma_s = 0.315  # ratio of G0 to Rn for bare soil (Kustas & Daughtry, 1989)
   
   # calculation
   G0 = Rn * (Gamma_c + (1.0 - cover) * (Gamma_s - Gamma_c))
   return G0

def FRUstar(z_pbl,hst):
   """Iteration to calculate RUstar
   z_pbl Input PBL depth [m]
   hst Input height of the ASL [m]"""
   
   print "Starting iterations to derive stability parameters..." 
   
   RUstar = ku / zdm
   RH = CH * RUstar / zdh
   RH0 = RH
   Reps = 10.0
   Isteps = 0
   RHA = RH
   RHB = RH
   RH0A = RH0
   RH0B = RH0
   RUstarA = RUstar
   RUstarB = RUstar
   IstepsA = Isteps
   IstepsB = Isteps
   RepsA = Reps
   RepsB = Reps
   itNr = 100.0
   itThreshold = 0.01
     
   while RepsA > itThreshold and IstepsA < itNr:
      RLA = CL * RUstarA ** 3.0 / RHA
      tempBw = Bw(z_pbl, RLA, z0m)
      RUstarA = ku / (zdm - tempBw)
      tempCw = Cw(z_pbl, RLA, z0m, z0h)
      RHA = CH * RUstarA / (zdh - tempCw)
      RepsA = math.fabs(RH0A - RHA)
      difa = math.fabs(RH0A - RHA)
      min = difa
      meandif = difa
      RH0A = RHA
      IstepsA = IstepsA + 1
      percentage = (IstepsA/itNr)*100
      print "Iteration A:", int(percentage), "% completed\r",
   print
   
   while RepsB > itThreshold and IstepsB < itNr:
      RLB = CL * RUstarB ** 3.0 / RHB
      tempPSIm_y1 = PSIm_y(zd0/ RLB)
      tempPSIm_y2 = PSIm_y(z0m / RLB)
      RUstarB = ku / (zdm - tempPSIm_y1 + tempPSIm_y2)
      tempPSIh_y1 = PSIh_y(zd0 / RLB)
      tempPSIh_y2 = PSIh_y(z0h / RLB)
      RHB = CH * RUstarB / (zdh - tempPSIh_y1 + tempPSIh_y2)
      RepsB = math.fabs(RH0B - RHB)
      difb = math.fabs(RH0B - RHB)
      meandif = difb
      min = difb                                                
      RH0B = RHB
      IstepsB =  IstepsB + 1
      percentage = (IstepsB/itNr)*100
      print "Iteration B:", int(percentage), "% completed\r",
#   RUstar = ifthenelse(z_pbl >= hst, RUstarA, RUstarB)
   if z_pbl >= hst:
       RUstar = RUstarA
   else:
       RUstar = RUstarB
#   RL = ifthenelse(z_pbl >= hst, RLA, RLB)
   if z_pbl >= hst:
       RL = RLA
   else:
       RL = RLB
#   dif = ifthenelse(z_pbl >= hst, difa, difb)
   if z_pbl >= hst:
       dif = difa
   else:
       dif = difb
   return RUstar, RL

# MOS STABILITY CORRECTION FUNCTIONS
def PSIma(f, g):
   a = 0.33
   b = 0.41
   pi = 3.141592654
   tangens = math.atan((2.0 * g - 1.0) / math.sqrt(3.0)) * pi /180
#   tangens = ifthenelse(tangens > pi/2.0, tangens - 2.0 * pi, tangens)
   if tangens > pi/2.0:
       tangens = tangens - 2.0 * pi
   else:
       tangens = tangens
   PSIma = math.log(a + f) - 3.0 * b * f ** (1.0 / 3.0) + b * a ** (1.0 / 3.0) / 2.0 * math.log((1 + g) ** 2.0 / (1.0 - g + g*g)) + math.sqrt(3.0) * b * a ** (1.0 / 3.0) * tangens
   return PSIma
   
def PSIm_y(Y):
   # Integrated stability correction function for momentum
   # Inputs
   # Y = -z/L, where z is the height, L the Obukhov length
   # test values
   
   # Constants (Brutsaert, 1999)
   a = 0.33
   b = 0.41
   m = 1.0
   pi= 3.141592654
   
   # Calculation
   #//HK 040902 
   Y = math.fabs(Y) #abs(Y)
   x = (Y/a) ** (1.0/3.0)
   PSI0 = math.log(a) + math.sqrt(3.0) * b * a ** (1.0 / 3.0) * pi / 6.0
   b_3 = b ** -3.0
#   PSIm_y = ifthenelse(Y <= b_3, PSIma(Y, x) + PSI0, PSIma(b_3, ((b_3/a)**(1.0/3.0))) + PSI0)
   if Y <= b_3:
       PSIm_y = PSIma(Y, x) + PSI0
   else:
       PSIm_y = PSIma(b_3, ((b_3/a)**(1.0/3.0))) + PSI0
   #PSIm_y = ifthenelse(Y <= b_3, PSIma(Y, x) + PSI0, (1.0 / (PSIma(b_3, ((b_3/a)**(1.0/3.0))))) + PSI0)
   return PSIm_y
   
def PSIh_y(Y):
   # Integrated stability correction function for heat
   # Inputs
   # Y = -z/L, z is the height, L the Obukhov length
   # constants (Brutsaert, 1999)
   c = 0.33
   d = 0.057
   n = 0.78
   # Calculation
   Y =  math.fabs(Y)
   PSIh_y = (1.0 - d) / n * math.log((c + Y ** n) / c)
   return PSIh_y

# BAS STABILITY CORRECTION FUNCTIONS
def Bw(hi, L, z0):
   # constants (Brutsaert, 1999)
   alfa = 0.12
   beta = 125.0
   
   # calculations
   B0 = (alfa / beta) * hi
   B1 = -1.0 *z0 / L
   B11 = -alfa * hi / L
   B21 = hi / (beta * z0)
   B22 = -beta * z0 / L
   tempB11 = PSIm_y(B11)
   tempB1 = PSIm_y(B1)
#   B = ifthenelse(z0 < B0, -1.0 * ln(alfa) + PSIm_y(B11) - PSIm_y(B1), ln(B21) + PSIm_y(B22) - PSIm_y(B1))
   if z0 < B0:
       B = -1.0 * math.log(alfa) + PSIm_y(B11) - PSIm_y(B1)
   else:
       B = math.log(B21) + PSIm_y(B22) - PSIm_y(B1)
#   Bw = ifthenelse(B < 0.0, 0.0, B) # This results from unfortunate parameter combination!
   if B < 0.0:
      Bw = 0.0
   else:
       Bw = B
   return Bw

def Cw(hi, L, z0, z0h):
   alfa = 0.12
   beta = 125.0
   C0 = (alfa / beta) * hi
   C1 = z0h / L
   C11 = -alfa * hi / L
   C21 = hi / (beta * z0)
   C22 = -beta * z0 / L
#   C = ifthenelse(z0 < C0, pcrumin(ln(alfa)) + PSIh_y(C11) - PSIh_y(C1), ln(C21) + PSIh_y(C22) - PSIh_y(C1))
   if z0 < C0:
       C = math.log(alfa) + PSIh_y(C11) - PSIh_y(C1)
   else:
       C = math.log(C21) + PSIh_y(C22) - PSIh_y(C1)
#   Cw = ifthenelse(C < 0.0, 0.0, C) # This results from unfortunate parameter combination!
   if C < 0.0:
       Cw = 0
   else:
       Cw = C
   return Cw

def esat(t):
   """Calculation of saturated vapour pressure [Pa]
   
   t Input temperature in degrees Celsius"""
   # constants
   e0 = 610.7   # saturated water vapour pressure at 273.15K
   A = 7.5
   B = 237.3
   
   # Calculation
   esat = e0 * 10.0 ** ((A * t) / (B + t))
   return esat


#----------------------------------------------------------------------------
# INPUT

# Validation pixel
#rowy = 0				# row number of validation pixel
#colx = 0				# column number of validation pixel
#checkFile = file("check.txt", "w")	# name of validation textfile

# Define inputs
# maps
DEM = 100
nd = 0.6
T = 30
albedo = 0.6
ems = 0.98

# parameters
root = Tkinter.Tk()
root.title("Enter SEBS model parameters:")
d = parameterDialog(root)
Trans,Lat,DOY,Time,z_pbl,alt_ms,u_s,t_s,p_s,hr_s = d.result
root.withdraw()
z_ms = alt_ms

# Define output files
#lemap = guiOutputMap('Latent Heat Flux Map','./example/le.map')
#hmap = guiOutputMap('Sensible Heat Flux Map','./example/h.map')
#gmap = guiOutputMap('Soil Heat Flux Map','./example/g0.map')
#rnmap = guiOutputMap('Net Radiation Map','./example/rn.map')
#evaprmap = guiOutputMap('Relative Evapotranspiration Map','./example/evapr.map')
#evapfrmap = guiOutputMap('Evaporative Fraction Map','./example/evapfr.map')
#etmap = guiOutputMap('Actual Evapotranspiration Map','./example/et.map')

print "Initializing SEBS.",
# Initialize model starttime for calculation runtime
starttime = time()
# Check input data
#nd = ifthenelse(pcror(pcrlt(nd,0.0),pcrgt(nd,1.0)), 1.0, nd) # Convert waterbodies to 1.0 --> soilflux is minimal
#assertWithinRange(nd, 0.0, 1.0)
assert nd >= 0.0 and nd <= 1

#assert cellvalue(mapminimum(DEM), 0, 0) >= 0.0
assert DEM >= 0.0

#assert cellvalue(mapminimum(T), 0, 0) >= 0.0
assert T >= 0.0

assert DOY >= 0.0 and DOY <= 366
assert Time >= 0.0 and Time <= 24.0
assert alt_ms >= 0.0
assert u_s >= 0.0
assert hr_s >= 0.0 and hr_s <= 1.0
assert z_pbl >= 0.0
#albedo = ifthenelse(pcror(pcrlt(albedo,0.0),pcrgt(albedo,1.0)), 0.0, albedo)
#assertWithinRange(albedo, 0.0, 1.0)
#ems = ifthenelse(pcror(pcrlt(ems,0.0), pcrgt(ems,1.0)), 0.0, ems)
#assertWithinRange(ems, 0.0, 1.0)
print "\b.",   

# INITIALIZE MODEL
# Calculating initial LAI
LAINDVI = LAINDVI(nd)
LAI = LAINDVI[0]
assert(LAI >= 0.0 and LAI <= 6.0)
print "\b.",
nd_max = LAINDVI[1]
nd_min = LAINDVI[2]
nd_mid = LAINDVI[3]
nd_df = LAINDVI[4]
print "\b.",
# Calculate initial PBL parameters
Fu_pbl = u_pbl(nd)
u_pbl = Fu_pbl[0]
u_pbl = Fu_pbl
print "u_pbl=",u_pbl
#u_pbl = cellvalue(u_pbl, 0, 0)
u_pbl = u_pbl[0]
assert u_pbl >= 0.0
print "\b.",
z0m = Fu_pbl[1]
d = Fu_pbl[2]
fc = Fu_pbl[3]
h = Fu_pbl[4]

# Calculating initial KB-1 and z0h
KB_1 = FKB_1(u_pbl, z_pbl, h, LAI, fc, t_s, p_s)
#KB_1 = cellvalue(KB_1, 0, 0)
print "KB_1=",KB_1
#KB_1 = KB_1[0]
print "\b.",
#z0h = cellvalue(z0h(KB_1, z0m), 0, 0)
z0h = z0h(KB_1, z0m)
print "z0h=",z0h
#z0h = z0h[0]
print "\b."

# Calculating initial temperatures and pressures"
t_c = math.log((z_pbl - d) / z0h) / math.log((alt_ms - d) / z0h)
t_s = t_s + 273.15
t_pbl_A = T * (1.0 - t_c) + t_s * t_c
p_s_A = p_s * ((44331.0 - DEM) / (44331.0 - alt_ms)) ** (1.0 / 0.1903)   # surface pressure
z_pbl_A = z_pbl
p_pbl_A = p_s * ((44331.0 - (DEM + z_pbl_A)) / (44331.0 - alt_ms)) ** (1.0 / 0.1903)
helpvar1= DEM/44331.0
helpvar2 = 1.0 - helpvar1
T0 = T / helpvar2 ** 1.5029
t_pbl_A = t_pbl_A / (1.0 - DEM / 44331.0) ** 1.5029
T_0pbl = 0.5 * (T0 + t_pbl_A)   # mean potential temperature
Tcn = T_0pbl - 273.15    # mean PBL temperature converted to degrees Celcius
esat = 611.0 * math.exp(17.502 * Tcn / (Tcn + 240.97))   # Pa
print "esat=",esat
hr_pbl = hr_s
#eact = hr_pbl * mean(esat) # actual vapour pressure
eact = hr_pbl * esat
q_pbl_A = 5.0 / 8.0 * eact / p_pbl_A
z_pbl = z_pbl_A
ps = p_s_A
Ta = T_0pbl - 273.15
t_pbl = t_pbl_A
LAI = math.sqrt(nd * (1.0 + nd)/ (1.0 + 1.0E-6 - nd))
#LAI = ifthenelse(LAI > 6.0, 6.0, LAI)
if LAI > 6.0:
    LAI = 6.0
assert LAI >= 0.0
fc = ((nd - nd_min) / nd_df) ** 2.0
#assertWithinRange(fc, 0.0, 1.0)
assert fc >= 0.0 and fc <= 1.0
p_pbl = p_pbl_A
q_pbl = q_pbl_A
z0m = 0.005 + 0.5 * (nd / nd_max) ** 2.5
d = z0m * 4.9
h = z0m / 0.136
KB_1 = GKB_1(u_pbl, z_pbl, h, LAI, fc, Ta, p_pbl)
z0h = z0m / math.exp(KB_1)
Tsk = T					# potential surface temperature
Theta_s = T0
Theta_v = Tsk * (1.0 + 0.61 * q_pbl)	# surface virtual temperature
#Theta_a = t_pbl				# potential air temperature at reference height (K)
Theta_a = t_pbl * (101325/p_pbl) ** 0.286
T0ta = Theta_s - Theta_a
Rv = 461.05				# specific gas constant water vapour (J kg-1 K-1)
Rd = 287.04				# specific gas constant dry air (J kg-1 K-1)
Cp = 1005.0				# specific heat (J kg-1 K-1)
eact = p_pbl * q_pbl * (Rv / Rd)	# actual vapour pressure
rhoa = ps / (Rd * Theta_v)		# surface air density (kg m-3)
rhoam = (ps / (Rd * Tsk)) * (1.0 - 0.378 * eact / ps) # moist air density (kg m-3)
rhoacp = rhoa * Cp			# specific air heat capacity (J K-1 m�3)
alfa = 0.12
beta = 125.0
g = 9.81
k = 0.4
print "alfa * z_pbl=",alfa * z_pbl,"\n"
print  "beta * z0m=",beta * z0m,"\n"
if((alfa * z_pbl) > (beta * z0m)):
    hst = alfa * z_pbl
if((alfa * z_pbl) <= (beta * z0m)):
    hst = beta * z0m
#hst = max((alfa * z_pbl), (beta * z0m)) # height of ASL (m)
zd0 = z_pbl - d
ku = k * u_pbl
zdm = math.log(zd0/z0m)
zdh = math.log(zd0/z0h)
CH = T0ta * k * rhoacp
print "rhoam=",rhoam,"\n"
#CL = pcrumin(rhoam) * Cp * Theta_v / (k * g)
CL = rhoam * Cp * Theta_v / (k * g)


# Calculate energy balance
print "Calculating Energy Balance terms..."
Rswd = Rswd(DEM, Lat, Trans, DOY, Time)
Eair = 9.2 * (t_pbl/1000.0) ** 2.0
Rn = Rn(albedo, Rswd, Eair, t_pbl, ems, T)
#report(Rn, rnmap)
print "Rn=",Rn,"\n"
G0 = G0(Rn, fc)
#report(G0,gmap)
print "G0=",G0,"\n"
R_G = Rn - G0
# Dry-limit heat flux
print "Calculating Dry Limit..."
H_d = R_G
FRUstar = FRUstar(z_pbl,  hst)
RUstar = FRUstar[0]
RL = FRUstar[1]
print "Calculating Wet Limit..."
# For completely wet areas
# Wet-limit stability length
L_e = 2.430E+06   # Latent heat of vapourization (J kg-1) (Brutsaert, 1982)
L_w = RUstar ** 3.0 * rhoam / (0.61 * k * g * R_G / L_e)
#C_wet = ifthenelse(z_pbl >= hst, Cw(z_pbl, L_w, z0m, z0h), PSIh_y(pcrumin(z_pbl/L_w)))
if z_pbl >= hst:
    C_wet = Cw(z_pbl, L_w, z0m, z0h)
else:
    C_wet = PSIh_y(z_pbl/L_w)
# Wet-limit external resistance
re_w = (zdh - C_wet) / (k * RUstar)
#re_w = ifthenelse(re_w <= 0.0, zdh / (k * RUstar), re_w)
if re_w <= 0.0:
    re_w = zdh / (k * RUstar)
else:
    re_w = re_w

# Wet-limit heat flux
slopef = 17.502 * 240.97 * esat / (Ta + 240.97) ** 2.0
gamma = 67.0   # psychrometric constant (Pa K-1)
H_w = (R_G - (rhoacp / re_w) * ((esat - eact) / gamma)) / (1.0 + slopef / gamma)
LEwet = Rn - G0 - H_w
# Sensible Heat flux
print "Calculating sensible heat flux..."
#C_i = ifthenelse(z_pbl >= hst, Cw(z_pbl, RL, z0m, z0h), PSIh_y(pcrumin(z_pbl)/RL))
if z_pbl >= hst:
    C_i = Cw(z_pbl, RL, z0m, z0h)
else:
    C_i = PSIh_y(z_pbl/RL)

# external resistance
re_i = (zdh - C_i) / (k * RUstar)
H_i = rhoacp * T0ta / re_i
#H_i = ifthenelse(H_i > H_d, H_d, H_i)
if H_i > H_d:
    H_i = H_d
else:
    H_i = H_i

#H_i = ifthenelse(H_i < H_w, H_w, H_i)
if H_i < H_w:
    H_i = H_w
else:
    H_i = H_i
    
#report(H_i, hmap)
print "H_i=",H_i,"\n"

# Calculate evaporation variables
print "Calculating relative evaporation and evaporative fraction..."
# Calculate relative evaporation
ev_r = 1.0 - (H_i - H_w) / (H_d - H_w) # set water and wet surfaces to 1.0
#report(ev_r, evaprmap)
print "ev_r=",ev_r,"\n"
# Calculate evaporative fraction
Evapfr = ev_r * (1.0 - H_w / H_d)
#report(Evapfr, evapfrmap)
print "Evapfr=",Evapfr,"\n"

# Calculate latent energy flux
print "Calculating Latent Energy Flux..."
labdaE = Evapfr * (Rn - G0)
labdaE2 = Rn - G0 - H_i
#assert(labdaE == labdaE2) # Check on closure of energy balance components!
#report(labdaE, lemap)
print "labdaE=",labdaE,"\n"

# Calculate evapotranspiration flux
print "Calculating Evapotranspiration Flux..."
rhow = 998.0 # density of water [kg m-3]
E = labdaE / (L_e * rhow) #[m/s]
#report(E, etmap)
print "E=",E,"\n"

#Ehour = E * 3600.0 * 100.0 # cm/h for data assimilation with sm model
#report(Ehour, "ehour_aster90.map")
#checkFile.close()
endtime = time()
deltaTime = endtime - starttime
print
print "============================================="
print "The model has been running for %5.2f seconds." % deltaTime
print
print "Credits:"
print "Bob Su (ITC)"
print "Ambro Gieske (ITC)"
print "Wim Timmermans (ITC)"
print "Victor Jetten (UU)"
print "Steven de Jong (UU)"
print "Li Jia (WUR)"
print "Kor de Jong (UU)"
print "Derek Karssenberg (UU)"
print "============================================="



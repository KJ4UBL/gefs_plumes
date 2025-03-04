#!/bin/usr/env python
import pygrib
import csv
import datetime
import ncepy
import numpy as np
import matplotlib
import math
import subprocess
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import interpolate
import sys
ymdh = str(sys.argv[1])
# ymdh='2021091800'     # Temporary manual date setting

slist=[]
slats=[]
slons=[]
with open('gfsxstations.txt','r') as f:
  for row in f:
    x=row.split(',')
    slist.append(x[0])
    slats.append(float(x[1]))
    slons.append(float(x[2]))
members=['time','date','c00','p01','p02','p03','p04','p05','p06','p07','p08','p09','p10','p11','p12','p13','p14','p15','p16','p17','p18','p19','p20','p21','p22','p23','p24','p25','p26','p27','p28','p29','p30','GFS']
fhours=[]
preciptotal=[]
amount=1.0
fhour=60
closest=0  #starting range of forecast hour
# furthest=195 #3 hours more than the actual ending forecast hour you want
furthest=63
ymd=ymdh[0:8]
year=int(ymdh[0:4])
month=int(ymdh[4:6])
day=int(ymdh[6:8])
hour=int(ymdh[8:10])
print(year, month , day, hour)
dtime=datetime.datetime(year,month,day,hour,0)
date_list = [dtime + datetime.timedelta(hours=x) for x in range(closest,furthest,3)]
firstdate=dtime - datetime.timedelta(hours=fhour)
fhours1=list(range(closest,furthest,3))
nmbtotal=np.empty((len(slist),len(fhours1),len(members)+1),dtype='object')
print(nmbtotal.shape)
for i in range(len(members)):
  print(members[i])
  ptotal=0
  for j in range(len(fhours1)):
    if i==0:
      nmbtotal[:,j,i]=fhours1[j]
    elif i==1:
      nmbtotal[:,j,i]=date_list[j].strftime("%m-%d-%Y:%H")
    elif i>1 and members[i]!='GFS':
      # grbs = pygrib.open('/gpfs/dell4/nco/ops/com/gefs/prod/gefs.'+str(ymd)+'/'+str(hour).zfill(2)+'/atmos/pgrb2bp5/ge'+members[i]+'.t'+str(hour).zfill(2)+'z.pgrb2b.0p50.f'+str(fhours1[j]).zfill(3))
      grbs = pygrib.open('/home/gefs/gefs/model_data/gefs/gefs.'+str(ymd)+'/'+str(hour).zfill(2)+'/atmos/pgrb2ap5/ge'+members[i]+'.t'+str(hour).zfill(2)+'z.pgrb2a.0p50.f'+str(fhours1[j]).zfill(3))
      # grbind = pygrib.index('/gpfs/dell4/nco/ops/com/gefs/prod/gefs.'+str(ymd)+'/'+str(hour).zfill(2)+'/atmos/pgrb2bp5/ge'+members[i]+'.t'+str(hour).zfill(2)+'z.pgrb2b.0p50.f'+str(fhours1[j]).zfill(3),'name')
      grbind = pygrib.index('/home/gefs/gefs/model_data/gefs/gefs.'+str(ymd)+'/'+str(hour).zfill(2)+'/atmos/pgrb2bp5/ge'+members[i]+'.t'+str(hour).zfill(2)+'z.pgrb2b.0p50.f'+str(fhours1[j]).zfill(3),'name')
     
      #for grb in grbs:
      precip=(grbind.select(name='MSLP (Eta model reduction)')[0].values/100.)
      precip=np.asarray(precip[::-1,:])
      lats,lons = grbind.select(name='2 metre dewpoint temperature')[0].latlons()
      latlist=lats[::-1,0]
      lonlist=lons[0,:]
      lonlist=np.asarray(lonlist)
      latlist=np.asarray(latlist)
      f=interpolate.interp2d(lonlist,latlist,precip,kind='linear')
      for k in range(len(slats)):
        znew=np.round(f((360+slons[k]),slats[k]),3)
        nmbtotal[k,j,i]=znew
    else:
      # grbind = pygrib.index('/gpfs/dell1/nco/ops/com/gfs/prod/gfs.'+str(ymd)+'/'+str(hour).zfill(2)+'/atmos/gfs.t'+str(hour).zfill(2)+'z.pgrb2.0p50.f'+str(fhours1[j]).zfill(3),'name')
      grbind = pygrib.index('/home/gefs/gefs/model_data/gfs/gfs.'+str(ymd)+'/'+str(hour).zfill(2)+'/atmos/gfs.t'+str(hour).zfill(2)+'z.pgrb2.0p50.f'+str(fhours1[j]).zfill(3),'name')
      #for grb in grbs:
      precip=(grbind.select(name='MSLP (Eta model reduction)')[0].values/100.)
      precip=np.asarray(precip[::-1,:])
      lats,lons = grbind.select(name='2 metre dewpoint temperature')[0].latlons()
      latlist=lats[::-1,0]
      lonlist=lons[0,:]
      lonlist=np.asarray(lonlist)
      latlist=np.asarray(latlist)
      f=interpolate.interp2d(lonlist,latlist,precip,kind='linear')
      for k in range(len(slats)):
        znew=np.round(f((360+slons[k]),slats[k]),3)
        nmbtotal[k,j,34]=znew
for k in range(len(slats)):
  for j in range(len(fhours1)):
    nmbtotal[k,j,33]=np.round(np.sum(nmbtotal[k,j,2:33])/31.0,3)
for k in range(len(slats)):
  f = open("GEFS"+slist[k]+ymdh+"slp.csv","wt")
  try:
    writer = csv.writer(f)
    writer.writerow(('time','date','c0','p1','p2','p3','p4','p5','p6','p7','p8','p9','p10','p11','p12','p13','p14','p15','p16','p17','p18','p19','p20','p21','p22','p23','p24','p25','p26','p27','p28','p29','p30','mean','GFS'))
    for i in range(nmbtotal.shape[1]):
      writer.writerow((str(m).replace("[","")).replace("]","") for m in nmbtotal[k,i,:])
  finally:
    f.close()

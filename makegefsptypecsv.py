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

def find_nearest(array,value):
  idx=(np.abs(array-value)).argmin()
  return idx
slist=[]
slats=[]
slons=[]
with open('gfsxstations.txt','r') as f:
  for row in f:
    x=row.split(',')
    slist.append(x[0])
    slats.append(float(x[1]))
    slons.append(float(x[2]))
members=['time','date','c00','p01','p02','p03','p04','p05','p06','p07','p08','p09','p10','p11','p12','p13','p14','p15','p16','p17','p18','p19','p20','p21','p22','p23','p24','p25','p26','p27','p28','p29','p30']
type=['rain','snow','freezing rain','ice pellets']
membertype=['time','date','rain','snow','freezing rain','ice pellets']
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
lastcycle=dtime - datetime.timedelta(hours=6)
lastymd=lastcycle.strftime("%Y%m%d")
lasthour=lastcycle.strftime("%H")
fhours1=list(range(closest,furthest,3))
nmbtotal=np.empty((len(slist),len(fhours1),len(membertype)),dtype='object')
nmbrain=np.empty((len(slist),len(fhours1),len(members)+1),dtype='object')
nmbsnow=np.empty((len(slist),len(fhours1),len(members)+1),dtype='object')
nmbfreezing=np.empty((len(slist),len(fhours1),len(members)+1),dtype='object')
nmbice=np.empty((len(slist),len(fhours1),len(members)+1),dtype='object')
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
      if j==0:
        # grbindprev = pygrib.index('/gpfs/dell4/nco/ops/com/gefs/prod/gefs.'+str(lastymd)+'/'+str(lasthour).zfill(2)+'/atmos/pgrb2ap5/ge'+members[i]+'.t'+str(lasthour).zfill(2)+'z.pgrb2a.0p50.f003','name')
        # grbind = pygrib.index('/gpfs/dell4/nco/ops/com/gefs/prod/gefs.'+str(lastymd)+'/'+str(lasthour).zfill(2)+'/atmos/pgrb2ap5/ge'+members[i]+'.t'+str(lasthour).zfill(2)+'z.pgrb2a.0p50.f006','name')
        grbindprev = pygrib.index('/home/gefs/gefs/model_data/gefs/gefs.'+str(lastymd)+'/'+str(lasthour).zfill(2)+'/atmos/pgrb2ap5/ge'+members[i]+'.t'+str(lasthour).zfill(2)+'z.pgrb2a.0p50.f003','name')
        grbind = pygrib.index('/home/gefs/gefs/model_data/gefs/gefs.'+str(lastymd)+'/'+str(lasthour).zfill(2)+'/atmos/pgrb2ap5/ge'+members[i]+'.t'+str(lasthour).zfill(2)+'z.pgrb2a.0p50.f006','name')
        precipnewc=grbind.select(name='Total Precipitation')[0].values*.03937
        precipnewp=grbindprev.select(name='Total Precipitation')[0].values*.03937
        catrain=grbind.select(name='Categorical rain')[0].values
        catsnow=grbind.select(name='Categorical snow')[0].values
        catfreezing=grbind.select(name='Categorical freezing rain')[0].values
        catice=grbind.select(name='Categorical ice pellets')[0].values
        precipnewc=np.asarray(precipnewc[::-1,:])
        precipnewp=np.asarray(precipnewp[::-1,:])
        catrain=np.asarray(catrain[::-1,:])
        catsnow=np.asarray(catsnow[::-1,:])
        catfreezing=np.asarray(catfreezing[::-1,:])
        catice=np.asarray(catice[::-1,:])

        precip=precipnewc-precipnewp
        
        # grbs = pygrib.open('/gpfs/dell4/nco/ops/com/gefs/prod/gefs.'+str(lastymd)+'/'+str(lasthour).zfill(2)+'/atmos/pgrb2ap5/ge'+members[i]+'.t'+str(lasthour).zfill(2)+'z.pgrb2a.0p50.f003')
        grbs = pygrib.open('/home/gefs/gefs/model_data/gefs/gefs.'+str(lastymd)+'/'+str(lasthour).zfill(2)+'/atmos/pgrb2ap5/ge'+members[i]+'.t'+str(lasthour).zfill(2)+'z.pgrb2a.0p50.f003')
      elif (j%2)!=0:
        # grbind = pygrib.index('/gpfs/dell4/nco/ops/com/gefs/prod/gefs.'+str(ymd)+'/'+str(hour).zfill(2)+'/atmos/pgrb2ap5/ge'+members[i]+'.t'+str(hour).zfill(2)+'z.pgrb2a.0p50.f'+str(fhours1[j]).zfill(3),'name')
        grbind = pygrib.index('/home/gefs/gefs/model_data/gefs/gefs.'+str(ymd)+'/'+str(hour).zfill(2)+'/atmos/pgrb2ap5/ge'+members[i]+'.t'+str(hour).zfill(2)+'z.pgrb2a.0p50.f'+str(fhours1[j]).zfill(3),'name')
        precip=grbind.select(name='Total Precipitation')[0].values*.03937
        catrain=grbind.select(name='Categorical rain')[0].values
        catsnow=grbind.select(name='Categorical snow')[0].values
        catfreezing=grbind.select(name='Categorical freezing rain')[0].values
        catice=grbind.select(name='Categorical ice pellets')[0].values
        precip=np.asarray(precip[::-1,:])
        catrain=np.asarray(catrain[::-1,:])
        catsnow=np.asarray(catsnow[::-1,:])
        catfreezing=np.asarray(catfreezing[::-1,:])
        catice=np.asarray(catice[::-1,:])
      else:
        # grbindprev = pygrib.index('/gpfs/dell4/nco/ops/com/gefs/prod/gefs.'+str(ymd)+'/'+str(hour).zfill(2)+'/atmos/pgrb2ap5/ge'+members[i]+'.t'+str(hour).zfill(2)+'z.pgrb2a.0p50.f'+str(fhours1[j-1]).zfill(3),'name')
        # grbind = pygrib.index('/gpfs/dell4/nco/ops/com/gefs/prod/gefs.'+str(ymd)+'/'+str(hour).zfill(2)+'/atmos/pgrb2ap5/ge'+members[i]+'.t'+str(hour).zfill(2)+'z.pgrb2a.0p50.f'+str(fhours1[j]).zfill(3),'name')
        grbindprev = pygrib.index('/home/gefs/gefs/model_data/gefs/gefs.'+str(ymd)+'/'+str(hour).zfill(2)+'/atmos/pgrb2ap5/ge'+members[i]+'.t'+str(hour).zfill(2)+'z.pgrb2a.0p50.f'+str(fhours1[j-1]).zfill(3),'name')
        grbind = pygrib.index('/home/gefs/gefs/model_data/gefs/gefs.'+str(ymd)+'/'+str(hour).zfill(2)+'/atmos/pgrb2ap5/ge'+members[i]+'.t'+str(hour).zfill(2)+'z.pgrb2a.0p50.f'+str(fhours1[j]).zfill(3),'name')
        precipnewc=grbind.select(name='Total Precipitation')[0].values*.03937
        precipnewp=grbindprev.select(name='Total Precipitation')[0].values*.03937
        catrain=grbind.select(name='Categorical rain')[0].values
        catsnow=grbind.select(name='Categorical snow')[0].values
        catfreezing=grbind.select(name='Categorical freezing rain')[0].values
        catice=grbind.select(name='Categorical ice pellets')[0].values
        precipnewc=np.asarray(precipnewc[::-1,:])
        precipnewp=np.asarray(precipnewp[::-1,:])
        catrain=np.asarray(catrain[::-1,:])
        catsnow=np.asarray(catsnow[::-1,:])
        catfreezing=np.asarray(catfreezing[::-1,:])
        catice=np.asarray(catice[::-1,:])

        precip=precipnewc-precipnewp
      lats,lons = grbs[31].latlons()
      latlist=lats[::-1,0]
      lonlist=lons[0,:]
      lonlist=np.asarray(lonlist)
      latlist=np.asarray(latlist)
      for k in range(len(slats)):
        nearestlat=find_nearest(latlist,slats[k])
        nearestlon=find_nearest(lonlist,slons[k]+360)
        thisprecip=precip[nearestlat,nearestlon]
        if thisprecip>0.01:
          thisrain=catrain[nearestlat,nearestlon]
          thissnow=catsnow[nearestlat,nearestlon]
          thisice=catice[nearestlat,nearestlon]
          thisfreezing=catfreezing[nearestlat,nearestlon]
          if thisrain==1:
            nmbrain[k,j,i]=1
          elif thissnow==1:
            nmbsnow[k,j,i]=1
          elif thisfreezing==1:
            nmbfreezing[k,j,i]=1
          elif thisice==1:
            nmbice[k,j,i]=1
for k in range(len(slats)):
  for j in range(len(fhours1)):
    nmbtotal[k,j,2]= np.round((np.sum([x for x in nmbrain[k,j,:] if x != None])/31.0)*100,1)
    nmbtotal[k,j,3]= np.round((np.sum([x for x in nmbsnow[k,j,:] if x != None])/31.0)*100,1)
    nmbtotal[k,j,4]= np.round((np.sum([x for x in nmbfreezing[k,j,:] if x != None])/31.0)*100,1)
    nmbtotal[k,j,5]= np.round((np.sum([x for x in nmbice[k,j,:] if x != None])/31.0)*100,1)
          

for k in range(len(slats)):
  f = open("GEFS"+slist[k]+ymdh+"ptype.csv","wt")
  try:
    writer = csv.writer(f)
    writer.writerow(('time','date','rain','snow','freezing rain','ice pellets'))
    for i in range(nmbtotal.shape[1]):
      writer.writerow((str(m).replace("[","")).replace("]","") for m in nmbtotal[k,i,:])
  finally:
    f.close()

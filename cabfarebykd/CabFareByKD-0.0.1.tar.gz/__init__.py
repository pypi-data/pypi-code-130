#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
from datetime import datetime
from datetime import time
from geopy.geocoders import Nominatim
from sklearn.linear_model import LinearRegression
import sklearn

journeys=pd.read_csv('journeys.csv')
journeys=journeys.astype({'Trip Created At Local Time':'datetime64[ns]'})
journeys=journeys.astype({'Trip Start At Local Time':'datetime64[ns]'})
journeys=journeys.astype({'Trip End At Local Time':'datetime64[ns]'})
journeys['Trip Sum Trip Price']=journeys['Trip Sum Trip Price'].replace('[\$,]','',regex=True).astype(float)
journeys=journeys.iloc[:,3:]

cityLatLong=pd.read_csv('uscities.csv')

data=journeys.merge(cityLatLong, how='inner', left_on='Car Parking Address City', right_on='city').drop(columns=['Car Parking Address City','city'])

x=pd.DataFrame(data.iloc[:,[4,5]])
y=(data.iloc[:,3])

x['Duration']=(data['Trip End At Local Time']-data['Trip Start At Local Time']).dt.total_seconds()/3600
x['Day']=data['Trip Created At Local Time'].dt.day_name()

x['Period']='Morning'
x.loc[data['Trip Created At Local Time'].dt.time>time(12,0,0),'Period']='Afternoon'
x.loc[data['Trip Created At Local Time'].dt.time>time(17,0,0),'Period']='Evening'
x.loc[data['Trip Created At Local Time'].dt.time>time(20,0,0),'Period']='Night'

x.loc[(x['Day'].isin(['Monday','Tuesday','Wednesday','Thursday','Friday'])),'Day']='Weekday'
x.loc[~(x['Day'].isin(['Monday','Tuesday','Wednesday','Thursday','Friday','Weekday'])),'Day']='Weekend'

x=pd.concat([x,pd.get_dummies(x['Day'])],axis=1).drop(columns=['Day'])
x=pd.concat([x,pd.get_dummies(x['Period'])],axis=1).drop(columns=['Period'])

from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(x,y,test_size=0.20, random_state=2303)

#building linear regression model
lr=LinearRegression()
lr.fit(x_train,y_train)
y_pred=lr.predict(x_test)

def CabFare(city, sTime, sDate, duration):
    geolocator = Nominatim(user_agent='myapplication')
    location = geolocator.geocode(city)
    
    lat=location.latitude
    lng=location.longitude
    
    day=datetime.strptime('2022-08-14', '%Y-%m-%d').date().strftime("%A")    
    
    if day in ['Monday','Tuesday','Wednesday','Thursday','Friday']:
        Weekday=1
        Weekend=0
    else:
        Weekday=0
        Weekend=1
    
    stime=datetime.strptime(sTime, '%H:%M:%S').time()
    if stime>time(12,0,0):
        Afternoon=1
        Evening=0
        Morning=0
        Night=0
    elif stime>time(17,0,0):
        Afternoon=0
        Evening=1
        Morning=0
        Night=0
    elif stime>time(20,0,0):
        Afternoon=0
        Evening=0
        Morning=0
        Night=1
    else:
        Afternoon=0
        Evening=0
        Morning=1
        Night=0
        
    ride=pd.DataFrame({'lat':[lat],'lng':[lng],'Duration':[duration],'Weekday':[Weekday],'Weekend':[Weekend],'Afternoon':[Afternoon],'Evening':[Evening],'Morning':[Morning],'Night':[Night]})
    return('Journey Price: '+str(round(lr.predict(ride)[0],2)))


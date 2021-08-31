# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import builtins
import re

from modin.pandas import dataframe
from app.home import blueprint
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound
import requests
import json
import modin.pandas as pd
from app.home.api_utils import api_to_dataframe
from flask_googlemaps import GoogleMaps, Map
import ast
import pytz
import datetime

devices_data = {} # dict to store data of devices
devices_location = {} # dict to store coordinates of devices

class API:

    devices = None

    def __init__(self, df=None, uuid='all', datefrom='all', dateto='all', freq='D', sensor=None, measure=None, metric=None):
        self.mob_address_uuid = f'http://127.0.0.1:12345/mobility/{uuid}/{datefrom}/{dateto}/{freq}'
        self.sens_address_uuid = f'http://127.0.0.1:12345/sensor/{df}/{uuid}/{datefrom}/{dateto}/{freq}/{measure}/{metric}'
        self.devices = f'http://127.0.0.1:12345/devices'

def pull_data(uuid, datefrom, dateto, freq):
    
    api = API(uuid=uuid, datefrom=datefrom, dateto=dateto, freq=freq)
    response = requests.get(api.mob_address_uuid)
    mobility_data = response.json()['mobility']
    df = pd.read_json(mobility_data)

    bicycle = df.loc[df['classification'] == 'bicycle'].drop(columns='classification')
    bus = df.loc[df['classification'] == 'bus'].drop(columns='classification')
    car = df.loc[df['classification'] == 'car'].drop(columns='classification')
    motorbike = df.loc[df['classification'] == 'motorbike'].drop(columns='classification')
    person = df.loc[df['classification'] == 'person'].drop(columns='classification')
    truck = df.loc[df['classification'] == 'truck'].drop(columns='classification')

    mobility = {'bicycle' : bicycle, 'bus' : bus, 'car' : car, 'motorbike' : motorbike, 'person' : person, 'truck' : truck}

    api = API(uuid=uuid, df='sps', datefrom=datefrom, dateto=dateto, measure='pm2_5', metric='mean', freq=freq)
    response = requests.get(api.sens_address_uuid)
    pm2_5_mean = ast.literal_eval(response.json()['sensors'])
    pm2_5_mean = list(pm2_5_mean["mean"].values())

    api = API(uuid=uuid, df='sps', datefrom=datefrom, dateto=dateto, measure='pm2_5', metric='minimum', freq=freq)
    response = requests.get(api.sens_address_uuid)
    pm2_5_min = ast.literal_eval(response.json()['sensors'])
    pm2_5_min = list(pm2_5_min["min"].values())

    api = API(uuid=uuid, df='sps', datefrom=datefrom, dateto=dateto, measure='pm2_5', metric='maximum', freq=freq)
    response = requests.get(api.sens_address_uuid)
    pm2_5_max = ast.literal_eval(response.json()['sensors'])
    pm2_5_max = list(pm2_5_max["max"].values())

    api = API(uuid=uuid, df='sps', datefrom=datefrom, dateto=dateto, measure='pm10', metric='mean', freq=freq)
    response = requests.get(api.sens_address_uuid)
    pm10_mean = ast.literal_eval(response.json()['sensors'])
    pm10_mean = list(pm10_mean["mean"].values())

    api = API(uuid=uuid, df='sps', datefrom=datefrom, dateto=dateto, measure='pm10', metric='minimum', freq=freq)
    response = requests.get(api.sens_address_uuid)
    pm10_min = ast.literal_eval(response.json()['sensors'])
    pm10_min = list(pm10_min["min"].values())

    api = API(uuid=uuid, df='sps', datefrom=datefrom, dateto=dateto, measure='pm10', metric='maximum', freq=freq)
    response = requests.get(api.sens_address_uuid)
    pm10_max = ast.literal_eval(response.json()['sensors'])
    pm10_max = list(pm10_max["max"].values())

    sensors = {'pm2_5_mean' : pm2_5_mean, 'pm2_5_min' : pm2_5_min, 'pm2_5_max' : pm2_5_max, 'pm10_mean' : pm10_mean, 'pm10_min' : pm10_min, 'pm10_max' : pm10_max}

    api = API()
    response = requests.get(api.devices)
    devices = response.json()


    return mobility, sensors, devices

def render(mobility, sensors, devices):

    api = API()
    response = requests.get(api.devices)
    devices = response.json()
    df = pd.DataFrame(json.loads(devices['devices'])).reset_index()
    devices = pd.DataFrame(df.uuid.values, index=df.device_name).to_dict()[0]
    devices["All"] = "all"
    device_locations = devices
    df_lat_long = pd.DataFrame(df[['device_name', 'lat', 'long']])
    lat_long_list = df_lat_long.values.tolist()


    #print(sensors['pm10_min'])
    raw_date_range = mobility['bicycle']["datetime"].values.tolist()
    date_range = []
    for x in raw_date_range:
        print(x)
        x = x/1000000000
        x = datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S')
        date_range.append(x)

    

        '''
        utc_datetime = datetime.datetime(x, tzinfo=datetime.timezone.utc)
        local_timezone = pytz.timezone("GB")
        local_datetime = utc_datetime.replace(tzinfo=pytz.utc)
        local_datetime = local_datetime.astimezone(local_timezone)
        date_range.append(local_datetime)
        '''

    return render_template('index.html', segment='index', bicycle=mobility['bicycle'], bus=mobility['bus'], car=mobility['car'], motorbike=mobility['motorbike'], 
    person=mobility['person'], truck=mobility['truck'], device_locations=device_locations, pm2_5_mean=sensors['pm2_5_mean'], pm2_5_min=sensors['pm2_5_min'], 
    pm2_5_max=sensors['pm2_5_max'], pm10_mean=sensors['pm10_mean'], pm10_min=sensors['pm10_min'], pm10_max=sensors['pm10_max'], date_range=date_range, lat_long_list=lat_long_list)



@blueprint.route('/index')
@login_required
def index():

    mobility, sensors, devices = pull_data(uuid='all', datefrom='24-08-2021', dateto='26-08-2021', freq='H')

    return render(mobility, sensors, devices)



@blueprint.route('/filter_by_device', methods=['GET', 'POST'])
@login_required
def date_post():

    api = API()
    response = requests.get(api.devices)
    devices = response.json()
    df = pd.DataFrame(json.loads(devices['devices'])).reset_index()
    API.devices = pd.DataFrame(df.uuid.values, index=df.device_name).to_dict()[0]
    API.devices["All"] = "all"
    print(API.devices)
    dates = request.form['dates']
    uuid = request.form['uuid']
    uuid = API.devices[uuid]
    print("Dates + UUID", dates, uuid)
    
    datefrom, dateto = dates.split('-')
    datefrom = datefrom.strip()
    dateto = dateto.strip()
    dt_datefrom = datetime.datetime.strptime(datefrom, '%d/%m/%Y')
    dt_dateto = datetime.datetime.strptime(dateto, '%d/%m/%Y')
    print ("_____________", datefrom, dateto)
    if str(dt_datefrom) == str(dt_dateto):
        dateto = str(dt_dateto + datetime.timedelta(days=1))
    print ("_____________", datefrom, dateto)
    datefrom = datefrom.strip().replace("/", "-")
    dateto = dateto.strip().replace("/", "-")

    mobility, sensors, devices = pull_data(uuid=uuid, datefrom=datefrom, dateto=dateto, freq='H')
    
    return render(mobility, sensors, devices)

        



@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith( '.html' ):
            template += '.html'

        # Detect the current page
        segment = get_segment( request )

        # Serve the file (if exists) from app/templates/FILE.html
        return render_template( template, segment=segment )

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500

# Helper - Extract current page name from request 
def get_segment( request ): 

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment    

    except:
        return None  

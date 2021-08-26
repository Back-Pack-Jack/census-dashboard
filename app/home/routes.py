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


class API:

    devices = None

    def __init__(self, df=None, uuid='all', datefrom='all', dateto='all', freq='D', sensor=None, measure=None, metric=None):
        self.mob_address_uuid = f'http://127.0.0.1:12345/mobility/{uuid}/{datefrom}/{dateto}/{freq}'
        self.sens_address_uuid = f'http://127.0.0.1:12345/sensor/{df}/{uuid}/{datefrom}/{dateto}/{freq}/{measure}/{metric}'
        self.devices = f'http://127.0.0.1:12345/devices'

def pull_data(uuid, datefrom, dateto, freq):
    api = API(datefrom=datefrom, dateto=dateto, freq=freq)
    response = requests.get(api.mob_address_uuid)
    mobility_data = response.json()
    mobility_data = mobility_data['mobility']
    df = pd.read_json(mobility_data)

    bicycle = df.loc[df['classification'] == 'bicycle'].drop(columns='classification')
    bus = df.loc[df['classification'] == 'bus'].drop(columns='classification')
    car = df.loc[df['classification'] == 'car'].drop(columns='classification')
    motorbike = df.loc[df['classification'] == 'motorbike'].drop(columns='classification')
    person = df.loc[df['classification'] == 'person'].drop(columns='classification')
    truck = df.loc[df['classification'] == 'truck'].drop(columns='classification')

    mobility = {'bicycle' : bicycle, 'bus' : bus, 'car' : car, 'motorbike' : motorbike, 'person' : person, 'truck' : truck}

    api = API(df='sps', datefrom=datefrom, dateto=dateto, measure='pm2_5', metric='mean', freq=freq)
    response = requests.get(api.sens_address_uuid)
    pm2_5_mean = response.json()
    api = API(df='sps', datefrom=datefrom, dateto=dateto, measure='pm2_5', metric='minimum', freq=freq)
    response = requests.get(api.sens_address_uuid)
    pm2_5_min = response.json()
    api = API(df='sps', datefrom=datefrom, dateto=dateto, measure='pm2_5', metric='maximum', freq=freq)
    response = requests.get(api.sens_address_uuid)
    pm2_5_max = response.json()
    api = API(df='sps', datefrom=datefrom, dateto=dateto, measure='pm10', metric='mean', freq=freq)
    response = requests.get(api.sens_address_uuid)
    pm10_mean = response.json()
    api = API(df='sps', datefrom=datefrom, dateto=dateto, measure='pm10', metric='minimum', freq=freq)
    response = requests.get(api.sens_address_uuid)
    pm10_min = response.json()
    api = API(df='sps', datefrom=datefrom, dateto=dateto, measure='pm10', metric='maximum', freq=freq)
    response = requests.get(api.sens_address_uuid)
    pm10_max = response.json()

    sensors = {'pm2_5_mean' : pm2_5_mean, 'pm2_5_min' : pm2_5_min, 'pm2_5_max' : pm2_5_max, 'pm10_mean' : pm10_mean, 'pm10_min' : pm10_min, 'pm10_max' : pm10_max}

    api = API()
    response = requests.get(api.devices)
    devices = response.json()


    return mobility, sensors, devices

@blueprint.route('/index')
@login_required
def index():

    mobility, sensors, devices = pull_data(uuid='all', datefrom='24-08-2021', dateto='26-08-2021', freq='H')

    print(sensors['pm10_max'])

    
    api = API()
    response = requests.get(api.devices)
    devices = response.json()
    
    df = pd.DataFrame(json.loads(devices['devices'])).reset_index()
    API.devices = pd.DataFrame(df.uuid.values, index=df.device_name).to_dict()[0]
    device_locations = API.devices.keys()
    print(device_locations)
    
    return render_template('index.html', segment='index', bicycle=mobility['bicycle'], bus=mobility['bus'], car=mobility['car'], motorbike=mobility['motorbike'], person=mobility['person'], truck=mobility['truck'], device_locations=device_locations, pm2_5_mean=sensors['pm2_5_mean'], pm2_5_min=sensors['pm2_5_min'], pm2_5_max=sensors['pm2_5_max'], pm10_mean=sensors['pm10_mean'], pm10_min=sensors['pm10_min'], pm10_max=sensors['pm10_max'])



@blueprint.route('/filter_by_device', methods=['GET', 'POST'])
@login_required
def date_post():
    dates = request.form['dates']
    uuid = request.form['uuid']
    uuid = API.devices[uuid]
    print("Dates + UUID", dates, uuid)
    
    datefrom, dateto = dates.split('-')
    datefrom = datefrom.strip().replace("/", "-")
    dateto = dateto.strip().replace("/", "-")

    api = API(datefrom=datefrom, dateto=dateto, uuid=uuid)

    response = requests.get(api.mob_address_uuid)
    mobility_data = response.json()
    mobility_data = mobility_data['mobility']
    mobility_data = api_to_dataframe(mobility_data, 0)
    bicycle = mobility_data['bicycle']
    bus = mobility_data['bus']
    car = mobility_data['car']
    motorbike = mobility_data['motorbike']
    person = mobility_data['person']
    truck = mobility_data['truck']

    response = requests.get(api.sens_address_uuid)
    sensor_data = response.json()
    sps = sensor_data['sps']
    sps = api_to_dataframe(sps, 1)
    mics = sensor_data['mics']
    mics = api_to_dataframe(mics, 1)
    zmod = sensor_data['zmod']
    zmod = api_to_dataframe(zmod, 1)
    
    return render_template('index.html', segment='index', bicycle=bicycle, bus=bus, car=car, motorbike=motorbike, person=person, truck=truck, sps=sps, mics=mics, zmod=zmod, device_locations=device_locations)

        



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

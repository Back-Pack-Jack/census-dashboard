import modin.pandas as pd
import json

def api_to_dataframe(data, mode):
    '''
    mode (0 mobility data)
    mode (1 sensor data)
    '''
    dfs = {}
    for key in data.keys():
        response = json.loads(data[key])
        df = pd.DataFrame.from_dict(response, orient="columns")
        if mode == 0:
            df = df.drop(columns='classification')
            try:
                df = df.drop(columns='uuid')
            except Exception:
                print('all values')
            df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
            df['datetime'] = df.datetime.apply(lambda x: x.strftime('%Y-%m-%d %H:%M'))
            df['count'] = df['count'].astype(int)
        if mode == 1:
            df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
            df['datetime'] = df.datetime.apply(lambda x: x.strftime('%Y-%m-%d %H:%M'))
        dfs[key] = df
    return dfs
    
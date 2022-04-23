import pandas as pd
import numpy as np
import json
import os


### DI-Connect-Wellness Files ###

# _wellnessActivities.json'
def build_health_snapshot_data(file_name):
    """
    Take in ...wellnessActivities.json file and output pandas

    Input:
        file_name | str
            _wellnessActivities file
    Output
        health_snap_pd | pdf
            pandas dataframe of healthsnap shots
    """

    with open(file_name) as file:
        j = json.load(file)

    name = []
    start = []
    end = []
    day_type = []

    # These are must-have feautres for snapshot to count
    for i in range(len(j)):
        sesh = j[i]
        name.append(sesh['activityName'])
        start.append(sesh['startTimestampLocal'])
        end.append(sesh['endTimestampLocal'])
        day_type.append(sesh['snapshotTimeOfDayType'])

    health_snap_pd = pd.DataFrame({"name":name,"start_time":start,"end_time":end,"time_of_day":day_type})

    health_snap_pd['hr_min'] = np.nan
    health_snap_pd['hr_max'] = np.nan
    health_snap_pd['hr_avg'] = np.nan

    health_snap_pd['resp_min'] = np.nan
    health_snap_pd['resp_max'] = np.nan
    health_snap_pd['resp_avg'] = np.nan

    health_snap_pd['stress_min'] = np.nan
    health_snap_pd['stress_max'] = np.nan
    health_snap_pd['stress_avg'] = np.nan

    health_snap_pd['spo2_min'] = np.nan
    health_snap_pd['spo2_max'] = np.nan
    health_snap_pd['spo2_avg'] = np.nan

    health_snap_pd['hrv_rmsdd'] = np.nan
    health_snap_pd['hrv_sdnn'] = np.nan



    # There are metrics that could be dropped by snapshot
    # hence the double loop
    levs = ['minValue','maxValue','avgValue']
    for i in range(len(j)):
        for metric in j[i]['summaryTypeDataList']:
            metric_type = metric['summaryType']

            ## Why can't python have switch statements...
            if metric_type == 'HEART_RATE':
                cols = ['hr_min','hr_max','hr_avg']
            elif metric_type == 'RESPIRATION':
                cols = ['resp_min','resp_max','resp_avg']
            elif metric_type == 'STRESS':
                cols = ['stress_min','stress_max','stress_avg']
            elif metric_type == 'SPO2':
                cols = ['spo2_min','spo2_max','spo2_avg']
            elif metric_type == 'RMSSD_HRV':
                health_snap_pd.loc[i,'hrv_rmsdd'] = metric['avgValue']
                continue
            elif metric_type == 'SDRR_HRV':
                health_snap_pd.loc[i,'hrv_sdnn'] = metric['avgValue']
                continue
            else:
                raise Exception(f"Adam didn't account for {metric_type} metric in snapshot! Let him know!!")

            for lev,col in zip(levs,cols):
                health_snap_pd.loc[i,col] = metric[lev]

    return(health_snap_pd)

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

    ## Including both times because sleep data + others don't have that
    start_local = []
    end_local = []
    start_gmt = []
    end_gmt = []

    day_type = []

    # These are must-have feautres for snapshot to count
    for i in range(len(j)):
        sesh = j[i]

        name.append(sesh['activityName'])

        start_local.append(pd.Timestamp(sesh['startTimestampLocal']))
        end_local.append(pd.Timestamp(sesh['endTimestampLocal']))

        start_gmt.append(pd.Timestamp(sesh['startTimestampGMT']))
        end_gmt.append(pd.Timestamp(sesh['endTimestampGMT']))
        day_type.append(sesh['snapshotTimeOfDayType'])

    health_snap_pd = pd.DataFrame({"name":name,"timeOfDay":day_type,
                                   "localStart":start_local,"localEnd":end_local,
                                   "gmtStart":start_gmt,"gmtEnd":end_gmt})

    health_snap_pd['heartRateMin'] = np.nan
    health_snap_pd['heartRateMax'] = np.nan
    health_snap_pd['heartRateAvg'] = np.nan

    health_snap_pd['respirationMin'] = np.nan
    health_snap_pd['respirationMax'] = np.nan
    health_snap_pd['respirationAvg'] = np.nan

    health_snap_pd['stressMin'] = np.nan
    health_snap_pd['stressMax'] = np.nan
    health_snap_pd['stressAvg'] = np.nan

    health_snap_pd['spo2Min'] = np.nan
    health_snap_pd['spo2Max'] = np.nan
    health_snap_pd['spo2Avg'] = np.nan

    health_snap_pd['hrvRMSSD'] = np.nan
    health_snap_pd['hrvSDNN'] = np.nan



    # There are metrics that could be dropped by snapshot
    # hence the double loop
    levs = ['minValue','maxValue','avgValue']
    for i in range(len(j)):
        for metric in j[i]['summaryTypeDataList']:
            metric_type = metric['summaryType']

            ## Why can't python have switch statements...
            if metric_type == 'HEART_RATE':
                cols = ['heartRateMin','heartRateMax','heartRateAvg']
            elif metric_type == 'RESPIRATION':
                cols = ['respirationMin','respirationMax','respirationAvg']
            elif metric_type == 'STRESS':
                cols = ['stressMin','stressMax','stressAvg']
            elif metric_type == 'SPO2':
                cols = ['spo2Min','spo2Max','spo2Avg']
            elif metric_type == 'RMSSD_HRV':
                health_snap_pd.loc[i,'hrvRMSSD'] = metric['avgValue']
                continue
            elif metric_type == 'SDRR_HRV':
                health_snap_pd.loc[i,'hrvSDNN'] = metric['avgValue']
                continue
            else:
                raise Exception(f"Adam didn't account for {metric_type} metric in snapshot! Let him know!!")

            for lev,col in zip(levs,cols):
                health_snap_pd.loc[i,col] = metric[lev]

    return(health_snap_pd)

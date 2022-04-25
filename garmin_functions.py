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

# _sleepData.json'
def build_sleep_data(file_name):
    """
    Take in ...sleepData.json file and output pandas

    Input:
        file_name | str
            _sleepData file
    Output
        sleep_pd | pdf
            pandas dataframe of sleep data
    """

    with open(file_name) as file:
        j = json.load(file)

    # These are must-have feautres for sleep sesh to count
    sleep_start = []
    sleep_end = []
    date = []

    for i in range(len(j)):
        sesh = j[i]
        sleep_start.append(sesh['sleepStartTimestampGMT'])
        sleep_end.append(sesh['sleepEndTimestampGMT'])
        date.append(sesh['calendarDate'])

    sleep_pd = pd.DataFrame({"gmtStart":sleep_start,"gmtEnd":sleep_end,"date":date})

    # There are metrics that could be dropped by snapshot
    # hence the double loop
    sleep_pd['sleepWindowConfirmationType'] = np.nan
    sleep_pd['deepSleepSeconds'] = np.nan
    sleep_pd['lightSleepSeconds'] = np.nan
    sleep_pd['remSleepSeconds'] = np.nan
    sleep_pd['awakeSleepSeconds'] = np.nan
    sleep_pd['unmeasurableSeconds'] = np.nan
    sleep_pd['averageRespiration'] = np.nan
    sleep_pd['lowestRespiration'] = np.nan
    sleep_pd['highestRespiration'] = np.nan
    sleep_pd['retro'] = np.nan
    sleep_pd['awakeCount'] = np.nan
    sleep_pd['avgSleepStress'] = np.nan

    sleep_pd['overallScore'] = np.nan
    sleep_pd['qualityScore'] = np.nan
    sleep_pd['durationScore'] = np.nan
    sleep_pd['recoveryScore'] = np.nan
    sleep_pd['deepScore'] = np.nan
    sleep_pd['lightScore'] = np.nan
    sleep_pd['awakeningsCountScore'] = np.nan
    sleep_pd['awakeTimeScore'] = np.nan
    sleep_pd['combinedAwakeScore'] = np.nan
    sleep_pd['restfulnessScore'] = np.nan
    sleep_pd['feedback'] = np.nan
    sleep_pd['insight'] = np.nan

    for i in range(len(j)):
        sesh = j[i]
        for key, value in sesh.items():
            # Already good
            if key in ['sleepStartTimestampGMT','sleepEndTimestampGMT','calendarDate']:
                continue
            # Sleep Scores
            elif key == 'sleepScores':
                for sleep_key, score in sesh[key].items():
                    sleep_pd.loc[i,sleep_key] = score
            elif key in sleep_pd.columns:
                sleep_pd.loc[i,key] = value
            else:
                raise Exception(f"Adam didn't account for {key} metric in snapshot! Let him know!!")


    # Rename bc I hate this column phrasing
    sleep_pd = sleep_pd.rename(columns= {"averageRespiration":"respirationAvg",
                                "lowestRespiration":"respirationMin",
                                "highestRespiration":"respirationMax"})
    return(sleep_pd)

### DI-Connect-Fitness Files ###

# summarizedActivities.json
def build_activity_summary_data(file_name):
    """
        Take in ...summarizedActivities.json file and output pandas
        IT IS possible to return empty pdfs, since optional to use activities feature

        Input:
            file_name | str
                _summarizedActivities file
        Output
            activity_pd | pdf
                pandas dataframe of summarized activity data
            activity_set_pd | pdf
                pandas dataframe of summarized sets of activity data
    """

    with open(file_name) as file:
        j = json.load(file)

    activity_pd = pd.DataFrame()

    activity_pd['activityId'] = np.nan
    activity_pd['name'] = np.nan
    activity_pd['activityType'] = np.nan
    activity_pd['sportType'] = np.nan

    activity_pd['eventTypeId'] = np.nan
    activity_pd['startTimeGmt'] = np.nan
    activity_pd['startTimeLocal'] = np.nan
    activity_pd['duration'] = np.nan
    activity_pd['distance'] = np.nan
    activity_pd['avgSpeed'] = np.nan
    activity_pd['avgHr'] = np.nan
    activity_pd['maxHr'] = np.nan
    activity_pd['calories'] = np.nan
    activity_pd['bmrCalories'] = np.nan
    activity_pd['waterEstimated'] = np.nan
    activity_pd['moderateIntensityMinutes'] = np.nan
    activity_pd['vigorousIntensityMinutes'] = np.nan
    activity_pd['purposeful'] = np.nan
    activity_pd['pr'] = np.nan

    activity_pd['elevationGain'] = np.nan
    activity_pd['elevationLoss'] = np.nan
    activity_pd['minElevation'] = np.nan
    activity_pd['maxElevation'] = np.nan

    activity_pd['maxSpeed'] = np.nan
    activity_pd['maxVerticalSpeed'] = np.nan

    activity_pd['steps'] = np.nan
    activity_pd['locationName'] = np.nan

    activity_pd['minRespirationRate'] = np.nan
    activity_pd['maxRespirationRate'] = np.nan
    activity_pd['avgRespirationRate'] = np.nan

    activity_pd['avgFractionalCadence'] = np.nan
    activity_pd['maxFractionalCadence'] = np.nan

    activity_pd['startStress'] = np.nan
    activity_pd['endStress'] = np.nan
    activity_pd['differenceStress'] = np.nan

    activity_pd['summarizedExerciseSets'] = np.nan
    activity_pd['activeSets'] = np.nan
    activity_pd['totalSets'] = np.nan
    activity_pd['totalReps'] = np.nan

    activity_set_pd = pd.DataFrame()
    activity_set_pd['activityId'] = np.nan
    activity_set_pd['startTimeGmt'] = np.nan

    activity_set_pd['category'] = np.nan
    activity_set_pd['subCategory'] = np.nan
    activity_set_pd['reps'] = np.nan
    activity_set_pd['volume'] = np.nan
    activity_set_pd['duration'] = np.nan
    activity_set_pd['sets'] = np.nan
    set_row = 0

    for i in range(len(j[0]['summarizedActivitiesExport'])):
        sesh = j[0]['summarizedActivitiesExport'][i]
        for key, value in sesh.items():
            if key == 'summarizedExerciseSets':
                e = sesh['summarizedExerciseSets']
                start_row = set_row
                for ii in range(len(e)):
                    for s_key, s_value in e[ii].items():
                        activity_set_pd.loc[set_row,s_key]=s_value
                    set_row+=1
                activity_set_pd.loc[start_row:set_row, "activityId"] = sesh['activityId']
                activity_set_pd.loc[start_row:set_row, "startTimeGmt"] = sesh['startTimeGmt']
            elif key in activity_pd.columns:
                activity_pd.loc[i,key] = value

    return(activity_pd,activity_set_pd)

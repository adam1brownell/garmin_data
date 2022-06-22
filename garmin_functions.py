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

### DI-Connect-User Files

# FitnessAgeData.json
def build_fitness_age_data(file_name):
    with open(file_name) as file:
        j = json.load(file)
    ts = []
    for i in range(len(j)):
        ts.append(j[i]["createTimestamp"]['date'])

    fitness_age_pd = pd.DataFrame({"readingTimestamp":ts})

    fitness_age_pd['chronologicalAge'] = np.nan

    fitness_age_pd['bmi'] = np.nan
    fitness_age_pd['rhr'] = np.nan
    fitness_age_pd['totalVigorousDays'] = np.nan
    fitness_age_pd['numOfWeeksForIM'] = np.nan
    fitness_age_pd['healthyBmi'] = np.nan
    fitness_age_pd['healthyFat'] = np.nan
    fitness_age_pd['vo2MaxForHealthyBmiFat'] = np.nan
    fitness_age_pd['vo2MaxForHealthyActive'] = np.nan
    fitness_age_pd['biometricVo2Max'] = np.nan
    fitness_age_pd['currentBioAge'] = np.nan

    fitness_age_pd['healthyAllBioAge'] = np.nan
    fitness_age_pd['healthyBmiFatBioAge'] = np.nan
    fitness_age_pd['healthyActiveBioAge'] = np.nan

    fitness_age_pd['weightDataLastEntryDate'] = np.nan
    fitness_age_pd['rhrLastEntryDate'] = np.nan
    fitness_age_pd['totalVigorousIMs'] = np.nan

    for i in range(len(j)):
        sesh = j[i]
        for k,v in sesh.items():
            if k in ['createTimestamp','asOfDateGmt']:
                continue
            elif k in ['weightDataLastEntryDate','rhrLastEntryDate']:\
                fitness_age_pd.loc[i,k] = v['date']
            elif k in fitness_age_pd.columns:
                fitness_age_pd.loc[i,k] = v
    return(fitness_age_pd)

# HydrationLogFile
def build_hydration_data(file_name):
    with open(file_name) as file:
        j = json.load(file)

    ts_g = []
    ts_l = []
    for i in range(len(j)):
        ts_g.append(j[i]['persistedTimestampGMT']['date'])
        ts_l.append(j[i]['timestampLocal']['date'])

    hydrate_pd = pd.DataFrame({"timestampGMT":ts_g,"timestampLocal":ts_l})

    hydrate_pd['hydrationSource'] = np.nan

    hydrate_pd['hydrationSource'] = np.nan
    hydrate_pd['valueInML'] = np.nan
    hydrate_pd['activityId'] = np.nan
    hydrate_pd['capped'] = np.nan
    hydrate_pd['estimatedSweatLossInML'] = np.nan
    hydrate_pd['duration'] = np.nan

    for i in range(len(j)):
        sesh = j[i]
        for k,v in sesh.items():
            # Already used
            if k in ['persistedTimestampGMT','timestampLocal']:
                continue
            # Redundant/useless
            elif k in ['userProfilePK','calendarDate']:
                continue
            elif k in hydrate_pd.columns:
                try:
                    hydrate_pd.loc[i,k] = v
                except:
                    print('bad',k)
            else:
                print(k)

    return(hydrate_pd)



# UDSFile_ file
def build_uds_data(file_name):
    with open(file_name) as file:
        j = json.load(file)

    ts_g = []
    ts_l = []
    for i in range(len(j)):
        ts_g.append(j[i]['wellnessStartTimeGmt']['date'])
        ts_l.append(j[i]['wellnessStartTimeLocal']['date'])

    uds_pd = pd.DataFrame({"timestampStartGMT":ts_g,"timestampStartLocal":ts_l})

    # Listing all features for easy lookup later
    for col in [
                # Distance & Time Features
                "durationInMilliseconds","totalKilocalories",
                "activeKilocalories","bmrKilocalories","wellnessKilocalories","remainingKilocalories",
                "wellnessTotalKilocalories","wellnessActiveKilocalories","totalSteps",
                "dailyStepGoal","totalDistanceMeters","wellnessDistanceMeters","wellnessEndTimeGmt",
                "wellnessEndTimeLocal","highlyActiveSeconds","activeSeconds","moderateIntensityMinutes",
                "vigorousIntensityMinutes","floorsAscendedInMeters","floorsDescendedInMeters",
                "userIntensityMinutesGoal","userFloorsAscendedGoal","restingCaloriesFromActivity",


                # HR Features
                "minHeartRate","maxHeartRate","minAvgHeartRate","maxAvgHeartRate",
                "restingHeartRate","currentDayRestingHeartRate","restingHeartRateTimestamp",

                # Flags
                "includesWellnessData","includesActivityData","includesCalorieConsumedData",
                "includesSingleMeasurement","includesContinuousMeasurement","includesAllDayPulseOx",
                "includesSleepPulseOx",

                # Stress Features
                "totalAverageStressLevel","totalAverageStressLevelIntensity",
                "totalMaxStressLevel","totalStressIntensityCount","totalStressOffWristCount",
                "totalStressTooActiveCount","totalStressCount","totalStressIntensity","totalStressDuration",
                "totalStressRestDuration","totalStressActivityDuration","totalStressUncategorizedDuration",
                "StresstotalDuration","totalStressLowDuration","totalStressMediumDuration",
                "awakeAverageStressLevel","awakeAverageStressLevelIntensity","awakeMaxStressLevel",
                "awakeStressIntensityCount","awakeStressOffWristCount","awakeStressTooActiveCount",
                "awakeTotalStressCount","awakeTotalStressIntensity","awakeStressDuration",
                "awakeStressRestDuration","awakeStressActivityDuration","awakeStressUncategorizedDuration",
                "awakeStressTotalDuration","awakeStressLowDuration","awakeStressMediumDuration",
                "sleepAverageStressLevel","sleepAverageStressLevelIntensity",
                "totalStressHighDuration","awakeStressHighDuration","sleepMaxStressLevel",
                "sleepStressIntensityCount","sleepStressOffWristCount","sleepStressTooActiveCount",
                "sleepTotalStressCount","sleepTotalStressIntensity","sleepStressDuration",
                "sleepStressRestDuration","sleepStressActivityDuration","sleepStressUncategorizedDuration",
                "sleepStressTotalDuration","sleepStressLowDuration","sleepStressMediumDuration",
                "sleepStressHighDuration"

                # Body Battery Features
                "maxBodyBattery","maxBodyBatteryTimestamp","minBodyBattery",
                "minBodyBatteryTimestamp","EODbodyBattery","EODbodyBatteryTimestamp",

                # Respiration Features
                "avgWakingRespirationValue","highestRespirationValue","lowestRespirationValue",
                "latestRespirationValue","latestRespirationTimeGMT",

                # SPO2 Features
                "lowestSpo2Value","latestSpo2Value","latestSpo2ValueReadingTimeGmt",
                "latestSpo2ValueReadingTimeLocal"
                ]:
        uds_pd[col] = np.nan
    bad = []
    for i in range(len(j)):
        for key,value in j[i].items():
            if key in ['wellnessStartTimeGmt','wellnessStartTimeLocal','calendarDate',
                       'userProfilePK','hydration','uuid','version','source']:
                continue
            elif key in ['wellnessEndTimeGmt','wellnessEndTimeLocal',
                         'latestSpo2ValueReadingTimeGmt','latestSpo2ValueReadingTimeLocal']:
                uds_pd.loc[i,key]=value['date']
            elif key == 'allDayStress':
                for stress_dict in j[i][key]['aggregatorList']:

                    for stress_key,stress_value in stress_dict.items():
                        if 'stress' not in stress_key.lower():
                            a = 'Stress'
                        else:
                            a = ''
                        if stress_key == 'type':
                            continue
                        if (stress_dict['type'] == 'TOTAL') and ('total' in stress_key):
                            stress_key2 = a+stress_key
                        elif stress_dict['type'] == 'ASLEEP':
                            stress_key2 = 'sleep'+a+stress_key[0].upper()+stress_key[1:]
                        else:
                            stress_key2 = stress_dict['type'].lower()+a+stress_key[0].upper()+stress_key[1:]

                        uds_pd.loc[i,stress_key2]=stress_value
            elif key == 'bodyBattery':
                for batt_dict in j[i][key]['bodyBatteryStatList']:
                    bb_type = batt_dict['bodyBatteryStatType']
                    if bb_type in ['HIGHEST','LOWEST']:
                        if bb_type == 'HIGHEST':
                            b = 'max'
                        else:
                            b = 'min'
                        uds_pd.loc[i,b+'BodyBattery'] =  batt_dict['statsValue']
                        uds_pd.loc[i,b+'BodyBatteryTimestamp'] =  batt_dict['statTimestamp']['date']
                    elif bb_type == 'ENDOFDAY':
                        uds_pd.loc[i,'EODbodyBattery'] =  batt_dict['statsValue']
                        uds_pd.loc[i,'EODbodyBatteryTimestamp'] =  batt_dict['statTimestamp']['date']


            elif key == 'respiration':
                for resp_key, resp_value in j[i][key].items():
                    if resp_key in ['userProfilePK','calendarDate']:
                        continue
                    elif resp_key == 'latestRespirationTimeGMT':
                        uds_pd.loc[i,resp_key]=resp_value['date']
                    else:
                        uds_pd.loc[i,resp_key]=resp_value
            else:
                uds_pd.loc[i,key]=value
    return(uds_pd.copy())

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

## FIT Files ##

def generate_fit_files(FitCSVToolJar,tmp_root):
    from zipfile import ZipFile
    import subprocess

    with ZipFile(tmp_root+'UploadedFiles_0-_Part1.zip', 'r') as zipObj:
        fitFiles = zipObj.namelist()
        zipObj.extractall(tmp_root)

    for file in fitFiles:
        print(file)

        inputfile = tmp_root+file
        outputfile = tmp_root+file.replace(".fit","_raw.csv")
        os.system(f'java -jar {FitCSVToolJar} -b "{inputfile}" "{inputfile.replace(".fit","_raw.csv")}"')
        os.system(f'java -jar {FitCSVToolJar} -b "{inputfile}" "{inputfile.replace(".fit","_records.csv")}"  --defn none --data record')
        os.remove(inputfile)


    old_root = os.getcwd()
    os.chdir(tmp_root)

    os.system("cat *_records.csv >combined_records_full.csv")
    os.system("cat *_raw.csv >combined_raw_full.csv")
    os.chdir(old_root)

    ## TODO: Can change this to a python func if needed
    os.system(f'python clean_garmin.py -i {tmp_root+"/combined_records_full.csv"} -o {tmp_root+"/combined_records_clean.csv"}')
    os.system(f'python clean_garmin.py -i {tmp_root+"/combined_raw_full.csv"} -o {tmp_root+"/combined_raw_clean.csv"}')

    for file in os.listdir(tmp_root):
        if '.csv' in file:
            if 'clean' not in file:
                os.remove(tmp_root+"/"+file)

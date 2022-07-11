import sys
import os
from garmin_functions import *
import warnings
warnings.filterwarnings('ignore')

def main(connect_folder, FitCSVToolJar):
    """
    Generate usable CSV files from Garmin Connect Folders + Fit Files.

    Run via terminal -- python parse_garmin_connect "connect_folder" "FitCSVToolJar"

    input
        connect_folder || str || absolute file path to DI_CONNECT folder
        FitCSVToolJar  || str || absolute file path to FitCSVToolJar jar file

    output

    """

    garmin_pd = pd.DataFrame(columns=["startTimeGmt","dataType"])
    tmp_root = os.getcwd()+'/DI_CONNECT'
    for folder_name in os.listdir(tmp_root):
        tmp_folder = tmp_root+'/'+folder_name

        print(folder_name)


        ### DI-Connect-Wellness Files ###
        if folder_name == 'DI-Connect-Wellness':
            for file_name in os.listdir(tmp_folder):

                join_cols = ['startTimeGmt']

                if 'wellnessActivities' in file_name:

                    print("Pulling Heath Snapshot data...")
                    health_snapshot_pd = build_health_snapshot_data(tmp_folder+'/'+file_name)

                    print(f"\t{len(health_snapshot_pd):,} entrees..")

                    if 'startTimeLocal' in garmin_pd.columns:
                        join_cols.append('startTimeLocal')
                    if 'endTimeGmt' in garmin_pd.columns:
                        join_cols.append('endTimeGmt')
                    if 'respirationMin' in garmin_pd.columns:
                        join_cols.append('respirationMin')
                    if 'respirationMax' in garmin_pd.columns:
                        join_cols.append('respirationMax')
                    if 'respirationAvg' in garmin_pd.columns:
                        join_cols.append('respirationAvg')
                    if 'name' in garmin_pd.columns:
                        join_cols.append('name')

                    garmin_pd = garmin_pd.merge(health_snapshot_pd,on=join_cols,how="outer") \
                                         .fillna({'dataType':'healthSnapshot'})

                elif 'sleepData' in file_name:

                    print("Pulling Sleep data...")
                    sleep_pd = build_sleep_data(tmp_folder+'/'+file_name)

                    print(f"\t{len(sleep_pd):,} entrees..")

                    if 'endTimeGmt' in garmin_pd.columns:
                        join_cols.append('endTimeGmt')
                    if 'respirationMin' in garmin_pd.columns:
                        join_cols.append('respirationMin')
                    if 'respirationMax' in garmin_pd.columns:
                        join_cols.append('respirationMax')
                    if 'respirationAvg' in garmin_pd.columns:
                        join_cols.append('respirationAvg')

                    garmin_pd = garmin_pd.merge(sleep_pd,on=join_cols,how="outer") \
                                         .fillna({'dataType':'sleepData'})

        ### DI-Connect-User Files ###
        elif folder_name == 'DI-Connect-User':
            for file_name in os.listdir(tmp_folder):

                join_cols = ['startTimeGmt']

                if 'FitnessAgeData' in file_name:

                    print("Fitness Age data...")
                    fitness_age_pd = build_fitness_age_data(tmp_folder+'/'+file_name)

                    print(f"\t{len(fitness_age_pd):,} entrees..")

                    garmin_pd = garmin_pd.merge(fitness_age_pd,on=join_cols,how="outer") \
                                         .fillna({'dataType':'fitnessAge'})

                elif 'HydrationLogFile' in file_name:

                    print("Hydration data...")
                    hydration_pd = build_hydration_data(tmp_folder+'/'+file_name)

                    print(f"\t{len(hydration_pd):,} entrees..")


                    if 'startTimeLocal' in garmin_pd.columns:
                        join_cols.append('startTimeLocal')
                    if 'duration' in garmin_pd.columns:
                        join_cols.append('duration')
                    if 'activityId' in garmin_pd.columns:
                        join_cols.append('activityId')

                    garmin_pd = garmin_pd.merge(hydration_pd,on=join_cols,how="outer") \
                                         .fillna({'dataType':'hydrationData'})

                elif 'UDSFile_' in file_name:

                    print("UDS data...")
                    uds_pd = build_uds_data(tmp_folder+'/'+file_name)

                    print(f"\t{len(uds_pd):,} entrees..")

                    if 'startTimeLocal' in garmin_pd.columns:
                        join_cols.append('startTimeLocal')
                    if 'moderateIntensityMinutes' in garmin_pd.columns:
                        join_cols.append('moderateIntensityMinutes')
                    if 'vigorousIntensityMinutes' in garmin_pd.columns:
                        join_cols.append('vigorousIntensityMinutes')

                    garmin_pd = garmin_pd.merge(uds_pd,on=join_cols,how="outer") \
                                         .fillna({'dataType':'UDS'})

        ### DI-Connect-Fitness Files ###
        elif folder_name == 'DI-Connect-Fitness':
            for file_name in os.listdir(tmp_folder):

                join_cols = ['startTimeGmt']

                if 'summarizedActivities' in file_name:

                    print("Activity data...")
                    # activity_pd,activity_set_pd = build_activity_summary_data(tmp_folder+'/'+file_name)
                    activity_pd = build_activity_summary_data(tmp_folder+'/'+file_name)

                    print(f"\t{len(activity_pd):,} entrees..")


                    if 'startTimeLocal' in garmin_pd.columns:
                        join_cols.append('startTimeLocal')
                    if 'name' in garmin_pd.columns:
                        join_cols.append('name')
                    if 'duration' in garmin_pd.columns:
                        join_cols.append('duration')
                    if 'moderateIntensityMinutes' in garmin_pd.columns:
                        join_cols.append('moderateIntensityMinutes')
                    if 'vigorousIntensityMinutes' in garmin_pd.columns:
                        join_cols.append('vigorousIntensityMinutes')
                    if 'activityId' in garmin_pd.columns:
                        join_cols.append('activityId')
                    if 'respirationMin' in garmin_pd.columns:
                        join_cols.append('respirationMin')
                    if 'respirationMax' in garmin_pd.columns:
                        join_cols.append('respirationMax')
                    if 'respirationAvg' in garmin_pd.columns:
                        join_cols.append('respirationAvg')

                    garmin_pd = garmin_pd.merge(activity_pd,on=join_cols,how="outer") \
                                         .fillna({'dataType':'activityData'})

        ### DI-Connect-Fitness Files ###
        elif folder_name == "DI-Connect-Fitness-Uploaded-Files":
            for file_name in os.listdir(tmp_folder):

                if 'UploadedFiles' in file_name:

                    if os.path.exists(FitCSVToolJar):
                        print("FITCSV JAR:", FitCSVToolJar)
                        generate_fit_files(FitCSVToolJar,tmp_folder,file_name)
                    else:
                        print("FitCSVJar Path is invalid!")

    
    garmin_pd.to_csv("garmin_data.csv")
    return

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

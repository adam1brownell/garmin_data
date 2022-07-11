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

        ### DI-Connect-Wellness Files ###
        if folder_name == 'DI-Connect-Wellness':
            for file_name in os.listdir(tmp_folder):
                if 'wellnessActivities' in file_name:

                    print("Pulling Heath Snapshot data...")
                    health_snapshot_pd = build_health_snapshot_data(tmp_folder+'/'+file_name)

                    print(f"\t{len(health_snapshot_pd):,} entrees..")
                    print(f"\tJoinable Key: {'startTimeGmt' in health_snapshot_pd.columns}")

                    garmin_pd = garmin_pd.merge(health_snapshot_pd,on='startTimeGmt',how="outer") \
                                         .fillna({'dataType':'healthSnapshot'})

                elif 'sleepData' in file_name:

                    print("Pulling Sleep data...")
                    sleep_pd = build_sleep_data(tmp_folder+'/'+file_name)

                    print(f"\t{len(sleep_pd):,} entrees..")
                    print(f"\tJoinable Key: {'startTimeGmt' in sleep_pd.columns}")

                    garmin_pd = garmin_pd.merge(sleep_pd,on='startTimeGmt',how="outer") \
                                         .fillna({'dataType':'healthSnapshot'})

        ### DI-Connect-User Files ###
        elif folder_name == 'DI-Connect-User':
            for file_name in os.listdir(tmp_folder):
                if 'FitnessAgeData' in file_name:

                    print("Fitness Age data...")
                    fitness_age_pd = build_fitness_age_data(tmp_folder+'/'+file_name)

                    print(f"\t{len(fitness_age_pd):,} entrees..")
                    print(f"\tJoinable Key: {'startTimeGmt' in fitness_age_pd.columns}")

                    garmin_pd = garmin_pd.merge(fitness_age_pd,on='startTimeGmt',how="outer") \
                                         .fillna({'dataType':'fitnessAge'})

                elif 'HydrationLogFile' in file_name:

                    print("Hydration data...")
                    hydration_pd = build_hydration_data(tmp_folder+'/'+file_name)

                    print(f"\t{len(hydration_pd):,} entrees..")
                    print(f"\tJoinable Key: {'startTimeGmt' in hydration_pd.columns}")

                    garmin_pd = garmin_pd.merge(hydration_pd,on='startTimeGmt',how="outer") \
                                         .fillna({'dataType':'hydrationData'})

                elif 'UDSFile_' in file_name:

                    print("UDS data...")
                    uds_pd = build_uds_data(tmp_folder+'/'+file_name)

                    print(f"\t{len(uds_pd):,} entrees..")
                    print(f"\tJoinable Key: {'startTimeGmt' in uds_pd.columns}")

                    garmin_pd = garmin_pd.merge(uds_pd,on='startTimeGmt',how="outer") \
                                         .fillna({'dataType':'UDS'})

        ### DI-Connect-Fitness Files ###
        elif folder_name == 'DI-Connect-Fitness':
            for file_name in os.listdir(tmp_folder):
                if 'summarizedActivities' in file_name:

                    print("Activity data...")
                    activity_pd,activity_set_pd = build_activity_summary_data(tmp_folder+'/'+file_name)

                    print(f"\t{len(activity_pd):,} entrees..")
                    print(f"\tJoinable Key: {'startTimeGmt' in activity_pd.columns}")
                    print(f"\t{len(activity_set_pd):,} set entrees..")
                    print(f"\tJoinable Key: {'startTimeGmt' in activity_set_pd.columns}")

                    garmin_pd = garmin_pd.merge(activity_pd,on='startTimeGmt',how="outer") \
                                         .merge(activity_set_pd,on='startTimeGmt',how="outer") \
                                         .fillna({'dataType':'activityData'})

        ### DI-Connect-Fitness Files ###
        elif folder_name == "DI-Connect-Fitness-Upload-Files":
            for file_name in os.listdir(tmp_folder):
                if 'UploadedFiles' in file_name:
                    if os.path.exists(FitCSVToolJar):
                        generate_fit_files(FitCSVToolJar,tmp_root,file_name)
                    else:
                        print("FitCSVJar Path is invalid!")

    garmin_pd.to_csv("garmin_data.csv")
    return

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[1])

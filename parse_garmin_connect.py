import sys
import os
from garmin_functions import *
import warnings
warnings.filterwarnings('ignore')

def main(connect_folder):

    tmp_root = os.getcwd()+'/DI_CONNECT'
    for folder_name in os.listdir(tmp_root):
        tmp_folder = tmp_root+'/'+folder_name
        ### DI-Connect-Wellness Files ###
        if folder_name == 'DI-Connect-Wellness':
            for file_name in os.listdir(tmp_folder):
                if 'wellnessActivities' in file_name:
                    health_snapshot_pd = build_health_snapshot_data(tmp_folder+'/'+file_name)
                elif 'sleepData' in file_name:
                    sleep_pd = build_sleep_data(tmp_folder+'/'+file_name)

        ### DI-Connect-User Files ###
        elif folder_name == 'DI-Connect-User':
            for file_name in os.listdir(tmp_folder):
                if 'FitnessAgeData' in file_name:
                    fitness_age_pd = build_fitness_age_data(tmp_folder+'/'+file_name)
                elif 'HydrationLogFile' in file_name:
                    hydration_pd = build_hydration_data(tmp_folder+'/'+file_name)
                elif 'UDSFile_' in file_name:
                    uds_pd = build_uds_data(tmp_folder+'/'+file_name)

        ### DI-Connect-Fitness Files ###
        elif folder_name == 'DI-Connect-Fitness':
            for file_name in os.listdir(tmp_folder):
                if 'summarizedActivities' in file_name:
                    activity_pd,activity_set_pd = build_activity_summary_data(tmp_folder+'/'+file_name)


    return

if __name__ == '__main__':
    main(sys.argv[1])

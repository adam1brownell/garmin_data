import sys
import os
from garmin_functions import *

def main(connect_folder):
    tmp_root = os.getcwd()+'/DI_CONNECT'
    for folder_name in os.listdir(tmp_root):

        ### DI-Connect-Wellness Files ###
        if folder_name == 'DI-Connect-Wellness':
            tmp_folder = tmp_root+'/'+folder_name
            for file_name in os.listdir(tmp_folder):
                if 'wellnessActivities' in file_name:
                    health_snapshot_pd = build_health_snapshot_data(tmp_folder+'/'+file_name)
                elif 'sleepData' in file_name:
                    sleep_pd = build_sleep_data(tmp_folder+'/'+file_name)
                    
        ### DI-Connect-Fitness Files ###
        elif folder_name == 'DI-Connect-Fitness':
            tmp_folder = tmp_root+'/'+folder_name
            for file_name in os.listdir(tmp_folder):
                if 'summarizedActivitie' in file_name:
                    activity_pd,activity_set_pd = build_activity_summary_data(tmp_folder+'/'+file_name)


    return

if __name__ == '__main__':
    main(sys.argv[1])

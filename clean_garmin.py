import pandas as pd
import numpy as np
import sys, getopt

def main(argv):

    inputfile = ''
    outputfile = ''
    try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
      print('clean_garmin.py -i <inputfile> -o <outputfile>')
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
         print('clean_garmin.py -i <inputfile> -o <outputfile>')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg

    print('Reading Data...')
    bd_data = pd.read_csv(inputfile, on_bad_lines="skip")

    print("Filtering Down to Data...")
    ### Filter down to Data ###
    bd_data = bd_data[(bd_data.Type=='Data')& \
                      (~bd_data.Message.isin(['unknown','file_id','device_info','software']))]

    cols = bd_data.columns

    print("Pivoting Table...")
    ### Pivot Ugly Table Manually ###
    for col in cols:
        if 'Field' in col:
            num = col.split()[1]
            vals = bd_data[col].unique()
            for v in vals:
                if (v is in ['unknown','software_version']) or pd.isna(v):
                    continue
                if v not in bd_data.columns:
                    bd_data[str(v)] = None
                bd_data.loc[bd_data[col] == v, v] = bd_data['Value '+num]

    bd_data.drop(cols, axis=1, inplace=True)

    print("Cleaning Timestamps...")

    ### Handle Messy Timestamps in Raw Data ###
    if 'stress_level_time' in bd_data.columns:
        bd_data.loc[~pd.isna(bd_data.stress_level_time),'timestamp'] = bd_data.stress_level_time
        bd_data.drop(['stress_level_time'],axis=1,inplace=True)

    if 'local_timestamp' in bd_data.columns:
        bd_data.drop(['local_timestamp'],axis=1,inplace=True)

    if 'timestamp_16' in bd_data.columns:
        place = 1
        for i in bd_data.index[1:]:
            # If timestamp 16 is a number...
            if not pd.isna(bd_data.loc[i].timestamp_16):
                # Go back up index...
                for j in reversed(bd_data.index[:place]):
                    # Find the most recent timestamp
                    if not pd.isna(bd_data.loc[j].timestamp):
                        # Add them together
                        try:
                            bd_data.loc[bd_data.index==i,'timestamp'] = int(bd_data.loc[j].timestamp)+int(bd_data.loc[i].timestamp_16)
                        except:
                            print("Time Stamp:", bd_data.loc[j].timestamp)
                            print("Time Stamp 16:", bd_data.loc[i].timestamp_16)
                        break
            place += 1
        bd_data.drop(['timestamp_16'],axis=1,inplace=True)

    bd_data = bd_data[~pd.isna(bd_data.timestamp)]


    print("Creating timestamp-indexed dataset...")
    ### Change all columns to numeric, reduce columns to be timestamp-based ###
    g_dict = {}
    for col in bd_data.columns:
        try:
            bd_data[col] = pd.to_numeric(bd_data[col])
        except:
            bd_data[col] = [str(i).split("|")[0] if i else None for i in bd_data[col]]
            bd_data[col] = pd.to_numeric(bd_data[col])
        g_dict[col] = lambda x: np.max(x)

    bd_data = bd_data.groupby('timestamp').agg(g_dict).drop(['timestamp'],axis=1).reset_index()
    print("Saving...")
    bd_data.to_csv(outputfile)
    print("Done!")

if __name__ == "__main__":
    main(sys.argv[1:])

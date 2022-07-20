"""
This blank correction is based on the wheel TW3416 which contained the following sets of samples:
Wood
Plant
Water

The first section of this code does "pre-processing" from RLIMS to Python.
Essentially, from RLIMS, the data formatting needs to be cleaned up in order to be worked with. For blank corrections,
this means linking the chemical and physical pre-treatment processes with the ratio to standard data. Importing XCAMS
results to RLIMS does this; however, when exported back into python to do the blank correction, there are "n" extra columns per
sample based on how many "Process steps" there were.
The code below identifies how many gaps exist between the important data in the exported sheet, and associates the "Process it
underwent" to the sample itself. This linkage is critical for the next step of the blank correction.

The second section of the code does some quality checking on OX-1 data.

The third will link it to the standards of a similar type for later blank correction

"""
import pandas as pd
import numpy as np
from Process_List_Library import processes
pd.options.mode.chained_assignment = None  # default='warn'
"""
This script is written to use a specific output file from RLIMS which includes exported data from the tables:
"Process List"
"AMS Submission Results Complete"
"""
df = pd.read_excel(r'C:\Users\clewis\Desktop\3416_2.xlsx')  # export the file from RLIMS containing TW DATA

# <editor-fold desc="Pre Processing / Data Organizing from RLIMS">
"""
The first thing I want to do is "pre-process" the file. I want to get the pre-treatment data in the same line as 
the data I want, and drop ALLLL the unnecessary columns I don't want. This process is complicated by the fact that the pre-processing information
is not delivered in a constant way in the excel file, based on how much data for pre-processing exists. We need to get rid of those gaps, and associate
the process to the rts data in the same line. 
"""

cat_index = np.linspace(0, len(df)-1, len(df))   # here I am creating a list the length of the dataframe, and attaching it to the dataframe (next line)
df['cat_index'] = cat_index                      # it will be used later in removing duplicates during concatanation.

df = df[['cat_index', 'Category Field',          # This group of lines gets rid of the excess "clutter" that comes from the dataframe when its exported from RLIMS
         'Description from Sample','TP',         # I'm only going to keep the columns that I really need for the rest of the analysis / blank correction.
         'AMS Category ID XCAMS',
         'Process Name',
         'Category In Calculation',
         'delta13C_IRMS',
         'delta13C_IRMS_Error',
         'delta13C_AMS','delta13C_AMS_Error',
         'Ratio to standard','Ratio to standard error']]

df['AMS Category ID XCAMS'] = df['AMS Category ID XCAMS'].fillna(0)  # wherever you see an empty cell in the category 'AMS Category ID XCAMS', add a zero.
                                                                     # I did this so I could relate to it in a few lines

# This very tricky but very important block of code identifies where there is data, and where there is empty space when RLIMS
# exports in the way I described earlier. The array that is created ("Indexing_array") stores a list of where there is data it will need later
indexing_array = []                                                  # Initialize an empty array
for i in range(0, len(df)):                                          # Begin the a loop for the length of the ENTIRE dataframe
    row = df.iloc[i]                                                 # grab the "i'th" row.
    cat = row['AMS Category ID XCAMS']                               # Isolate the category ['AMS Category ID XCAMS']
    if cat != 0:                                                     # Do I see NOT a zero? THis means there was real data here, not just extra processes.
        indexing_array.append(row['cat_index'])                      # Take this row and index it onto the array I initialized before.

# The next three lines take the final row of the dataframe, and add it onto the array that I'm building, called "Indexing_array".
# I did this beacuse, later the script will search for intervals upon which to index. To do this, it needs the final row to do the final index.
finalrow = df.iloc[-1]
finalcat = finalrow['cat_index']
indexing_array.append(finalcat)

# Now the code is going to use the "Indexing_array" to index the data.
mt_array2 = []                                                       # Initialize another empty array.
for i in range(0, 40):                                               # From 0-40, or as python sees, 0-39, begin a loop:
    row = df.iloc[int(indexing_array[i])]                            # Store each row with real data as it's own variable for later
    x = df.iloc[int(indexing_array[i]):int(indexing_array[i+1])]     # Index from this row, until our indexing array says the next target begins
    x = x['Process Name']                                            # grab the data in the column process name and turn it into data type column (next line)
    x = list(x)
# In this nested loop, the scripts is going to go into Process_list_library.py and find the list of processes I'm interested in (I want
# to know which samples are pre-processed with AAA, Cellulose, Water CO2 Evolution, etc."
    for k in range(0, len(processes)):                               # Loop through each item in the list.
        y = processes[k]                                             # For this, the "k'th" item,
        if y in x:                                                   # if this "k'th" item matches one of those in the data grabbed from the main loop above,
            row['Cleaned PreProcess Information'] = y                # Tack this item (k) onto the row itsef. BEFORE IT WAS A DIFFERENT LINE. This is what I'm trying to remedy.
            mt_array2.append(row)                                    # Append this row, now containing the preprocessing info, to a new array.

cleaneddf = pd.DataFrame(mt_array2)                                  # Turn this new array into a DataFrame
cleaneddf = cleaneddf.dropna(subset='AMS Category ID XCAMS')         # Drop where there is no data in this category
df = df.dropna(subset='AMS Category ID XCAMS')                       # THis line returns to the ORIGINAL, main dataframe (not the difference)

# Now I'm going to concatonate the old and new dataframes together, and drop the duplicates.
# This allows me to see which rows contain empty cells in the pre-processing column. (Usually OX-1's).
df_new = pd.concat([cleaneddf, df], ignore_index=True, sort =True).drop_duplicates(['cat_index'], keep='first')
df_new = df_new.dropna(subset = 'Category In Calculation')           # Drop empty lines
# </editor-fold>

# <editor-fold desc="Primary Standard Quality Check">
"""
Lets check how the OX-1's performed.
"""
primary_standards = df_new.loc[df_new['AMS Category ID XCAMS'] == 'OxI']  # grab all the OX-1's
print("The OX-1 category is {}, and the description is {}.".format(np.unique(primary_standards['Category Field']),
                                                                   np.unique(primary_standards['Description from Sample'])))

prim_std_average = np.average(primary_standards['Ratio to standard'])
prim_std_1sigma = np.std(primary_standards['Ratio to standard'])
rounding_decimal = 3
# Note: if the rounding decimal is around 3, but the result comes out to 1.0, this is because it has rounded up from 0.99999 or so, for example.
print("The average RTS of the Primary Standards in this wheel is {} \u00B1 {}".format(round(prim_std_average, rounding_decimal),
                                                                                      round(prim_std_1sigma, rounding_decimal)))

prim_std_13average = np.average(primary_standards['delta13C_AMS'])
prim_std_13_1sigma = np.std(primary_standards['delta13C_AMS'])
print("The average RTS of the OX-1 13C values in this wheel is {} \u00B1 {}".format(round(prim_std_13average, rounding_decimal),
                                                                                    round(prim_std_13_1sigma, rounding_decimal)))
print()
# Do any of the OX-1's deviate from their IRMS number?
# Compare 13C AMS to 13C IRMS

arr1 = []  # initialize a few empty arrays for later use
arr2 = []
C13_threshold = 2
for i in range(0, len(primary_standards)):
    row = primary_standards.iloc[i]         # access the first row
    ams = row['delta13C_AMS']
    ams_err = row['delta13C_AMS_Error']
    irms = row['delta13C_IRMS']
    irms_error = row['delta13C_IRMS_Error']
    delta = abs(ams - irms)

    if delta >= C13_threshold:
        arr1.append(delta)
        arr2.append(row['TP'])

result = pd.DataFrame({"TP": arr2, "Absolute value, (AMS - IRMS 13C)": arr1})
if len(result) > 0:
    print("The following standards are outside the selected range of {}\u2030 difference between IRMS and AMS 13C".format(C13_threshold))
    print(result)
print()
# </editor-fold>

"""
Now, link the data that we just cleaned with blanks and standards of the same type. 
"""
# For example, in df_new:
# TODO: For these samples, coordinate them with standards with R# XXXX/ X
AAA = df_new.loc[(df_new['AMS Category ID XCAMS'] == 'UNOr') | (df_new['Cleaned PreProcess Information'] == 'Acid Alkali Acid')]
Cell = df_new.loc[(df_new['AMS Category ID XCAMS'] == 'UNOr') | (df_new['Cleaned PreProcess Information'] == 'Cellulose Extraction')]
waters = df_new.loc[(df_new['AMS Category ID XCAMS'] == 'UNIn') | (df_new['Cleaned PreProcess Information'] == 'Water CO2 Evolution')]
AAA_std = df_new.loc[(df_new['AMS Category ID XCAMS'] == 'UNSt') | (df_new['Cleaned PreProcess Information'] == 'Acid Alkali Acid')]
Cell_std = df_new.loc[(df_new['AMS Category ID XCAMS'] == 'UNSt') | (df_new['Cleaned PreProcess Information'] == 'Cellulose Extraction')]
waters_std = df_new.loc[(df_new['AMS Category ID XCAMS'] == 'UNSt') | (df_new['Cleaned PreProcess Information'] == 'Water CO2 Evolution')]

# Historical standard data (This will need to be re-downloaded each time we do blank corrections in order to get the
# most up to date blanks
stds_hist = pd.read_excel(r'C:\Users\clewis\Desktop\hist_stds.xlsx')

AAA_stds = stds_hist.loc[(stds_hist['R'] == '40142/2')]
Cell_stds = stds_hist.loc[(stds_hist['R'] == '40142/1')]
Water_stds = stds_hist.loc[(stds_hist['R'] == '14047/11')]

mt_dataframe = pd.DataFrame
x = [AAA_stds, Cell_stds, Water_stds]
for i in range(0, len(x)):
    group = x[i]
    rts = group['Ratio to standard']
    rts_average = np.average(rts)
    rts_std = np.std(rts)
    stds_df = pd.DataFrame({"Standard Group": group['R'],
                            "Ratio to standard Average": rts_average,
                            "Ratio to standard 1-sigma": rts_std})

    # mt_dataframe.concat(stds_df, ignore_index=True)

























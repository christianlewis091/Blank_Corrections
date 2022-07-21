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
from blank_correction_functions import long_date_to_decimal_date
from scipy.stats import sem
pd.options.mode.chained_assignment = None  # default='warn'
"""
This script is written to use a specific output file from RLIMS which includes exported data from the tables:
"Process List"
"AMS Submission Results Complete"

Currently, this script should be able to determine MCC for wheels that contain organics processed with AAA and Cellulose
and waters. 
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
         'Ratio to standard','Ratio to standard error',
         'delta13C_In_Calculation','Collection Decimal Date','Date Run']]


df['AMS Category ID XCAMS'] = df['AMS Category ID XCAMS'].fillna(0)  # wherever you see an empty cell in the category 'AMS Category ID XCAMS', add a zero.
                                                                     # I did this so I could relate to it in a few lines


df['Collection Decimal Date'] = df['Collection Decimal Date'].fillna(max(df['Date Run']))  # if there is no sampling date, set it to TODAY.

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
df_new = df_new.dropna(subset = 'Category In Calculation').reset_index(drop=True)           # Drop empty lines
# df_new.to_excel('Results.xlsx')
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

# <editor-fold desc="Select Standards that will be used for correction">
"""
Now, link the data that we just cleaned with blanks and standards of the same type. 
"""
# TODO: When new processes need to be added to the script (Carbonate CO2 Evolution, AIRS, GRASS), it needs to be added HERE.
# UNKNOWNS
AAA = df_new.loc[((df_new['AMS Category ID XCAMS'] == 'UNOr') |                     # Find where the colums is (UNOr OR UNSt) AND Acid Alkali Acid
                  (df_new['AMS Category ID XCAMS'] == 'UNSt')) &
                  (df_new['Cleaned PreProcess Information'] == 'Acid Alkali Acid')].reset_index(drop=True)

Cell = df_new.loc[((df_new['AMS Category ID XCAMS'] == 'UNOr') |                     # Find where the colums is (UNOr OR UNSt) AND Acid Alkali Acid
                   (df_new['AMS Category ID XCAMS'] == 'UNSt')) &
                   (df_new['Cleaned PreProcess Information'] == 'Cellulose Extraction')].reset_index(drop=True)

waters = df_new.loc[((df_new['AMS Category ID XCAMS'] == 'UNOr') |                     # Find where the colums is (UNOr OR UNSt) AND Acid Alkali Acid
                     (df_new['AMS Category ID XCAMS'] == 'UNSt')) &
                    (df_new['Cleaned PreProcess Information'] == 'Water CO2 Evolution')].reset_index(drop=True)

# Historical standard data (This will need to be re-downloaded each time we do blank corrections in order to get the
# most up to date blanks
stds_hist = pd.read_excel(r'C:\Users\clewis\Desktop\hist_stds.xlsx')

AAA_stds = stds_hist.loc[(stds_hist['R'] == '40142/2')]               # FIND ALL THE AAA STANDARDS IN THE HISTORICAL SET
Cell_stds = stds_hist.loc[(stds_hist['R'] == '40142/1')]              # FIND ALL THE cellulose STANDARDS IN THE HISTORICAL SET
Water_stds = stds_hist.loc[(stds_hist['R'] == '14047/11')]            # FIND ALL THE WATERLINE STANDARDS IN THE HISTORICAL SET
chosen_stds = pd.concat([AAA_stds, Cell_stds, Water_stds]).dropna(subset = 'Date Run').reset_index(drop=True)  # CONCAT so I can clean them up in one shot

x = chosen_stds['Date Run']
chosen_stds['Date Run'] = long_date_to_decimal_date(x)                     # This line converts the dates to "Decimal Date" so that I can find only dates that are 0.5 years max before most recent date
date_bound = max(chosen_stds['Date Run']) - 0.5
chosen_stds = chosen_stds.loc[(chosen_stds['Date Run'] > date_bound)]      # Index: find ONLY dates that are more recent than 1/2 year
chosen_stds = chosen_stds.loc[(chosen_stds['Quality Flag'] != 'X..')]      # Index: drop everything that contains a quality flag
chosen_stds = chosen_stds.loc[(chosen_stds['Weight Initial'] > 0.3)]       # Drop everything that is smaller than 0.3 mg.

chosen_stds = chosen_stds[['Sample Description','Category In Calculation', 'Job', 'TP', 'R', 'Ratio to standard', 'Ratio to standard error', 'Quality Flag', 'TW']]

AAA_stds = chosen_stds.loc[(chosen_stds['R'] == '40142/2')].reset_index(drop=True)                         # Re-isolate the AAA standards
Cell_stds = chosen_stds.loc[(chosen_stds['R'] == '40142/1')].reset_index(drop=True)                        # Re-isolate the Cellulose standards
Water_stds = chosen_stds.loc[(chosen_stds['R'] == '14047/11')].reset_index(drop=True)                      # Re-isolate the WATERLINE standards

rounding_decimal = 5
AAA_blank = np.average(AAA_stds['Ratio to standard'])                          # Calculate the average RTS of this blank, and its standard deviation. Then print it with
AAA_blank_1sigma = np.std(AAA_stds['Ratio to standard'])                       # the number of decimal points specified above.
AAA['MCC'] = AAA_blank
AAA['MCC_error'] = AAA_blank_1sigma
print("For AAA, the MCC (the average of all available standards) is: {} \u00B1 {}".format(round(AAA_blank, rounding_decimal), round(AAA_blank_1sigma, rounding_decimal)))

Cell_blank = np.average(Cell_stds['Ratio to standard'])
Cell_blank_1sigma = np.std(Cell_stds['Ratio to standard'])
Cell['MCC'] = Cell_blank
Cell['MCC_error'] = Cell_blank_1sigma
print("For Cellulose, the MCC (the average of all available standards) is: {} \u00B1 {}".format(round(Cell_blank, rounding_decimal), round(Cell_blank_1sigma, rounding_decimal)))

water_blank = np.average(Water_stds['Ratio to standard'])
print(type(water_blank))
water_blank_1sigma = np.std(Water_stds['Ratio to standard'])
waters['MCC'] = water_blank
waters['MCC_error'] = water_blank_1sigma
print("For waters, the MCC (the average of all available standards) is: {} \u00B1 {}".format(round(water_blank, rounding_decimal), round(water_blank_1sigma, rounding_decimal)))
print("Right now, the code does a great job duplicating MCC calculated from RLIMS, but not the  Check RLIMS script for MCC error type (1-sigma? std error?)")
# </editor-fold>


"""
As Jocelyn asked, if you want the calculations to be done in RLIMS, then you can skip this step, and let the code just 
write everything above to excel. But, I want all the calculatinos to be done via python to save time, and then the files
be merged into RLIMS. We can add the calculations here and not use them if we don't want to use them. 
"""

# This function uses the equations built from RLIMS to calculate the corrected fraction modern.
# rts = ratio to standard of the sample.
# MCC = the blanks found in the step / section above
# DCCstd & DCC = for large samples, set these to zero
# delta13C_In_Calculation = grab this variable from the imported data from RLIMS x['delta13C_In_Calculation']
# sampling_date = grab from RLIMS data x['Collection Decimal Date']
# dataframe used =

def radiocarbon_calcs(dataframe_used):
    template_dataframe = dataframe_used  # import the real dataframe for calculation / variable addition
    rts = template_dataframe['Ratio to standard']
    MCC = template_dataframe['MCC']
    delta13C_In_Calculation = template_dataframe['delta13C_In_Calculation']
    sampling_date = template_dataframe['Collection Decimal Date']
    DCCstd = 0
    DCC = 0

    RTS_corrected = (rts - MCC)/(1-MCC)
    Std_spec_act_const = 1.040  # Standard multiplier
    rts_stds_av = prim_std_average           # see from above. I'm keeping rts_stds_av as the variable name since this is how it is in RLIMS
    delta13C_stds_av = prim_std_13average    # same as line above, want to keep VAR name the same as RLIMS
    F_corrected_normed = (RTS_corrected /(Std_spec_act_const * rts_stds_av)) * \
                         ((1 + delta13C_stds_av/ 1000) / (1 + delta13C_In_Calculation / 1000))
    # TODO propogate error in FM calculation
    age_corr = np.exp((1950-sampling_date)/8267)
    D14C = 1000*(F_corrected_normed*age_corr - 1)
    # TODO D14C_err = 1000 * FM error

    template_dataframe['RTS_corrected'] = RTS_corrected
    template_dataframe['F_corrected_normed'] = F_corrected_normed
    template_dataframe['D14C'] = D14C

    return template_dataframe

AAA = radiocarbon_calcs(AAA)

# <editor-fold desc="Write Data to Excel">
writer = pd.ExcelWriter('Results.xlsx', engine='openpyxl')
df_new.to_excel(writer, sheet_name='Wheel Summary')
AAA.to_excel(writer, sheet_name='Unknowns (AAA)')
Cell.to_excel(writer, sheet_name='Unknowns (Cellulose)')
waters.to_excel(writer, sheet_name='Unknowns (Waters)')
AAA_stds.to_excel(writer, sheet_name='Chosen Standards (AAA)')
Cell_stds.to_excel(writer, sheet_name='Chosen Standards (Cellulose)')
Water_stds.to_excel(writer, sheet_name='Chosen Standards (Waters)')

writer.save()
# </editor-fold>
























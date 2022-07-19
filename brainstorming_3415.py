"""
This project is meant to streamline the historial process of blank corrections in the GNS Rafter Lab. Typically this
was done in many steps using RLIMS and I hope to streamline it to save lots of people lots of time.

The following steps need to be taken throughout this process to mimic/streamline the original process.

Outside of this script:
Export data from CALAMS
Change it to CSV File
Import into RLIMS
Export from RLIMS to xlsx file, including ancillary data required for useful indexing

Index by graphite type:
 - primary standard
 - secondary standard
 - blank
 - unknown

Quality Check on Primary Standards

Match sample types to historal standards of that type for 180 days before present day

Using that associated group of standards, mass balance calculate the blank for each unknown

Output data to a file which can be merged into RLIMS
Output a text file that can saved into a folder, including useful metadata.
"""
# TODO: Add first step: download TW data from RLIMS
# TODO: Bring up to Valerie, RLIMS output file has two columns titled: "Sample Description"
# TODO: In order to streamline yet more, we need to enable ODBC/JDBC which communicates from script to database and back (or just leave it as Import XCAMS Results -> Export as .mer file)
# TODO: Increase useability for more complex wheels with different sample types:
# TODO: add rafter v ANSTO Cellulose
# TODO: pull R number
# TODO: flag ratio to standard outside of 2-sigma

import pandas as pd
import numpy as np
from PyAstronomy import pyasl
import openpyxl

def long_date_to_decimal_date(x):
    array = []  # define an empty array in which the data will be stored
    for i in range(0, len(x)):  # initialize the for loop to run the length of our dataset (x)
        j = x[i]  # assign j: grab the i'th value from our dataset (x)
        decy = pyasl.decimalYear(j)  # The heavy lifting is done via this Py-astronomy package
        decy = float(decy)  # change to a float - this may be required for appending data to the array
        array.append(decy)  # append it all together into a useful column of data
    return array  # return the new data

df = pd.read_excel(r'C:\Users\clewis\Desktop\test4.xlsx')  # export the file from RLIMS containing TW DATA

primary_standards = df.loc[df['AMS Category'] == 'Primary Standard OxI']  # grab all the OX-1's
# primary_standards.to_excel('test2.xlsx')
print("The types of OX-1's used in this wheel are as follows:")
print(np.unique(primary_standards['Category Field']))
print(np.unique(primary_standards['Sample Description2']))
print()

print("The average RTS of the Primary Standards in this wheel is")
prim_std_average = np.average(primary_standards['Ratio to standard'])
prim_std_1sigma = np.std(primary_standards['Ratio to standard'])
print("{} \u00B1 {}".format(prim_std_average, prim_std_1sigma))
print()

print("The average RTS of the OX-1 13C values in this wheel is")
prim_std_13average = np.average(primary_standards['delta13C_AMS'])
prim_std_13_1sigma = np.std(primary_standards['delta13C_AMS_Error'])
print("{} \u00B1 {}".format(prim_std_13average, prim_std_13_1sigma))
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

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# Let's find what types of samples are in this wheel.....
unknowns = df.dropna(subset='AMS Category')
unk_type_list = np.unique(unknowns['AMS Category'])

# CATEGORIZE THE SAMPLES BASED ON THEIR PRETREATMENT CATEGORY
AAA_array = []
cellulose_array = []
# Let's find what types of pre-treatments happened in this wheel:
for i in range(0, len(df)):   # start the loop for the length of the dataframe
    row = df.iloc[i]          # grab first row
    if row['Category In Calculation'] == 'Unknown Organic':
        pretreatment = df.iloc[i+1]
        pretreatment = pretreatment['Process Name']
        if pretreatment == 'Acid Alkali Acid':
            AAA_array.append(row)
        elif pretreatment == 'Cellulose Extraction':
            cellulose_array.append(row)

AAA = pd.DataFrame(AAA_array).reset_index(drop=True)
x = AAA['Date Run']
AAA['Date Run'] = long_date_to_decimal_date(x)
AAA['CorrectionType'] = 'AAA'


cellulose_array = pd.DataFrame(cellulose_array).reset_index(drop=True)
x = cellulose_array['Date Run']
cellulose_array['Date Run'] = long_date_to_decimal_date(x)
cellulose_array['CorrectionType'] = 'Cellulose'

unknowns = pd.concat([cellulose_array, AAA]).reset_index(drop=True)
unknowns.to_excel('categorized_samples.xlsx')

# CATEGORIZE THE HISTORICAL STANDARDS BASED ON THEIR PRETREATMENT CATEGORY
stds_hist = pd.read_excel(r'C:\Users\clewis\Desktop\hist_stds.xlsx')  # import historical standards data
AAA_standards = []
cellulose_standards = []
# Let's find what types of pre-treatments happened in this wheel:
for i in range(0, len(stds_hist)):   # start the loop for the length of the dataframe
    row = stds_hist.iloc[i]          # grab first row
    if row['Category In Calculation'] == 'Background Organic':
        pretreatment = stds_hist.iloc[i+1]
        pretreatment = pretreatment['Process Name']
        if pretreatment == 'Acid Alkali Acid':
            AAA_standards.append(row)
        elif pretreatment == 'Cellulose Extraction':
            cellulose_standards.append(row)

AAA_standards = pd.DataFrame(AAA_standards)
AAA_standards['Correction Type'] = 'AAA'

cellulose_standards = pd.DataFrame(cellulose_standards)
cellulose_standards['Correction Type'] = 'Cellulose'

chosen_stds = pd.concat([cellulose_standards, AAA_standards]).dropna(subset = 'Date Run').reset_index(drop=True)
x = chosen_stds['Date Run']                                                                               # next two lines convert run date to decimal date
chosen_stds['Date Run'] = long_date_to_decimal_date(x)
date_bound = max(chosen_stds['Date Run']) - 0.5                        # set time boundary as 0.5 year (~180 days) from the maximum date in the RLIMS file
chosen_stds = chosen_stds.loc[(chosen_stds['Date Run'] > date_bound)]                                           # index the data only in the date period that I want.
chosen_stds = chosen_stds.loc[(chosen_stds['Quality Flag'] != 'X..')]
chosen_stds = chosen_stds.loc[(chosen_stds['Weight Initial'] > 0.3)]

a = chosen_stds.loc[(chosen_stds['Correction Type'] == 'AAA')]
AAA_MCC = np.average(a['Ratio to standard'])
AAA_MCC_err = np.std(a['Ratio to standard'])
print("MCC correction applied to samples made using AAA pretreatment is: {} \u00B1 {}".format(AAA_MCC, AAA_MCC_err))

c = chosen_stds.loc[(chosen_stds['Correction Type'] == 'Cellulose')]
Cell_MCC = np.average(c['Ratio to standard'])
Cell_MCC_err = np.std(c['Ratio to standard'])
print("MCC correction applied to samples made using AAA pretreatment is: {} \u00B1 {}".format(Cell_MCC, Cell_MCC_err))

writer = pd.ExcelWriter('Results.xlsx', engine='openpyxl')
AAA.to_excel(writer, sheet_name='Unknowns (AAA)')
cellulose_array.to_excel(writer, sheet_name='Unknowns (Cellulose)')
a.to_excel(writer, sheet_name='Standards (AAA)')
c.to_excel(writer, sheet_name='Standard (Cellulose)')
writer.save()

















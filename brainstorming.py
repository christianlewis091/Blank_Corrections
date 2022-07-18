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

import pandas as pd
import numpy as np
import openpyxl
df = pd.read_excel(r'C:\Users\clewis\Desktop\test4.xlsx')  # export the file from RLIMS

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
C13_threshold = 0.01
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

print("The following standards are outside the selected range of {} per mil difference between IRMS and AMS 13C".format(C13_threshold))
print(result)









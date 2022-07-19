"""
This blank correction is based on the wheel TW3416 which contained the following sets of samples:

Wood
Plant
Water

Let's see if we can get the same results as that which we corrected the normal way today.

"""
import pandas as pd
import numpy as np

"""
This script is written to use a specific output file from RLIMS which includes exported data from the tables:
"Process List"
"AMS Submission Results Complete"
"""
df = pd.read_excel(r'C:\Users\clewis\Desktop\3416_2.xlsx')  # export the file from RLIMS containing TW DATA

# <editor-fold desc="Primary Standard Quality Check">
"""
First, lets check how the OX-1's performed. 
"""
primary_standards = df.loc[df['AMS Category ID XCAMS'] == 'OxI']  # grab all the OX-1's
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



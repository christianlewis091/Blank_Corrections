"""
This blank correction is based on the wheel TW3416 which contained the following sets of samples:

Wood
Plant
Water

Let's see if we can get the same results as that which we corrected the normal way today.

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

"""
The first thing I want to do is "pre-process" the file. I want to get the pre-treatment data in the same line as 
the data I want, and drop ALLLL the unnecessary columns I don't want. This process is complicated by the fact that the pre-processing information
is not delivered in a constant way in the excel file, based on how much data for pre-processing exists. Where is the chemical pre-treatement, the 
first row, the second row? its unknown. 
"""
# add the pre-treatment Process Name to line,
# then drop all NaN's on AMS category.

cat_index = np.linspace(0, len(df)-1, len(df))
df['cat_index'] = cat_index                           # add an indexing category to help me deal with isolating chemical preprocessing
df = df[['cat_index', 'AMS Category ID XCAMS', 'Process Name','Category In Calculation','delta13C_IRMS','delta13C_IRMS_Error','delta13C_AMS','delta13C_AMS_Error','Ratio to standard','Ratio to standard error']]                                           # simplify my life by only keeping the columns I need while I code this project
df['AMS Category ID XCAMS'] = df['AMS Category ID XCAMS'].fillna(0)
# df.to_excel('test.xlsx')

indexing_array = []
for i in range(0, len(df)):
    row = df.iloc[i]
    cat = row['AMS Category ID XCAMS']
    if cat != 0:
        indexing_array.append(row['cat_index'])
finalrow = df.iloc[-1]
finalcat = finalrow['cat_index']
indexing_array.append(finalcat)
print(indexing_array)
print(len(indexing_array))

mt_array2 = []
for i in range(0, 40):
    row = df.iloc[int(indexing_array[i])]
    x = df.iloc[int(indexing_array[i]):int(indexing_array[i+1])]
    x = x['Process Name']
    x = list(x)
    print(x)
    for k in range(0, len(processes)):
        y = processes[k]
        print(y)
        if y in x:   # if the item in the list of processes I'm searching for is in the list from RLIMS,
            row['Cleaned PreProcess Information'] = y   # add this item onto a new row of the dataframe
            mt_array2.append(row)

cleaneddf = pd.DataFrame(mt_array2)
cleaneddf = cleaneddf.dropna(subset='AMS Category ID XCAMS')


cleaneddf.to_excel('diditworkdiditwork.xlsx')









# mt_array = []
# for i in range(0, len(df)-1):
#     row = df.iloc[i]          # grab a row
#     pretreatment_row = df.iloc[i+1]
#     pretreatment = pretreatment_row['Process Name']
#     row['test'] = pretreatment
#     mt_array.append(row)
#
# df = pd.DataFrame(mt_array)
# df = df.dropna(subset='AMS Category ID XCAMS').reset_index(drop=True)
# df.to_excel('testingggggg.xlsx')
#
# # What columns do I want to keep?
# # df = [[]]
#
#
#













#
# # <editor-fold desc="Primary Standard Quality Check">
# """
# First, lets check how the OX-1's performed.
# """
# primary_standards = df.loc[df['AMS Category ID XCAMS'] == 'OxI']  # grab all the OX-1's
# print("The OX-1 category is {}, and the description is {}.".format(np.unique(primary_standards['Category Field']),
#                                                                    np.unique(primary_standards['Description from Sample'])))
#
# prim_std_average = np.average(primary_standards['Ratio to standard'])
# prim_std_1sigma = np.std(primary_standards['Ratio to standard'])
# rounding_decimal = 3
# # Note: if the rounding decimal is around 3, but the result comes out to 1.0, this is because it has rounded up from 0.99999 or so, for example.
# print("The average RTS of the Primary Standards in this wheel is {} \u00B1 {}".format(round(prim_std_average, rounding_decimal),
#                                                                                       round(prim_std_1sigma, rounding_decimal)))
#
# prim_std_13average = np.average(primary_standards['delta13C_AMS'])
# prim_std_13_1sigma = np.std(primary_standards['delta13C_AMS'])
# print("The average RTS of the OX-1 13C values in this wheel is {} \u00B1 {}".format(round(prim_std_13average, rounding_decimal),
#                                                                                     round(prim_std_13_1sigma, rounding_decimal)))
# print()
# # Do any of the OX-1's deviate from their IRMS number?
# # Compare 13C AMS to 13C IRMS
#
# arr1 = []  # initialize a few empty arrays for later use
# arr2 = []
# C13_threshold = 2
# for i in range(0, len(primary_standards)):
#     row = primary_standards.iloc[i]         # access the first row
#     ams = row['delta13C_AMS']
#     ams_err = row['delta13C_AMS_Error']
#     irms = row['delta13C_IRMS']
#     irms_error = row['delta13C_IRMS_Error']
#     delta = abs(ams - irms)
#
#     if delta >= C13_threshold:
#         arr1.append(delta)
#         arr2.append(row['TP'])
#
# result = pd.DataFrame({"TP": arr2, "Absolute value, (AMS - IRMS 13C)": arr1})
# if len(result) > 0:
#     print("The following standards are outside the selected range of {}\u2030 difference between IRMS and AMS 13C".format(C13_threshold))
#     print(result)
# print()
# # </editor-fold>
#
# Let's index the wheel based on sample type, and then, sample pre-treatment.
df = pd.read_excel(r'C:\Users\clewis\Desktop\3416_2.xlsx')  # export the file from RLIMS containing TW DATA

# # Let's find what types of samples and pre-treatments are in this wheel.....
# unknowns = df.dropna(subset='AMS Category ID XCAMS')
# unk_type_list = np.unique(unknowns['AMS Category ID XCAMS'])
#
# mt_array = []
# process_array = []
# for i in range(0, len(processes)):
#     process = processes[i]
#     for k in range(0, len(df)-1):
#         row = df.iloc[k]                  # grab the first row
#         pretreatment_row = df.iloc[k+1]
#         if pretreatment_row['Process Name'] == process:
#             print(process)
#             mt_array.append(row)
#             process_array.append(process)
#
# #
# #
#







    #
    #
    # if row['Category In Calculation'] == 'Unknown Organic':
    #     pretreatment = df.iloc[i+1]
    #     pretreatment = pretreatment['Process Name']
    #     if pretreatment == 'Acid Alkali Acid':
    #         AAA_array.append(row)
    #     elif pretreatment == 'Cellulose Extraction':
    #         cellulose_array.append(row)
    #
    #
    #
    #
    #
    #
    #
    #












# print("This wheel contains the following types of samples {}".format(unk_type_list))






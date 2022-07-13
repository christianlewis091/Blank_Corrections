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

import pandas as pd
import openpyxl
df = pd.read_excel(r'H:\The Science\Current Projects\Blank Correction Streamlining\Brainstorm.xlsx', nrows=40)

# FIND ALL THE PRIMARY STANDARDS:
primary_std = df.loc[(df['Type'] == 'Primary Standard')]
secondary_std = df.loc[(df['Type'] == 'Secondary')]
blank = df.loc[(df['Type'] == 'Blank')]
unknown = df.loc[(df['Type'] == 'Unknown')]



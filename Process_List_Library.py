"""
Here I want to keep a log all the processes "NAMES" and the "R-NUMBER associated with them so I can easily index
through data for blank correction.
This is an ongoing project and will likely not be polished for a while
"""
import pandas as pd

# GB = graphite background
# CBIn = Combustion Blank inorganic (Carrera Marble)
# CBOr = Combustion Blank Organic (Kauri)
# OxI = primary standard
# UNSt = unknown as standard
# UNIn = unknown inorganic
# UNOr = unknown organic
category_list = ['GB', 'CBIn','CBOr','OxI','UNSt', 'UNIn','UNOr']

# Put in here the list of processes that I want to check for in order to correct samples.
processes = ['Water CO2 Evolution','Cellulose Extraction','Acid Alkali Acid','AMS Submission Results']

# processes = pd.DataFrame({ "Water Carbonate CO2 Evolution": '14047/11',
#                            "Cellulose Extraction": '40142/1',
#                            "Acid Alkali Acid":     '40142/2'
#                            })
secondaries = ['FIRI-D: wood', 'LAC1 coral', 'LAA1 coral']
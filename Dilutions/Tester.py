import numpy as np
import pandas as pd

# #  setting variables
target_con = 10

# importing excel file
# concentrations = np.loadtxt("Concentrations.csv", dtype=float)
csv_raw = '''
125
83
65
111
16
53
20
73
'''
csv_data = csv_raw.splitlines()[1:]
concentrations = np.array(csv_data, dtype=float)
print(concentrations)
# #  importing data and creating necessary arrays
sample_num = len(concentrations)
sample_num_array = np.empty([sample_num], dtype=float)
water_array = np.empty([sample_num], dtype=float)
DNA_array = np.empty([sample_num], dtype=float)


for i in range(0, sample_num):
    sample_num_array[i] = i + 1
# # Filling in arrays for the machine to know how much water and sample is needed
for i in range(0, sample_num):
    dna = round(100 * target_con / concentrations[i], 2)
    water = 100 - dna
    DNA_array[i] = dna
    water_array[i] = water

# # Combining all the data into one big data frame
big_data = pd.DataFrame(np.column_stack((sample_num_array, DNA_array, water_array)))

# # Splitting the data frame so machine does p20
print(DNA_array)
print(water_array)
print(sample_num_array)
print(big_data)

print(big_data[0][1])
# Make samples correspond to a number.
# Do calculations, for every water that needs more than 20 increase a variable by 1. Make samples correspond to a number.
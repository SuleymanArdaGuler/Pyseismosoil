import numpy as np

def read_exp(line):
    parts = line.split(',')

    # Iterate over the parts to find the one containing DT
    dt_part = None
    for part in parts:
        if 'DT' in part:
            dt_part = part
            break
    
    # If DT part is found, extract the value
    if dt_part:
        dt_value = dt_part.split('=')[-1].strip()
        numerical_dt = dt_value.split()[0]
    return float(numerical_dt)

def read_file(file_name):
    # Line number to start reading from
    start_line = 4

    # Initialize an empty list to store the data
    data = []

    # Open the text file for reading
    with open(file_name, 'r') as file:
        # Read all lines from the file starting from the desired line
        lines = file.readlines()[start_line-1:]
        exp_line = lines[0]
        
        # Iterate over each line in the file
        for line in lines[1:]:
            # Split the line into individual values (assuming values are separated by spaces)
            values = line.split()
            for value in values:
            # Convert each value to a floating-point number and append it to the data list
 
                data.append(value)
    
    # Convert the data list into a NumPy array
    data_array = np.array(data,dtype=float)
    # Now you can work with the data_array using NumPy functions and operations
    return data_array,read_exp(exp_line)

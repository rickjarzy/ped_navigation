import pandas as pd
import numpy

# Paul Arzberger
# 00311430
# 2nd Lab - Navigation Systems - WS18/19
# function file

def create_data_matrix(input_txt_path):
    """
    This function reads out the txt file which path is given by the input_txt_path variable. the header will be
    read out seperatly and the rest of the data is extracted by a for loop.
    only the pandas dataframe, which header (columns) get rearanged by alphabet, rows stay the same.
    the rows are stored as key value pair, where the key is the [ms] info from the txt file and the values are the
    data seperated by whitespace

    :param input_txt_path:  the path to the data.txt file which should be read out
    :return:                the data from the data.txt file stored in a pandas data frame
    """

    data = dict()

    # read out data and store it onto a pandas dataframe
    with open(input_txt_path, "r") as data_file:
        header = data_file.readline().split("\n")[0].split()    # read out the header and store it as a list
        #print(header)
        for line in data_file:                                  # walk through the txt file and read out each line
            #print(line)

            line = line.split("\n")[0].split()                  # store each line as list and split it by blank space
            data[line[0]] = {header[1]: float(line[1]),         # store each value of the line in a dict with the time as key and the rest as values - reusing the header
                             header[2]: float(line[2]),         # ATTENTION! - the pandas dataframe rearenages the data by sorting it by alphabet!
                             header[3]: float(line[3]),
                             header[4]: float(line[4]),
                             header[5]: float(line[5]),
                             header[6]: float(line[6]),
                             header[7]: float(line[7]),
            }


    data = pd.DataFrame.from_dict(data).T
    return data
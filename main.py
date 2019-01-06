import pandas as pd
import numpy
import scipy
from matplotlib import pyplot as plt
import sys
import pdr_functions

# Paul Arzberger
# 00311430
# Navigation Systems - 2nd Lab Pedestrian Navigation - WS18/19
# main file

def outlier_detection(input_array):


    median = numpy.nanmedian(input_array)               # get the median of the input array
    dist_median = numpy.absolute(input_array - median)  # array where the input data is subtracted with the median


    if numpy.max(dist_median) > 0.5:
        print("- Median: ", median)
        print("- max dist_median: ", numpy.max(dist_median))
        print("- data: \n", input_array)

        return 1

def median_filter(input_array):


    pass

if __name__ == "__main__":

    # startpoint
    phi = 47.06427                  # [°]
    lam = 15.45313                  # [°]

    print(sys.argv)     # checking if some extra input from the cmd comes in

    print("======================================\n Pedestrian Navigation - Lab 2 \n======================================\n")
    # store the txt data onto a pandas dataframe
    data = pdr_functions.create_data_matrix(r"data.txt")

    # outlier detection
    print("Outlier detection Median Distance Test")
    median_window_size = 30
    sub_data = data["baro"]
    count_outlier = 0
    for sub_data in range(0,len(data["baro"]),median_window_size):

        check_sum = outlier_detection(data["baro"][sub_data:sub_data + median_window_size])

        if check_sum == 1:
            count_outlier += 1

    print("Sum outlier: ", count_outlier)

    # plotting the data
    time = data["time"].tolist()
    fig = plt.figure()
    ax = fig.add_subplot(211, frameon=True)
    plt.title("NavSys - Accelerometer and Magnometer Data")
    plt.plot(time, data["acc_total"].tolist(), label="acc total")
    plt.plot(time, data["a_x"].tolist(), label="acc x")
    plt.plot(time, data["a_y"].tolist(), label="acc y")
    plt.plot(time, data["a_z"].tolist(), label="acc z")

    plt.plot(time, data["m_x"].tolist(), label="m_x")
    plt.plot(time, data["m_y"].tolist(), label="m_y")
    plt.plot(time, data["m_z"].tolist(), label="m_z")
    plt.grid(True)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)

    ax2 = fig.add_subplot(212, frameon=True)
    plt.title("NavSys - Barometer Data raw")
    plt.plot(time, data["baro"].tolist(), label="baro")
    plt.grid(True)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)

    plt.show()

    print("\n======================================\nProgramm ENDE")
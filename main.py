import pandas as pd
import numpy
from matplotlib import pyplot as plt
import sys
import pdr_functions
# Paul Arzberger
# 00311430
# Navigation Systems - 2nd Lab Pedestrian Navigation - WS18/19
# main file



if __name__ == "__main__":

    # startpoint
    phi = 47.06427                  # [°]
    lam = 15.45313                  # [°]

    print(sys.argv)     # checking if some extra input from the cmd comes in

    print("======================================\n Pedestrian Navigation - Lab 2 \n======================================\n")
    # store the txt data onto a pandas dataframe
    data = pdr_functions.create_data_matrix(r"data.txt")


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
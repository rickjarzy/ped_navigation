import pandas as pd
import numpy
from scipy import signal
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

    # filter raw data and store it on seperate Series
    data["a_x_filtered"] = signal.savgol_filter(data["a_x"], 7, 2)
    data["a_y_filtered"] = signal.savgol_filter(data["a_y"], 7, 2)
    data["a_z_filtered"] = signal.savgol_filter(data["a_z"], 7, 2)
    data["acc_total_filtered"] = numpy.sqrt(data["a_x_filtered"]**2 + data["a_y_filtered"]**2 + data["a_z_filtered"]**2)
    data["baro_median_filt"] = signal.medfilt(signal.medfilt(data["baro"], 41), 83)

    data_savgol_filt = signal.savgol_filter(data["baro_median_filt"].tolist(), 601, 2)
    data["data_savgol_filt"] = data_savgol_filt

    data["m_x_filtered"] = signal.savgol_filter(data["m_x"], 61, 2)
    data["m_y_filtered"] = signal.savgol_filter(data["m_y"], 61, 2)
    data["m_z_filtered"] = signal.savgol_filter(data["m_z"], 61, 2)

    # find peaks
    peaks = signal.find_peaks(data["acc_total_filtered"])

    print(peaks)

    # three steps for PDR
    # 1. step detection
    # 2. step length estimation
    # 3. step direction estimation





    # plotting the data
    # ==================================================================================================================

    time = data["time"].tolist()
    fig = plt.figure(1)
    ax = fig.add_subplot(211, frameon=True)
    plt.title("NavSys - Accelerometer Data")
    plt.plot(time, data["acc_total"], label="acc total")
    plt.plot(time, data["a_x"], label="acc x")
    plt.plot(time, data["a_x_filtered"], label="acc x filtered")
    plt.plot(time, data["a_y"], label="acc y")
    plt.plot(time, data["a_y_filtered"], label="acc y filtered")
    plt.plot(time, data["a_z"], label="acc z")
    plt.plot(time, data["a_z_filtered"], label="acc z filtered")
    plt.plot(time, data["acc_total_filtered"], label="acc total components sav gol filtered")
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)

    ax2 = fig.add_subplot(212, frameon=True)
    plt.title("NavSys - Magnetometer Data")
    plt.plot(time, data["m_x"], label="m_x")
    plt.plot(time, data["m_x_filtered"], label="m_x_filtered")
    plt.plot(time, data["m_y"], label="m_y")
    plt.plot(time, data["m_y_filtered"], label="m_y_filtered")
    plt.plot(time, data["m_z"], label="m_z")
    plt.plot(time, data["m_z_filtered"], label="m_z_filtered")
    plt.grid(True)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)

    fig = plt.figure(2)

    ax3 = fig.add_subplot(211, frameon=True)
    plt.title("NavSys - Barometer Data raw")
    plt.plot(time, data["baro"], label="baron raw")
    plt.plot(time, data["baro_median_filt"], label="baro median filtered")
    plt.grid(True)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)


    ax4 = fig.add_subplot(212, frameon=True)
    plt.title("NavSys - Baro Filtering")
    plt.plot(time, data["baro_median_filt"], label="baro median filtered")
    plt.plot(time, signal.medfilt(data["data_savgol_filt"], 83), label="baro savgol filtered")
    plt.grid(True)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)

    plt.show()


    print("\n======================================\nProgramm ENDE")
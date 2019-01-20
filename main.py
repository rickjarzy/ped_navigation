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
    data["a_x_filtered"] = signal.savgol_filter(data["a_x"], 13, 2)
    data["a_y_filtered"] = signal.savgol_filter(data["a_y"], 13, 2)
    data["a_z_filtered"] = signal.savgol_filter(data["a_z"], 13, 2)
    data["acc_total_filtered"] = numpy.sqrt(data["a_x_filtered"]**2 + data["a_y_filtered"]**2 + data["a_z_filtered"]**2)
    data["baro_median_filt"] = signal.medfilt(signal.medfilt(data["baro"], 41), 83)
    data["height"] = (288.15/0.0065) * (1- (data["baro_median_filt"]/1013.25)**(1/5.255))

    data_savgol_filt = signal.savgol_filter(data["baro_median_filt"].tolist(), 601, 2)
    data["baro_savgol_filt"] = signal.medfilt(data_savgol_filt, 83)
    data["height_savgol"] = (288.15 / 0.0065) * (1 - (data["baro_savgol_filt"] / 1013.25) ** (1 / 5.255))


    data["m_x_filtered"] = signal.savgol_filter(data["m_x"], 61, 2)
    data["m_y_filtered"] = signal.savgol_filter(data["m_y"], 61, 2)
    data["m_z_filtered"] = signal.savgol_filter(data["m_z"], 61, 2)

    # three steps for PDR
    # 1. step detection

        # find max peaks
    peaks = signal.find_peaks(data["acc_total_filtered"], height=10.5, distance=15)
    indizes_peaks_max = peaks[0]
    print(data.at[str(584), "time"])
    indizes_p_min_heading = indizes_peaks_max
    time_peaks_max = [data.at[str(index), "time"] for index in indizes_peaks_max]
    data_peaks_max = peaks[1]["peak_heights"]
    print("len data_peaks_max", len(data_peaks_max))

        # argrelmin
    peaks_min = signal.argrelmin(data["acc_total_filtered"].values, order=15)   # !!! FIND ALL Min PEAKS
    indizes_peaks_min = peaks_min[0]
    print("len min peaks: ", len(indizes_peaks_min))
    indizes_p_min_heading = [index for index in indizes_peaks_min if data.at[str(index), "acc_total_filtered"] < 10]
    time_peaks_min = [data.at[str(index), "time"] for index in indizes_peaks_min if data.at[str(index), "acc_total_filtered"] < 10]               # just take those with a reasonable threshold
    data_peaks_min = [data.at[str(index), "acc_total_filtered"] for index in indizes_peaks_min if data.at[str(index), "acc_total_filtered"] < 10] # just take those with a reasonable threshold
    print("len time_peaks min: ", len(time_peaks_min))
    print("len indizes min heading: ", len(indizes_p_min_heading))
    # 2. step length estimation
    step_fix = 0.6  # [m]       fixed value from the angabeblatt


    # 3. step direction estimation
        # formulars from angabeblatt
    data["roll"] = numpy.arctan2(-data["a_y_filtered"],  -data["a_z_filtered"])
    data["pitch"] = numpy.arctan2(data["a_x_filtered"], numpy.sqrt( data["a_y_filtered"]**2 + data["a_z_filtered"]**2 ))

        # calculate the yaw angle - HEADING
    gegen_kath = -data["m_y_filtered"] * numpy.cos(data["pitch"]) + data["m_z_filtered"] * numpy.sin(data["roll"])
    an_kath = data["m_x_filtered"] * numpy.cos(data["pitch"]) + data["m_y_filtered"] * numpy.sin(data["pitch"]) * numpy.sin(data["roll"] + data["m_z_filtered"] * numpy.sin(data["pitch"]) * numpy.cos(data["roll"]))
    data["yaw_mag"] = numpy.arctan2(gegen_kath , an_kath)



    # plotting the data
    # ==================================================================================================================

    time = data["time"].tolist()
    fig = plt.figure(1)
    ax11 = fig.add_subplot(311, frameon=True)
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

    ax12 = fig.add_subplot(312, frameon=True)
    plt.title("NavSys - Magnetometer Data")
    plt.plot(time, data["m_x"], label="m_x")
    plt.plot(time, data["m_x_filtered"], label="m_x_filtered")
    plt.plot(time, data["m_y"], label="m_y")
    plt.plot(time, data["m_y_filtered"], label="m_y_filtered")
    plt.plot(time, data["m_z"], label="m_z")
    plt.plot(time, data["m_z_filtered"], label="m_z_filtered")
    plt.grid(True)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)

    ax13 = fig.add_subplot(313, frameon=True)
    plt.title("NavSys - Find Peaks")
    #plt.plot(time, data["acc_total"], label="acc total")
    plt.plot(time, data["acc_total_filtered"], label="acc total components sav gol filtered")
    plt.plot(time_peaks_max, data_peaks_max, label="Peaks Acc Total Max", marker='^', markerfacecolor='red', markersize=6)
    plt.plot(time_peaks_min, data_peaks_min, label="Peaks Acc Total Min", marker='^', markerfacecolor='green', markersize=6)
    plt.grid(True)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)

    # fig 2
    # ==============================================
    fig = plt.figure(2)

    ax21 = fig.add_subplot(311, frameon=True)
    plt.title("NavSys - Barometer Data raw")
    plt.plot(time, data["baro"], label="baron raw")
    plt.plot(time, data["baro_median_filt"], label="baro median filtered")

    plt.grid(True)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)

    ax22 = fig.add_subplot(312, frameon=True)
    plt.title("NavSys - Baro Filtering")

    plt.plot(time, data["baro_median_filt"], label="baro median filtered")
    plt.plot(time, data["baro_savgol_filt"], label="baro savgol and median filtered")
    plt.grid(True)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)

    ax23 = fig.add_subplot(313, frameon=True)
    plt.title("NavSys - Höhe")
    plt.plot(time, data["height"], label="höhe aus baro_median")
    plt.plot(time, data["height_savgol"], label="höhe aus baro_savgol")
    plt.grid(True)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)


    # fig 3
    # ==============================================
    fig = plt.figure(3)
    ax31 = fig.add_subplot(311, frameon=True)
    plt.title("NavSys - roll and pitch angle out of a_y and a_z")
    plt.plot(time, data["roll"], label="roll angle")
    plt.plot(time, data["pitch"], label="pitch angle")
    plt.plot(time, data["yaw_mag"], label="yaw magnetic angle")
    plt.grid(True)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)

    plt.show()
    print("\n======================================\nProgramm ENDE")
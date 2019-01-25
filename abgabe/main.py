import pandas as pd
import numpy
from scipy import signal, ndimage, stats
from matplotlib import pyplot as plt
from matplotlib import patches
import sys
import pdr_functions

# Paul Arzberger
# 00311430
# Navigation Systems - 2nd Lab Pedestrian Navigation - WS18/19
# main file


if __name__ == "__main__":

    # startpoint
    phi_rad = 47.06427 * (numpy.pi / 180) # [rad]
    lam_rad = 15.45313 * (numpy.pi / 180) # [rad]

    phi_deg = 47.06427
    lam_deg = 15.45313

    print(sys.argv)     # checking if some extra input from the cmd comes in

    print("======================================\n Pedestrian Navigation - Lab 2 \n======================================\n")
    # store the txt data onto a pandas dataframe
    data = pdr_functions.create_data_matrix(r"data.txt")

    # filter raw data and store it on seperate Series using median and Savitzky Golay filters with different Moving windows
    # till the data looks fine
    data["a_x_filtered"] = signal.savgol_filter(data["a_x"], 13, 2)
    data["a_y_filtered"] = signal.savgol_filter(data["a_y"], 13, 2)
    data["a_z_filtered"] = signal.savgol_filter(data["a_z"], 13, 2)
    data["acc_total"] = numpy.sqrt(data["a_x"]**2 + data["a_y"]**2 + data["a_z"]**2)
    data["acc_total_filtered"] = numpy.sqrt(data["a_x_filtered"]**2 + data["a_y_filtered"]**2 + data["a_z_filtered"]**2)
    data["baro_median_filt"] = signal.medfilt(signal.medfilt(data["baro"], 41), 83)
    data["height"] = (288.15/0.0065) * (1- (data["baro_median_filt"]/1013.25)**(1/5.255))

    data_savgol_filt = signal.savgol_filter(data["baro_median_filt"].tolist(), 601, 2)
    data["baro_savgol_filt"] = signal.medfilt(data_savgol_filt, 83)
    data["height_savgol"] = (288.15 / 0.0065) * (1 - (data["baro_savgol_filt"] / 1013.25) ** (1 / 5.255))


    data["m_x_filtered"] = signal.savgol_filter(data["m_x"], 81, 2)
    data["m_y_filtered"] = signal.savgol_filter(data["m_y"], 81, 2)
    data["m_z_filtered"] = signal.savgol_filter(data["m_z"], 81, 2)

    # step classification

    data["slope_height"] = ndimage.filters.generic_filter(input=data["height_savgol"], function=pdr_functions.LinReg, size=500 )
    data["step_size"] = numpy.where(data["slope_height"] < 0.001, 0.6, 0.3)
    print(data["slope_height"])

    # three steps for PDR
    # 1. step detection

        # find max peaks
    peaks = signal.find_peaks(data["acc_total_filtered"], height=10.5, distance=15)
    indizes_peaks_max = peaks[0]
    print(data.at[str(584), "time"])
    indizes_p_max_heading = indizes_peaks_max
    time_peaks_max = [data.at[str(index), "time"] / 1000 for index in indizes_peaks_max]
    data_peaks_max = peaks[1]["peak_heights"]
    print("len data_peaks_max", len(data_peaks_max))

        # argrelmin
    peaks_min = signal.argrelmin(data["acc_total_filtered"].values, order=15)   # !!! FIND ALL Min PEAKS
    indizes_peaks_min = peaks_min[0]
    print("len min peaks: ", len(indizes_peaks_min))
    indizes_p_min_heading = [index for index in indizes_peaks_min if data.at[str(index), "acc_total_filtered"] < 10]
    time_peaks_min = [data.at[str(index), "time"] / 1000 for index in indizes_peaks_min if data.at[str(index), "acc_total_filtered"] < 10]               # just take those with a reasonable threshold
    data_peaks_min = [data.at[str(index), "acc_total_filtered"] for index in indizes_peaks_min if data.at[str(index), "acc_total_filtered"] < 10] # just take those with a reasonable threshold
    print("len time_peaks min: ", len(time_peaks_min))
    print("len indizes min heading: ", len(indizes_p_min_heading))

    # 2. step length estimation
    step_fix = 0.6  # [m]       fixed value from the angabeblatt


    # 3. step direction estimation
        # formulars from angabeblatt
    data["roll_raw"] = numpy.arctan2(-data["a_y_filtered"],  -data["a_z_filtered"])
    data["pitch_raw"] = numpy.arctan2(data["a_x_filtered"], numpy.sqrt( data["a_y_filtered"]**2 + data["a_z_filtered"]**2 ))

    data["roll_med"] = signal.medfilt(data["roll_raw"], 51)
    data["pitch_med"] = signal.medfilt(data["pitch_raw"], 51)
    data["roll"] = signal.savgol_filter(data["roll_med"], 51,2)
    data["pitch"] = signal.savgol_filter(data["pitch_med"], 51, 2)

        # calculate the yaw angle - HEADING
    gegen_kath = -data["m_y_filtered"] * numpy.cos(data["roll"]) + data["m_z_filtered"] * numpy.sin(data["roll"])
    an_kath = data["m_x_filtered"] * numpy.cos(data["pitch"]) + data["m_y_filtered"] * numpy.sin(data["pitch"]) * numpy.sin(data["roll"]) + data["m_z_filtered"] * numpy.sin(data["pitch"]) * numpy.cos(data["roll"])

    data["yaw_mag"] = numpy.arctan2(gegen_kath , an_kath)
    data["yaw_mag_median"] = signal.medfilt(data["yaw_mag"],15)
    data["yaw_mag_sgf"] = signal.savgol_filter(data["yaw_mag_median"], 81,3)

        #subdata yaw - HEADING
    data_sub_yaw = data["yaw_mag"].iloc[indizes_p_min_heading]
    data_sub_step = data["step_size"].iloc[indizes_p_min_heading]
    #print("data sub yaw\n", data_sub_yaw)


    north_delta = data_sub_step * numpy.cos(data_sub_yaw)        # later on transformed to d_phi
    east_delta = data_sub_step * numpy.sin(data_sub_yaw)

    #north_delta = step_fix * numpy.cos(data_sub_yaw)  # later on transformed to d_phi
    #east_delta = step_fix * numpy.sin(data_sub_yaw)

    #print("north_delta\n", north_delta)

    # transformation to geographic koordinates
    # sperical aproximation --> rel pos to geographic coordinates
    # ============================================================
    R = 6378137 # Radius in [m]
    d_phi = north_delta / R                        #   [rad] - reform ... dx = R * d_phi
    d_lam = east_delta / (R * numpy.cos(phi_rad))      #   [rad] - reform ... dy = R * cos(phi) * d_lam

    # sum up all timeepochs to represent the walked trajektory
    d_phi_deg = d_phi * (180 / numpy.pi)            # [°]
    d_lam_deg = d_lam * (180 / numpy.pi)            # [°]

    d_phi_deg_csum = numpy.cumsum(d_phi_deg)
    d_lam_deg_csum = numpy.cumsum(d_lam_deg)

    phi_traj = d_phi_deg_csum + phi_deg
    lam_traj = d_lam_deg_csum + lam_deg

    #pdr_functions.write_phi_lam_txt(phi_traj, lam_traj, data_sub_step,  "min_peaks_all_sensors_filtered_yaw_sgf_dyn_stepsize")


    # plotting the data
    # ==================================================================================================================

    time = [timestamp / 1000 for timestamp in data["time"].tolist()]          # [ms] -->[sec]
    fig = plt.figure(1)
    #ax11 = fig.add_subplot(211, frameon=True)
    plt.title("NavSys - Accelerometer Data")
    plt.plot(time, data["acc_total"], label="acc total", linewidth=3)
    plt.plot(time, data["acc_total_filtered"], label="acc total SG fit", linewidth=3)
    plt.xlabel("Time [sec]")
    plt.ylabel("Acceleration [m/s²]")
    #plt.legend()
    #plt.plot(time, data["a_x"], label="acc x raw")
    #plt.plot(time, data["a_x_filtered"], label="acc x SG fit")
    #plt.plot(time, data["a_y"], label="acc y raw")
    #plt.plot(time, data["a_y_filtered"], label="acc y SG fit")
    #ax11 = fig.add_subplot(212, frameon=True)
    #plt.plot(time, data["a_z"], label="acc z raw")
    #plt.plot(time, data["a_z_filtered"], label="acc z SG fit")

    #plt.xlabel("Time [sec]")
    #plt.ylabel("Acceleration [m/s²]")
    #plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
    plt.legend()

    fig = plt.figure(2)
    #ax12 = fig.add_subplot(312, frameon=True)
    plt.title("NavSys - Magnetometer Data")
    plt.plot(time, data["m_x"], label="mag x raw", linewidth=3)
    plt.plot(time, data["m_x_filtered"], label="mag x SG fit", linewidth=3)
    plt.plot(time, data["m_y"], label="mag y raw", linewidth=3)
    plt.plot(time, data["m_y_filtered"], label="mag y SG fit", linewidth=3)
    plt.plot(time, data["m_z"], label="mag z raw", linewidth=3)
    plt.plot(time, data["m_z_filtered"], label="mag z SG fit", linewidth=3)
    plt.grid(True)
    plt.xlabel("Time [sec]")
    plt.ylabel("[μT]")      # mikrotesla
    #plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
    plt.legend()

    fig = plt.figure(3)
    #ax13 = fig.add_subplot(313, frameon=True)
    plt.title("NavSys - Find Peaks")
    #plt.plot(time, data["acc_total"], label="acc total")
    plt.plot(time, data["acc_total_filtered"], label="Acc total out of SG filtered components")
    plt.plot(time_peaks_max, data_peaks_max, label="Peaks Acc Total Max", marker='^', markerfacecolor='red', markersize=6,  linewidth=3)
    plt.plot(time_peaks_min, data_peaks_min, label="Peaks Acc Total Min", marker='^', markerfacecolor='green', markersize=6,  linewidth=3)
    plt.grid(True)
    plt.xlabel("Time [sec]")
    plt.ylabel("Accelerations total [m/s²]")
    #plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
    plt.legend()

    # fig 2
    # ==============================================
    fig = plt.figure(4)

    #ax21 = fig.add_subplot(311, frameon=True)
    plt.title("NavSys - Barometer Data raw")
    plt.plot(time, data["baro"], label="Barometer data raw",  linewidth=3)
    plt.plot(time, data["baro_median_filt"], label="Barometer median fit",  linewidth=3)
    plt.xlabel("Time [sec]")
    plt.ylabel("Preausre [hPa]")
    plt.grid(True)
    #plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
    plt.legend()

    fig = plt.figure(5)
    #ax22 = fig.add_subplot(312, frameon=True)
    plt.title("NavSys - Baro Filtering")
    plt.xlabel("Time [sec]")
    plt.ylabel("Preausre [hPa]")
    plt.plot(time, data["baro_median_filt"], label="Barometer median fit",  linewidth=3)
    plt.plot(time, data["baro_savgol_filt"], label="Barometer fit with Median and SG",  linewidth=3)
    plt.grid(True)
    #plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
    plt.legend()

    fig = plt.figure(6)
    #ax23 = fig.add_subplot(313, frameon=True)
    plt.title("NavSys - Height")
    plt.plot(time, data["height"], label="Height out of Barometer median fit",  linewidth=3)
    plt.plot(time, data["height_savgol"], label="Height out of Barometer SG fit",  linewidth=3)
    plt.grid(True)
    plt.xlabel("Time [sec]")
    plt.ylabel("Elevation [m]")
    #plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
    plt.legend()


    # fig 3
    # ==============================================
    fig = plt.figure(7)
    #ax31 = fig.add_subplot(311, frameon=True)
    plt.title("NavSys - Roll and Pitch angle out of a_y and a_z with different filter methods")
    plt.plot(time, data["roll_raw"], label="roll angle raw data",  linewidth=3)
    plt.plot(time, data["roll_med"], label="roll angle med fit", linewidth=3)
    plt.plot(time, data["roll"], label="roll angle SG fit", linewidth=3)
    plt.plot(time, data["pitch_raw"], label="pitch angle raw data",  linewidth=3)
    plt.plot(time, data["pitch_med"], label="pitch angle med fit", linewidth=3)
    plt.plot(time, data["pitch"], label="pitch angle SG fit", linewidth=3)
    plt.plot(time, data["yaw_mag"], label="yaw magnetic angle",  linewidth=3)
    plt.xlabel("time [sec]")
    plt.ylabel("rad []")
    plt.grid(True)
    #plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
    plt.legend()


    fig = plt.figure(8)
    #ax32 = fig.add_subplot(312, frameon=True)
    plt.title("NavSys - Slope")
    plt.plot(time, data["slope_height"], label="Slope",  linewidth=3)
    plt.xlabel("Time [sec]")
    plt.ylabel("Slope []")
    plt.grid(True)
    #plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
    plt.legend()

    fig = plt.figure(9)
    #ax33 = fig.add_subplot(313, frameon=True)
    plt.title("NavSys - Height")
    plt.plot(time, data["height"], label="Height out of Barometer median fit",  linewidth=3)
    plt.plot(time, data["height_savgol"], label="Height out of Barometer SG fit",  linewidth=3)
    plt.grid(True)
    plt.xlabel("Time [sec]")
    plt.ylabel("Elevation [m]")
    #plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
    plt.legend()
    plt.subplots_adjust(bottom=0.2, wspace=0.2)

    # fig 4
    # ==============================================

    fig = plt.figure(10)
    #ax41 = fig.add_subplot(111, frameon=True)
    plt.title("NavSys - Trajektory")
    plt.plot(lam_traj, phi_traj, label="Trajektory",  linewidth=3)
    plt.plot(lam_deg, phi_deg, label="Start", marker='^', markerfacecolor='red', markersize=6,  linewidth=3)
    plt.xlabel("λ [°]")
    plt.ylabel("φ [°]")
    #plt.plot(start_lam.tail(1), start_phi.tail(1), label="Start", marker='^', markerfacecolor='green', markersize=6)
    plt.grid(True)
    #plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
    plt.legend()

    # fig 5 Google API for Python
    # does not work right
    #from mapsplotlib import mapsplot as mplt
    #plot_df = pd.DataFrame()
    #plot_df["latitude"] = lam_traj
    #plot_df["longitude"] = phi_traj

    #mplt.register_api_key('AIzaSyCyJuOW-15fzA0HWpu4lceIihrfJsVgZvY')
    #mplt.plot_markers(plot_df)


    plt.show()
    print("\n======================================\nProgramm ENDE")
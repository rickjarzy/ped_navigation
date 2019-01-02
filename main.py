import pandas as pd
import numpy
import sys
import pdr_functions
# Paul Arzberger
# 00311430
# 2nd Lab - Navigation Systems - WS18/19
# main file



if __name__ == "__main__":

    # startpoint
    phi = 47.06427                  # [°]
    lam = 15.45313                  # [°]

    print(sys.argv)     # checking if some extra input from the cmd comes in

    print("======================================\n Pedestrian Navigation - Lab 2 \n======================================\n")
    # store the txt data onto a pandas dataframe
    data = pdr_functions.create_data_matrix(r"data.txt")

    print("\n======================================\nProgramm ENDE")
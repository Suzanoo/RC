import pandas as pd
import numpy as np
from tabulate import tabulate

def calculate_balance_moment(DF_row, FEM_row):
    # Sum moment at joint before calculate Bal.M
    def calculate_FEM_X(FEM):
        FEM_X = [FEM[0]]
        for i in range(1, len(FEM)):
            if i == len(FEM) - 1:
                FEM_X.append(FEM[i])
            elif i % 2 != 0:
                FEM_X.append(FEM[i] + FEM[i + 1])
            else:
                FEM_X.append(FEM[i] + FEM[i - 1])
        return FEM_X

    # Calculate DF * FEM_X
    DF = np.array([DF_row])
    FEM_X = np.array([calculate_FEM_X(FEM_row)])
    Bal_M = -DF * FEM_X

    return Bal_M.flatten()

def calculate_carry_over_moment(COF_row, Bal_M_row):
    # Cross over balance moment before multiply by COF
    def calculate_COM_X(Bal_M_row):
        COF_X = []
        for i in range(0, len(Bal_M_row)):
            if i % 2 == 0:
                COF_X.append(Bal_M_row[i + 1])
            else:
                COF_X.append(Bal_M_row[i - 1])
        return COF_X

    # Calculate COF * COF_X
    COF= np.array([COF_row])
    COF_X = np.array([calculate_COM_X(Bal_M_row)])
    COM = COF * COF_X

    return COM.flatten()


def generate_distribution_moment(num_spans, DF, COF, FEM, N):
    # Generate joint names (A, B, C, ...)
    joints = [chr(ord('A') + i) for i in range(num_spans + 1)]

    # Generate column names based on joint names
    columns = ['SB']  # Set the first column name to "SB"
    for i in range(len(joints) - 1):
        column_name_forward = f"{joints[i]}{joints[i + 1]}"
        column_name_reverse = f"{joints[i + 1]}{joints[i]}"
        columns.extend([column_name_forward, column_name_reverse])

    # Create an empty DataFrame with the generated columns
    df = pd.DataFrame(columns=columns)

    # Fill the first row with provided DF values
    df.loc[0, 'SB'] = 'DF'
    df.loc[0, df.columns[1:]] = [item for sublist in DF for item in sublist]

    # Fill the second row with COF values
    df.loc[1, 'SB'] = 'COF'
    df.loc[1, df.columns[1:]] = [item for sublist in COF for item in sublist]

    # Fill the third row with Moment coeff. or moment values
    df.loc[2, 'SB'] = 'FEM'
    df.loc[2, df.columns[1:]] = [item for sublist in FEM for item in sublist]

    DF_row = df.iloc[0].values[1:]
    COF_row = df.iloc[1].values[1:]
    
    # Iteration 
    for i in range(1, N):
        # Calculate Balance Moment using the provided function
        Bal_M = calculate_balance_moment(DF_row, df.iloc[-1].values[1:])
        
        # Fill the fourth row with calculated Bal.M values
        df.loc[(2 * i + 1), 'SB'] = 'Bal.M'
        df.loc[(2 * i + 1), df.columns[1:]] = Bal_M

        # Calculate Carry Over Moment 
        COM = calculate_carry_over_moment(COF_row, df.iloc[-1].values[1:])

        # Fill row with calculated COM values
        df.loc[(2 * i + 2), 'SB'] = 'C.O.M'
        df.loc[(2 * i + 2), df.columns[1:]] = COM

    # Sum each column starting from FEM row
    moment = df.iloc[2:, 1:].sum()

    # Convert the sum to a DataFrame and transpose it
    sum_row = pd.DataFrame([['veM@support'] + moment.tolist()], columns=df.columns)
    df = pd.concat([df, sum_row])

    # Display the generated DataFrame
    print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="psql",
            )
        )

    return moment.tolist()
'''
Example: Generate a DataFrame for 3 spans with provided DF, COF, and FEM values
num_spans = 3
DF_values = [[0.41, 0.252], [0.386, 0.386], [0.252, 0.41]]
COF_values = [[0.506, 0.506], [0.513, 0.513], [0.506, 0.506]]
FEM_values = [[0.833, 0.833], [0.833, 0.833]. [0.833, 0.833]]
N = 5
moment = generate_distribution_moment(num_spans, DF_values, COF_values, FEM_values, N)
'''




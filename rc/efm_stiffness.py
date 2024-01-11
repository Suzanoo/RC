import numpy as np
import pandas as pd

from tools.section import Rectangle
from tools.utils import Utils

# Inertia for L-Shape and Tee
def isb(bw, bf, hw, hf):  
        A1 = bw * hw
        A2 = bf * hf
        d1 = hw /2
        d2 = hw + hf /2

        A = A1 + A2

        yd = (A1 * d1 + A2 * d2) / A
        print(f"\nN.A. = {yd:.0f} mm from bottom")

        I1 = (1/12) * bw * pow(hw, 3) + A1 * (yd - d1)**2
        I2 = (1/12) * bf * pow(hf, 3) + A2 * (yd - d2)**2
        I = I1 + I2
        # print(f"I = {I:.2e} mm4")
        return I

def get_range(df, A_value):
    # Find the closest values in the  column
    closest_values_A = df['A'].unique()
    closest_values_A.sort()

     # Use min and max values if A_value is outside the range
    closest_lower_A = min(closest_values_A) if A_value < min(closest_values_A) else max([value for value in closest_values_A if value <= A_value]) 
    closest_upper_A = max(closest_values_A) if A_value > max(closest_values_A) else min([value for value in closest_values_A if value >= A_value])

    return closest_lower_A, closest_upper_A

# Ksb
class Slab_Beam_Stiffness:
    def __init__(self):
        self.rect = Rectangle()
        self.utils = Utils()
        pass

    # Calculated slab-beam stifness factors 
    def get_slab_beam_stiffness(self, A_value, B_value, path):
        '''
        ACI 13.7.3 
        -Find the closest values in the "A" column
        eg.A_value = 0.56 --> closest value = (0, 1)
        -Use linear interpolatfion to find the stiffness factor values
        -Display the lower bound, the calculated values, and the upper bound as dataframe
        '''
        # Read data from the CSV file
        df = pd.read_csv(path)

        # Calculate the closest values in the table
        closest_lower_A, closest_upper_A = get_range(df, A_value)
        closest_lower_B, closest_upper_B = get_range(df, B_value)

        # Find rows that match the nearest values for A and B
        lower_row = df[(df['A'] == closest_lower_A) & (df['B'] == closest_lower_B)].copy().reset_index(drop=True)
        upper_row = df[(df['A'] == closest_upper_A) & (df['B'] == closest_upper_B)].copy().reset_index(drop=True)

        # Check if ['B'] is None use first ['A']
        '''
        A   B
        0.2 0.15
        0.2 0.25

        Find A = 0.2, B = 0.
        '''
        if lower_row.empty:
            lower_row = df[(df['A'] == closest_lower_A)].copy().reset_index(drop=True)[0:1]
        if upper_row.empty:
            upper_row = df[(df['A'] == closest_upper_A)].copy().reset_index(drop=True)[0:1]

        # Concatenate the rows to form a new DataFrame
        new_df = pd.concat([lower_row, upper_row])

        # Use "B" values in new_df as x1 and x2 in the interpolate function
        m1 = new_df['B'].values[0]
        m2 = new_df['B'].values[1]

        '''
        To avoid devide by 0
        -if B lower and upper is the same , use column A instead 
        -if A, B lower and upper is the same, use lower_row or upper_row
        '''
        if m1 != m2:
             # Create a new row to be added
            new_row = {'A': A_value,
                    'B': B_value,
                    'M.AB': self.utils.linear_interpolate(B_value, m1, m2, new_df['M.AB'].values[0], new_df['M.AB'].values[1]),
                    'M.BA': self.utils.linear_interpolate(B_value, m1, m2, new_df['M.BA'].values[0], new_df['M.BA'].values[1]),
                    'K.AB': self.utils.linear_interpolate(B_value, m1, m2, new_df['K.AB'].values[0], new_df['K.AB'].values[1]),
                    'K.BA': self.utils.linear_interpolate(B_value, m1, m2, new_df['K.BA'].values[0], new_df['K.BA'].values[1]),
                    'COF.AB': self.utils.linear_interpolate(B_value, m1, m2, new_df['COF.AB'].values[0], new_df['COF.AB'].values[1]),
                    'COF.BA': self.utils.linear_interpolate(B_value, m1, m2, new_df['COF.BA'].values[0], new_df['COF.BA'].values[1])}

            # Add the new row to the DataFrame as the second row
            # df = pd.concat([new_df.iloc[:1], pd.DataFrame([new_row]), new_df.iloc[1:]]).reset_index(drop=True)
            df = pd.DataFrame([new_row])

            # Print the updated new_df
            print(df)
            return df

        # if B lower and upper is the same, to avoid 0 divide then use A instead
        else:
            m1 = new_df['A'].values[0]
            m2 = new_df['A'].values[1]

            # if A lower and upper is the same too
            if m1 == m2:
                df = lower_row
                print(df)
                return df
            
            else:
                # Create a new row to be added
                new_row = {'A': A_value,
                        'B': B_value,
                        'M.AB': self.utils.linear_interpolate(A_value, m1, m2, new_df['M.AB'].values[0], new_df['M.AB'].values[1]),
                        'M.BA': self.utils.linear_interpolate(A_value, m1, m2, new_df['M.BA'].values[0], new_df['M.BA'].values[1]),
                        'K.AB': self.utils.linear_interpolate(A_value, m1, m2, new_df['K.AB'].values[0], new_df['K.AB'].values[1]),
                        'K.BA': self.utils.linear_interpolate(A_value, m1, m2, new_df['K.BA'].values[0], new_df['K.BA'].values[1]),
                        'COF.AB': self.utils.linear_interpolate(A_value, m1, m2, new_df['COF.AB'].values[0], new_df['COF.AB'].values[1]),
                        'COF.BA': self.utils.linear_interpolate(A_value, m1, m2, new_df['COF.BA'].values[0], new_df['COF.BA'].values[1])}

                # Add the new row to the DataFrame as the second row
                # df = pd.concat([new_df.iloc[:1], pd.DataFrame([new_row]), new_df.iloc[1:]]).reset_index(drop=True)
                df = pd.DataFrame([new_row])

                # Print the updated new_df
                print(df)
                return df


    def flat(self, c1A, c1B, b, t, l1, fc):
        '''
        c1A: width of column A, mm
        c1B: width of column B , mm
        l1: span along C1A-C1B, mm
        b: slab-beam strip width, mm
        t: slab thickness, mm
        '''
        Ec = 4700 * np.sqrt(fc)
        Is = (1/12) * b * pow(t, 3)
        Ib = 0
  
        print(f"Slab-Beam Stiffness Coefficien: Flat Slab")
        print(f"c1A/l1 = {c1A/l1:.4f}")
        print(f"c1B/l1 = {c1B/l1:.4f}")

        # Calculate factor values 
        df = self.get_slab_beam_stiffness(c1A/l1, c1B/l1, "data/slab-beam-coeff.csv")

        a = ['K.AB', 'K.BA']
        m = ['M.AB', 'M.BA']
        c = ['COF.AB', 'COF.BA']
        b = ['AB', 'BA']
        Ksb = []
        COF = []
        FEM = []

        for i in range(0, len(a)):            
            k = df.at[0, a[i]]
            ksb = k * Ec * (Is + Ib) / l1

            Ksb.append(ksb)
            COF.append(df.at[0, c[i]])
            FEM.append(df.at[0, m[i]])

            print(f"Ksb.{b[i]} = {ksb:.2e} N/mm2")
  
        return Ksb, COF, FEM

    

    def drop_panel(self, dp1A, dp1B, bs, t, l1, fc):
        '''
        dp1A: width of drop-panel A, mm
        dp1B: width of drop-panel B , mm
        l1: span along C1A-C1B, mm
        b: slab-beam strip width, mm
        t: slab thickness, mm
        '''
        Ec = 4700 * np.sqrt(fc)
        Is = (1/12) * bs * pow(t, 3)
        Ib = 0
  
        print(f"Slab-Beam Stiffness Factors: Flat with Drop-Panel")
        print(f"c1A/l1 = {dp1A/l1:.4f}")
        print(f"c1B/l1 = {dp1B/l1:.4f}")

        # Calculate factor values by interpolating
        df = self.get_slab_beam_stiffness(dp1A/l1, dp1B/l1, "data/slab-beam-coeff-with-drop.csv")

        a = ['K.AB', 'K.BA']
        m = ['M.AB', 'M.BA']
        c = ['COF.AB', 'COF.BA']
        b = ['AB', 'BA']
        Ksb = []
        COF = []
        FEM = []

        for i in range(0, len(a)):            
            k = df.at[0, a[i]]
            ksb = k * Ec * (Is + Ib) / l1

            Ksb.append(ksb)
            COF.append(df.at[0, c[i]])
            FEM.append(df.at[0, m[i]])

            print(f"Ksb.{b[i]} = {ksb:.2e} N/mm2")

        return Ksb, COF, FEM
    


    def traverse_beam_exteria(self, c1A, c1B, bw, h, t, l1, l2, fc):
        '''
        c1A: width of column A, mm
        c1B: width of column B , mm
        l1: span along C1A-C1B, mm
        w: beam width, mm   
        h: beam depth, mm
        bw: beam width, mm
        t: slab thickness, mm
        '''
        bs = l2 /2
        b = bs + bw / 2

        hf = t
        hw = h - hf
        bf = bw + min(hw, 4 * t)
        
        Ec = 4700 * np.sqrt(fc)
        Is = (1/12) * bs * pow(t, 3)
        # Ib = 1.5 * self.rect.moment_of_inertia(bw, h) # TODO why 1.5 
        Ib = isb(bw, bf, hw, hf)


        print(f"Slab-Beam Stiffness Factors: Slab with Beam Traverse")
        print(f"c1A/l1 = {c1A/l1:.4f}")
        print(f"c1B/l1 = {c1B/l1:.4f}")

        # Calculate factor values by interpolating
        df = self.get_slab_beam_stiffness(c1A/l1, c1B/l1, "data/slab-beam-coeff.csv")

        a = ['K.AB', 'K.BA']
        m = ['M.AB', 'M.BA']
        c = ['COF.AB', 'COF.BA']
        b = ['AB', 'BA']
        Ksb = []
        COF = []
        FEM = []

        for i in range(0, len(a)):            
            k = df.at[0, a[i]]
            ksb = k * Ec * (Is + Ib) / l1

            Ksb.append(ksb)
            COF.append(df.at[0, c[i]])
            FEM.append(df.at[0, m[i]])

            print(f"Ksb.{b[i]} = {ksb:.2e} N/mm2")

        return Ksb, COF, FEM


    
    def traverse_beam_interia(self, c1A, c1B, bw, h, t, l1, l2, fc):
        '''
        c1A: width of column A, mm
        c1B: width of column B , mm
        l1: span along C1A-C1B, mm
        w: beam width, mm
        h: beam depth, mm
        b: slab-beam strip width, mm
        t: slab thickness, mm
        '''
        hf = t
        hw = h - hf
        bf = bw + 2 * min(hw, 4 * t)
        bs = l2
        

        Ec = 4700 * np.sqrt(fc)
        Is = (1/12) * bs * pow(hf, 3)
        # Ib = self.rect.moment_of_inertia(bw, hw) # TODO why 1.5 
        Ib = isb(bw, bf, hw, hf)

  
        print(f"Slab-Beam Stiffness Factors: Slab with Beam Traverse")
        print(f"c1A/l1 = {c1A/l1:.4f}")
        print(f"c1B/l1 = {c1B/l1:.4f}")

        # Calculate factor values by interpolating
        df = self.get_slab_beam_stiffness(c1A/l1, c1B/l1, "data/slab-beam-coeff.csv")

        a = ['K.AB', 'K.BA']
        m = ['M.AB', 'M.BA']
        c = ['COF.AB', 'COF.BA']
        b = ['AB', 'BA']
        Ksb = []
        COF = []
        FEM = []

        for i in range(0, len(a)):            
            k = df.at[0, a[i]]
            ksb = k * Ec * (Is + Ib) / l1

            Ksb.append(ksb)
            COF.append(df.at[0, c[i]])
            FEM.append(df.at[0, m[i]])

            print(f"Ksb.{b[i]} = {ksb:.2e} N/mm2")

        return Ksb, COF, FEM


# Kc
class Column_Stiffness:
    '''
    Kc: Column stiffness
    K: Stiffness factors
    COF: Carry over factors
    FEM: Fixed end moment factors
    '''
    def __init__(self) -> None:
        self.utils = Utils()


    # Calculated column stifness factors
    def get_columns_stiffness(self, A_value):
        df = pd.read_csv("data/column-coeff.csv")

        # Find the closest values in the "A" column
        closest_values_A = df['A'].unique()
        closest_values_A.sort()

         # Use min and max values if A_value is outside the table
        closest_lower_A = min(closest_values_A) if A_value < min(closest_values_A) else max([value for value in closest_values_A if value <= A_value]) 
        closest_upper_A = max(closest_values_A) if A_value > max(closest_values_A) else min([value for value in closest_values_A if value >= A_value])

        # Find rows that match the nearest values for A and B
        lower_row = df[(df['A'] == closest_lower_A)].copy().reset_index(drop=True)
        upper_row = df[(df['A'] == closest_upper_A)].copy().reset_index(drop=True)


        # If sames row use only one
        if closest_lower_A == closest_upper_A:
            df = lower_row
        # Else use interpolation
        else:
            # Concatenate the rows to form a new DataFrame
            new_df = pd.concat([lower_row, upper_row])

            # Create a new row to be added
            new_row = {'A': A_value,
                    'M.AB': self.utils.linear_interpolate(A_value, closest_lower_A, closest_upper_A, new_df['M.AB'].values[0], new_df['M.AB'].values[1]),
                    'M.BA': self.utils.linear_interpolate(A_value, closest_lower_A, closest_upper_A, new_df['M.BA'].values[0], new_df['M.BA'].values[1]),
                    'K.AB': self.utils.linear_interpolate(A_value, closest_lower_A, closest_upper_A, new_df['K.AB'].values[0], new_df['K.AB'].values[1]),
                    'K.BA': self.utils.linear_interpolate(A_value, closest_lower_A, closest_upper_A, new_df['K.BA'].values[0], new_df['K.BA'].values[1]),
                    'COF.AB': self.utils.linear_interpolate(A_value, closest_lower_A, closest_upper_A, new_df['COF.AB'].values[0], new_df['COF.AB'].values[1]),
                    'COF.BA': self.utils.linear_interpolate(A_value, closest_lower_A, closest_upper_A, new_df['COF.BA'].values[0], new_df['COF.BA'].values[1])}

            # Add the new row to the DataFrame as the second row
            # df = pd.concat([new_df.iloc[:1], pd.DataFrame([new_row]), new_df.iloc[1:]]).reset_index(drop=True)
            df = pd.DataFrame([new_row])

        # Print the updated new_df
        print(df)

        return df

    
    # Column stiffness(Kc)
    def kc(self, c1A, lc, Ic, fc):
        '''
        Warning !!!
            c1A : Thickness of slab with drop panel or
            column capital or
            beam above the column in direction of l1, mm
        '''
        Ec =4700 * np.sqrt(fc)

        print(f"c1A/lc = {c1A/lc:.4f}")
        df = self.get_columns_stiffness(c1A/lc)

        a = ['K.AB', 'K.BA']
        b = ['bot', 'top']
        Kc = []
        for i in range(0, len(a)):            
            k = df.at[0, a[i]]
            kc = k * Ec * Ic / lc
            Kc.append(kc)
            print(f"Kc.{b[i]} = {kc:.2e} N/mm2")
        return Kc


# Kt
class Torsion_Stiffness:
    '''
    flat slab: c1 x hf
    flat slab with capital: c1 x hc
    with traverse beam(exterior): L-beam,  h x (w + min(hw, 4 * t))
    with traverse beam(interior): T- beam,  h x (w + 2 * min(hw, 4 * t))
    '''
    def __init__(self, fc) :
        self.Ec =4700 * np.sqrt(fc)


    def flat(self, c1, c2, t, l2):
        '''
        c1: column width
        t: slab thickness
        '''
        x1 = t
        y1 = c1
        C =  (1 - 0.63 * (x1 / y1)) * (pow(x1, 3) * y1) / 3
        Kt =  9 * self.Ec * C / (l2 * pow((1 - c2 / l2), 3))
        print(f"Kt = {Kt:.2e} N.mm")
        return Kt
    

    def drop_panel(self, c1, c2, td, l2):
        '''
        c1 x c2: drop dimension
        td: drop thickness
        l2: strip width
        '''
        x1 = c1
        y1 = td
        C =  (1 - 0.63 * (x1 / y1)) * (pow(x1, 3) * y1) / 3
        Kt =  9 * self.Ec * C / (l2 * pow((1 - c2 / l2), 3))
        print(f"Kt = {Kt:.2e} N.mm")
        return Kt


    def ext_beam(self, bw, h, t, c2, l1, l2):
        '''
        h: beam depth
        hf: flange thickness
        hw: h - hf
        bw: beam(web) width
        bf: flange width
        '''
        hw = h - t
        hf = t
        bf = bw +  min(hw, 4 * hf)
        bs = l1 + bw

        x1 = bw
        x2 = hf
        y1 = h
        y2 = bf - bw 
        C1 = (1 - 0.63 * (x1 / y1)) * (pow(x1, 3) * y1) / 3
        C2 = (1 - 0.63 * (x2 / y2)) * (pow(x2, 3) * y2) / 3
        CA = C1 + C2

        y1 = hw
        y2 = bf
        C1 = (1 - 0.63 * (x1 / y1)) * (pow(x1, 3) * y1) / 3
        C2 = (1 - 0.63 * (x2 / y2)) * (pow(x2, 3) * y2) / 3
        CB = C1 + C2

        C =  max(CA, CB)
        Is = (1/12) * bs * pow(hf, 3)
        Isb = isb(bw, bs, hw, hf)
        Kt =  9 * self.Ec * C / (l2 * pow((1 - c2 / l2), 3))
        Kt =  Kt * Isb / Is
        print(f"Kt = {Kt:.2e} N.mm")
        return Kt


    def tee(self, bw, h, t, c2, l1, l2):
        '''
        h: beam depth
        hf: flange thickness
        hw: h - hf
        bw: beam(web) width
        bf: flange width
        '''
        hw = h - t
        hf = t
        bf = bw +  2 * min(hw, 4 * hf)
        bs = l1 

        x1 = hf
        x2 = hw
        y1 = bf
        y2 = bw
        C1 = (1 - 0.63 * (x1 / y1)) * (pow(x1, 3) * y1) / 3
        C2 = (1 - 0.63 * (x2 / y2)) * (pow(x2, 3) * y2) / 3
        C =  C1 + C2
    
        Is = (1/12) * bs * pow(hf, 3)
        Isb = isb(bw, bs, hw, hf)

        Kt =  9 * self.Ec * C / (l2 * pow((1 - c2 / l2), 3))
        Kt =  Kt * Isb / Is
        print(f"Kt = {Kt:.2e} N.mm")
        return Kt
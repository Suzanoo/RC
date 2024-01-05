#!/usr/bin/env python3
import os
import pandas as pd
from tabulate import tabulate

class Rebar:
    def __init__(self) -> None:
        self.𝜙 = {
            "6": 6,
            "9": 9,
            "12": 12,
            "16": 16,
            "20": 20,
            "25": 25,
            "28": 28,
            "32": 32,
        }  # mm

        self.A = {
            "6": 0.2827,
            "9": 0.636,
            "12": 1.131,
            "16": 2.01,
            "20": 3.146,
            "25": 4.908,
            "28": 6.157,
            "32": 6.313,
        }  # cm2
    
    def rebar_selected(self):
        while True:
            dia = input(f"Select Diameter  = ? : ")
            if self.𝜙.get(dia) == None:
                print("Wrong diameter! select again")
            else:
                return int(dia), self.A[str(dia)]
    
    def rebar_design(self, As):
        while True:
            print(f"\nAs required = {As:.2f} cm2, please select")
            dia, A = self.rebar_selected()
            N = int(input("Quantities N = ? : "))
            
            if (N * A > As):
                print(f"[INFO] Reinforcment : {N} - ø{dia} mm = {N * A:.2f} cm2")
                return dia, N * A    
            else: 
                print(f"As provide : {N} - ø{dia} mm = {N * A:.2f} cm2 < {As:.2f} cm2, Try again!")


class Utils:
    def __init__(self) -> None:
        pass

    # Calculate spacing, and clear space of rebar in beam section
    def spacing(self, bw, c, db, N):
        db = db / 10 # cm
        s1 = (bw - 2 * c - 2 * db) / (N - 1)

        s2 = s1 - 2 * db # clear space

        return s1, s2
    
    
    # Display  table
    def display_table(self, text, path):
        print(text)
        CURRENT = os.getcwd()
        table = os.path.join(CURRENT, path)
        df = pd.read_csv(table)
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="psql",
            )
        )


    def linear_interpolate(self, x, x1, x2, y1, y2):
            """
            Perform linear interpolation to estimate the y-value at a given x-value
            between two known data points (x1, y1) and (x2, y2).
            
            Parameters:
            - x: The x-value at which to perform interpolation.
            - x1, y1: Coordinates of the first data point.
            - x2, y2: Coordinates of the second data point.
            
            Returns:
            - The estimated y-value at the given x-value.
            """
            # Ensure x1 is less than x2
            if x1 > x2:
                x1, y1, x2, y2 = x2, y2, x1, y1
            
            # Check if x is outside the range [x1, x2]
            if x < x1 or x > x2:
                raise ValueError("x is outside the range [x1, x2]")

            # Perform linear interpolation
            y = y1 + (y2 - y1) * (x - x1) / (x2 - x1)
            
            return y
    
    
    def get_fraction_input(self):
        while True:
            try:
                user_input = input("Enter a fraction (e.g., '1/36'): ")
                # Split the input into numerator and denominator
                numerator_str, denominator_str = user_input.split('/')
                
                # Convert numerator and denominator to integers
                numerator = int(numerator_str)
                denominator = int(denominator_str)
                
                # Check if denominator is not zero
                if denominator == 0:
                    raise ValueError("Denominator cannot be zero.")
                
                # Convert to float
                value = numerator / denominator
                
                return value
            except (ValueError, ZeroDivisionError, IndexError):
                print("Invalid input. Please enter a valid fraction (e.g., '1/36').")


    def calculate_center_of_gravity(self, coordinates, weights):
        total_weight = sum(weights)

        x = (
            sum(coord["x"] * weight for coord, weight in zip(coordinates, weights))
            / total_weight
        )
        y = (
            sum(coord["y"] * weight for coord, weight in zip(coordinates, weights))
            / total_weight
        )

        CoG = {
            "x": x,
            "y": y,
        }

        return CoG



    


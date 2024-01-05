import numpy as np
from absl import app, flags
from absl.flags import FLAGS

from beam import Beam
from shear import ShearCapacity, ShearReinforcement

'''
Deep Beam:
    -simple beam: h/ln > 4/5 
    -contineous: h/ln > 2/5

Critical section:
    -Distribution load: 0.15ln <= d
    -Point load: 0.50a <= d
'''


## FLAGS definition
# https://stackoverflow.com/questions/69471891/clarification-regarding-abseil-library-flags

flags.DEFINE_float("fc", 18, "240ksc, MPa")
flags.DEFINE_integer("fy", 295, "SD40 main bar, MPa")
flags.DEFINE_integer("fv", 235, "SR24 traverse, MPa")
flags.DEFINE_integer("c", 3, "concrete covering, cm")

flags.DEFINE_integer("main", 12, "initial main bar definition, mm")
flags.DEFINE_integer("trav", 6, "initial traverse bar definition, mm")
flags.DEFINE_integer("b", 0, "beam width, cm")
flags.DEFINE_integer("h", 0, "beam heigth, cm")
flags.DEFINE_integer("l", 0, "beam length, m")
flags.DEFINE_float("Mu", 0, "Moment, kN-m")
flags.DEFINE_float("Vu", 0, "Shear, kN")

## Constance
Es = 2e5  # MPa
𝜙b = 0.9
𝜙v = 0.85

def max_shear_capacity(ln, d):

    if (ln/d) <  2:
        return 𝜙v * (2/3) * np.sqrt(FLAGS.fc) * FLAGS.b * d *1e-1 # kN
    elif 2 <= (ln/d) <= 5:
        return 𝜙v * (1/18) * (10 + ln/d) * np.sqrt(FLAGS.fc) * FLAGS.b * d *1e-1 # kN
    else:
        return None

  
def main(_argv):
    # Display properties
    print("DEEPL BEAM DESIGN : USD METHOD")
    print(
        "========================================================================================================"
    )

    print("PROPERTIES")
    print(
        f"f'c = {FLAGS.fc} Mpa, fy = {FLAGS.fy} Mpa, fv = {FLAGS.fv} MPa, Es = {Es:.0f} MPa"
    )
    print(f"𝜙b = {𝜙b}, 𝜙v = {𝜙v}")

    print(f"\nGEOMETRY")
    print(
        f"b = {FLAGS.b} cm, h = {FLAGS.h} cm,l = {FLAGS.l} m"
    )

    # Instanciate simple beam class 
    beam = Beam(fc=FLAGS.fc, fy=FLAGS.fy, fv=FLAGS.fv, c=FLAGS.c)
    beam.initial(FLAGS.main, FLAGS.trav, FLAGS.b, FLAGS.h, FLAGS.l, FLAGS.Mu, FLAGS.Vu)

    # Implement some properties
    β1 = beam.beta()
    d, d1 = beam.eff_depth()
    pmin, pmax1, p = beam.percent_reinf()

    ln = FLAGS.l * 100 - (2 * d) # cm

    while True:

        if (ln / d > 5):
            print(f"\n[WARNING!] ln / d > 5, please revise your section before!!!")
            break
        else:
            # --------------------------------
            ## Main reinforcement 
            # --------------------------------
            # Calculate 𝜙Mn
            𝜙Mn1 = beam.capacity(d)

            # Check classification
            classify = beam.classification(FLAGS.Mu, 𝜙Mn1)

            # Main bar required
            data = beam.mainbar_req(d, d1, 𝜙Mn1, FLAGS.Mu, classify)

            # Design main reinf
            beam.db()
            dia_main, As_main = beam.main_call(data)

            # --------------------------------
            ## Traverse and Horizontal reinforcement 
            # --------------------------------
            # Traverse
            shearCapacity = ShearCapacity(FLAGS.fc, FLAGS.fv)
            𝜙Vc = shearCapacity.flexural_shear(FLAGS.b, d)

            # Horizontal
            shearReinf = ShearReinforcement(FLAGS.fc, FLAGS.fv, FLAGS.fy)
            𝜙Vs = shearReinf.deepBeam(FLAGS.b, d, ln)

            # Check condition of 𝜙Vn 
            𝜙Vn = 𝜙Vc + 𝜙Vs
            𝜙Vnmax = max_shear_capacity(ln, d)

            if (𝜙Vn <= 𝜙Vnmax):
                print(f"\n𝜙Vc = {𝜙Vc:.2f} kN, 𝜙Vs = {𝜙Vs:.2f} kN, 𝜙Vn = {𝜙Vn:.2f} kN, 𝜙Vnmax = {𝜙Vnmax:.2f} kN,")
                print(f'SECTION OK')
            else:
                print(f"𝜙Vn > 𝜙Vnmax, SECTION IS NOT OK, Try again!!")

           
            break
    

if __name__ == "__main__":
    app.run(main)

"""
How to used?
-Please see FLAGS definition for unit informations
-Make sure you are in the project directory run python in terminal(Mac) or command line(Windows)
-run script
    % cd <path to project directory>
    % conda activate <your conda env name>
    % python rc/deep_beam.py --b=35 --h=100 --l=4 --Mu=85 --Vu=120
    % python rc/deep_beam.py --fc=24 --fy=395 --b=35 --h=100 --l=4 --Mu=5 --Vu=2.5
    
-you can easy run the code with other FLAGS defined above if you want.
"""

        
    


       

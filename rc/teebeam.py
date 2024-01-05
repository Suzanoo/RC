from absl import app, flags
from absl.flags import FLAGS
from beam import Beam

# from tools.devLength import DevLength

## FLAGS definition
# https://stackoverflow.com/questions/69471891/clarification-regarding-abseil-library-flags

flags.DEFINE_float("fc", 18, "240ksc, MPa")
flags.DEFINE_integer("fy", 295, "SD40 main bar, MPa")
flags.DEFINE_integer("fv", 235, "SR24 traverse, MPa")
flags.DEFINE_integer("c", 3, "concrete covering, cm")

flags.DEFINE_integer("main", 12, "initial main bar definition, mm")
flags.DEFINE_integer("trav", 6, "initial traverse bar definition, mm")

flags.DEFINE_integer("b", 0, "beam width, cm")
flags.DEFINE_integer("bw", 0, "web width, cm")

flags.DEFINE_integer("h", 0, "beam heigth, cm")
flags.DEFINE_integer("hf", 0, "flange heigth, cm")

flags.DEFINE_integer("l", 0, "beam length, m")

flags.DEFINE_float("Mu", 0, "Moment, kN-m")
flags.DEFINE_float("Vu", 0, "Shear, kN")

Es = 2e5  # MPa
𝜙b = 0.9
𝜙v = 0.85


# ----------------------------------
## Tee beam
# ----------------------------------
def neutal_axis(β1, p, d):
    w = p * FLAGS.fy / FLAGS.fc
    a = w * d / 0.85  # cm
    c = a / β1  # cm
    print(f"\nNuetral axis = {c:.2f} cm")
    return c


def tee_capacity(d, As):
    a = (As * FLAGS.fy - 0.85 * FLAGS.fc * FLAGS.hf * (FLAGS.b - FLAGS.bw)) / (
        0.85 * FLAGS.fc * FLAGS.bw
    )  # cm

    𝜙Mw = 0.85 * FLAGS.fc * a * FLAGS.bw * (d - a / 2) * 1e-3  # kN-m
    𝜙Mf = (
        0.85 * FLAGS.fc * (FLAGS.b - FLAGS.bw) * FLAGS.hf * (d - FLAGS.h / 2) * 1e-3
    )  # kN-m

    𝜙Mn1 = 𝜙Mw + 𝜙Mf

    return 𝜙Mn1


def main(_argv):
    print("TEE BEAM DESIGN : USD METHOD")
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
        f"bw = {FLAGS.bw} cm, b = {FLAGS.b} cm, hf = {FLAGS.hf} cm, h = {FLAGS.h} cm,l = {FLAGS.l} m"
    )

    # instanciate
    beam = Beam(fc=FLAGS.fc, fy=FLAGS.fy, fv=FLAGS.fv, c=FLAGS.c)

    beam.initial(FLAGS.main, FLAGS.trav, FLAGS.b, FLAGS.h, FLAGS.l, FLAGS.Mu, FLAGS.Vu)

    β1 = beam.beta()
    d, d1 = beam.eff_depth()
    pmin, pmax1, p = beam.percent_reinf()

    # Check nuetral axis
    c = neutal_axis(β1, p, d)

    # Calculate 𝜙Mn
    if c < FLAGS.hf:
        print("Rectangular Beam")
        𝜙Mn1 = beam.capacity(d)

    else:
        As = p * FLAGS.b * d
        𝜙Mn1 = tee_capacity(d, As)
        print("Tee Beam")
        print(f"\nSection capacity : \n𝜙Mn = {𝜙Mn1:.2f} kN-m")

    # Check classification
    classify = beam.classification(FLAGS.Mu, 𝜙Mn1)

    # Main bar required
    data = beam.mainbar_req(d, d1, 𝜙Mn1, FLAGS.Mu, classify)

    # Design main reinf
    beam.db()
    dia_main, As_main = beam.main_call(data)

    # Design traverse
    if FLAGS.Vu != 0:
        dia_trav, Av, s = beam.traverse_call(d)

if __name__ == "__main__":
    app.run(main)

"""
How to used?

-Please see FLAGS definition for unit informations
-run script
    % cd <path to project directory>
    % conda activate <your conda env name>
    % python rc/teebeam.py --bw=30 --b=100 --hf=10 --h=40 --l=4 --Mu=85 --Vu=120
    % python rc/teebeam.py --fc=24 --fy=395 --bw=30 --b=100 --hf=10 --h=40 --l=5 --Mu=5 --Vu=2.5
    
"""

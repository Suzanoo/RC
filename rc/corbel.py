from absl import app, flags
from absl.flags import FLAGS

from beam import Beam
from tools.utils import Rebar

## FLAGS definition
# https://stackoverflow.com/questions/69471891/clarification-regarding-abseil-library-flags

flags.DEFINE_float("fc", 18, "240ksc, MPa")
flags.DEFINE_integer("fy", 295, "SD40 main bar, MPa")
flags.DEFINE_integer("fv", 235, "SR24 traverse, MPa")
flags.DEFINE_integer("c", 3, "concrete covering, cm")

flags.DEFINE_integer("main", 12, "initial main bar definition, mm")
flags.DEFINE_integer("trav", 9, "initial traverse bar definition, mm")
flags.DEFINE_integer("b", 0, "corbel width, cm")
flags.DEFINE_integer("h", 0, "corbel heigth, cm")
flags.DEFINE_integer("l", 0, "corbel length, m")
flags.DEFINE_float("Mu", 0, "Moment, kN-m")
flags.DEFINE_float("Vu", 0, "Shear, kN")

## Constance
Es = 2e5  # MPa
øb = 0.9
øv = 0.85


def main(_argv):
    # Display properties
    print("CORBEL DESIGN : USD METHOD")
    print(
        "========================================================================================================"
    )

    print("PROPERTIES")
    print(
        f"f'c = {FLAGS.fc} Mpa, fy = {FLAGS.fy} Mpa, fv = {FLAGS.fv} MPa, Es = {Es:.0f} MPa"
    )
    print(f"𝜙b = {øb}, 𝜙v = {øv}")

    print(f"\nGEOMETRY")
    print(
        f"b = {FLAGS.b} cm, h = {FLAGS.h} cm,l = {FLAGS.l} cm"
    )

    # Instanciate 
    rebar = Rebar()

    beam = Beam(fc=FLAGS.fc, fy=FLAGS.fy, fv=FLAGS.fv, c=FLAGS.c)
    beam.initial(FLAGS.main, FLAGS.trav, FLAGS.b, FLAGS.h, FLAGS.l, FLAGS.Mu, FLAGS.Vu)

    # Implement some properties
    β1 = beam.beta()
    d, d1 = beam.eff_depth()
    pmin, pmax1, p = beam.percent_reinf()

    # Definition
    a = FLAGS.b / 2 # Load position from edge, cm
    µ = 1 # friction coefficient for monolithic construction
    j = 0.85 # moment arm of stress block
    Nuc = 0.2 * FLAGS.Vu # Horizontal tension, kN
    Mu = (FLAGS.Vu * a + Nuc * (FLAGS.h - d)) * 1e-2 # kN-m

    while True:
        # First check
        if (a / d >= 1):
            print("Not a corbel, please revise section")
            break
        else:
            # Check section capacity
            øVn = øv * min(0.2 * FLAGS.fc *  FLAGS.b * d *1e-1, 5.5 *  FLAGS.b * d * 1e-1)
            if (øVn < FLAGS.Vu):
                print("Section overload, please revise section")
                break
            else:
                # Friction resistance at shear plane reinf.
                Avf = (FLAGS.Vu / (øv * µ * FLAGS.fy)) * 10 # cm2

                # Flexural resistance reinf
                Af = (Mu / (øb * FLAGS.fy * j * d)) * 1e3 # cm2

                # Tensile reinf
                An = (Nuc / (øv * FLAGS.fy)) * 10 # cm2

                # Main reinf
                print(f"\nMain reinforcements")
                Asmin = max(Af + An, (2/3) * Avf + An)

                beam.db()
                Asmin = max (Asmin, 0.04 *(FLAGS.fc / FLAGS.fy) * FLAGS.b * d)
                dia, As = rebar.rebar_design(Asmin)

                # Traverse
                print(f"\nTraverse")
                Ahmin = 0.5 * (As - An) 
                Ah = rebar.rebar_design(Ahmin)
                break



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
    % python rc/corbel.py --b=25 --h=35 --l=25 --Vu=200

"""
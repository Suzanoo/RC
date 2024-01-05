from absl import app, flags, logging
from absl.flags import FLAGS

from beam import Beam
from torsion import Torsion
from dev_length import DevLength

from tools.utils import Rebar

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
flags.DEFINE_integer("h", 0, "beam heigth, cm")
flags.DEFINE_integer("l", 0, "beam length, m")
flags.DEFINE_float("Mu", 0, "Moment, kN-m")
flags.DEFINE_float("Vu", 0, "Shear, kN")
flags.DEFINE_float("Tu", 0, "Torsion, kN-m")

Es = 2e5  # MPa
𝜙b = 0.9
𝜙v = 0.85

rebar = Rebar()

# ----------------------------------
def main(_argv):
    print("TYPICAL BEAM DESIGN : USD METHOD")
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

    # instanciate
    beam = Beam(fc=FLAGS.fc, fy=FLAGS.fy, fv=FLAGS.fv, c=FLAGS.c)
    beam.initial(FLAGS.main, FLAGS.trav, FLAGS.b, FLAGS.h, FLAGS.l, FLAGS.Mu, FLAGS.Vu)

    β1 = beam.beta()
    d, d1 = beam.eff_depth()
    pmin, pmax1, p = beam.percent_reinf()


    # Calculate 𝜙Mn
    𝜙Mn1 = beam.capacity(d)

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

    # Torsion reinf
    if FLAGS.Tu != 0:
        print("")
        logging.info(f"[INFO] : TORSION")

        Acp = FLAGS.b * FLAGS.h
        Pcp = 2 * (FLAGS.b + FLAGS.h)

        torsion = Torsion(FLAGS.fc, FLAGS.fv, FLAGS.fy, FLAGS.fv, FLAGS.fy, FLAGS.Vu, FLAGS.Tu)

        torsion.section_properties(FLAGS.b, FLAGS.h, FLAGS.c, d, dia_trav)

        torsion.condition(Acp, Pcp)
        torsion.section(FLAGS.b, d)
        
        # New traverse
        torsion.traverse(FLAGS.b)

        # Long-reinforcment
        Al = torsion.longitudinal_reinf(FLAGS.b, Acp)

        print(f"\nFor Each Side : ")
        rebar.rebar_design(Al / 4)

        # Merge flexural and torsion reinf.
        print(f"\nModify Main Reinforcement : ")
        As = As_main + Al / 4
        dia_main, As_main = rebar.rebar_design(As)

    # TODO Development Length
    # print(f"\nDevelopment Length : ")
    # devLength = DevLength(FLAGS.fc, FLAGS.fy)

    # N = int(input(f"Provide number of main reinforce on bottom layer : "))
    # devLength.tensile(FLAGS.b, FLAGS.c, dia_main, N)


if __name__ == "__main__":
    app.run(main)

"""
How to used?
-Please see FLAGS definition for unit informations
-Make sure you are in the project directory run python in terminal(Mac) or command line(Windows)
-run script
    % cd <path to project directory>
    % conda activate <your conda env name>
    % python rc/beam_design.py --fc=24 --fy=390 --b=20 --h=40 --l=4 --Mu=85 --Vu=120
    % python rc/beam_design.py --fc=24 --fy=390 --b=25 --h=40 --l=5 --Mu=5 --Vu=2.5
    % python rc/beam_design.py --fc=30 --fy=390 --fv=390 --b=30 --h=50 --l=6 --c=5 --Mu=183 --Vu=50 --Tu=20
    
-you can easy run the code with other FLAGS defined above if you want.
"""

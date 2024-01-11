from absl import app, flags, logging
from absl.flags import FLAGS

from efm_stiffness import Slab_Beam_Stiffness, Column_Stiffness, Torsion_Stiffness


# from tools.devLength import DevLength

## FLAGS definition
# https://stackoverflow.com/questions/69471891/clarification-regarding-abseil-library-flags

flags.DEFINE_float("fc1", 20, "slab concrete strength, MPa")
flags.DEFINE_float("fc2", 35, "column concrete strength, MPa")

flags.DEFINE_float("c1A", 0, "column A width, mm")
flags.DEFINE_float("c2A", 0, "column A depth, mm")
flags.DEFINE_float("c1B", 0, "column B width, mm")
flags.DEFINE_float("c2B", 0, "column B depth, mm")

flags.DEFINE_float("dp1A", 0, "drop A width, mm")
flags.DEFINE_float("dp2A", 0, "drop A depth, mm")
flags.DEFINE_float("dp1B", 0, "drop B width, mm")
flags.DEFINE_float("dp2B", 0, "drop B depth, mm")

flags.DEFINE_float("bw", 0, "beam width , mm")
flags.DEFINE_float("h", 0, "beam depth , mm")

flags.DEFINE_float("t", 0, "slab thickness , mm")
flags.DEFINE_float("td", 0, "drop thickness , mm")

flags.DEFINE_float("l1", 0, "span along AB, mm")
flags.DEFINE_float("l2", 0, "span , mm")
flags.DEFINE_float("lc", 0, "story heigth, mm")

flags.DEFINE_string('type', 'flat_int', 'flat_ext, flat_int, drop_ext, drop_int, tb_ext, tb_int')


def main(_argv):
    sb = Slab_Beam_Stiffness()
    cs = Column_Stiffness()
    ts = Torsion_Stiffness(FLAGS.fc2)
    '''
    flat --> t = t
    drop --> t - drop thickness
    traverse beam --> t - beam depth
    '''
    Ic = (1 / 12) * FLAGS.c1A * pow(FLAGS.c2A, 3) # mm4
    
    if FLAGS.type == 'flat_ext':
        b = FLAGS.l2 / 2
        sb.flat(FLAGS.c1A, FLAGS.c1B, b, FLAGS.t, FLAGS.l1, FLAGS.fc1)
        cs.kc(FLAGS.t, FLAGS.lc, Ic, FLAGS.fc2)
        ts.flat(FLAGS.c1A, FLAGS.c2A, FLAGS.t, FLAGS.l2)


    elif FLAGS.type == 'drop_ext':
        b = FLAGS.l2 / 2
        sb.drop_panel(FLAGS.dp1A, FLAGS.dp1B, b, FLAGS.td, FLAGS.l1, FLAGS.fc1)
        cs.kc(FLAGS.td, FLAGS.lc, Ic, FLAGS.fc2)
        ts.drop_panel(FLAGS.dp1A, FLAGS.dp2A, FLAGS.td, FLAGS.l2)
        

    elif FLAGS.type == 'drop_int':
        b = FLAGS.l2
        sb.drop_panel(FLAGS.dp1A, FLAGS.dp1B, b, FLAGS.t, FLAGS.l1, FLAGS.fc1)
        cs.kc(FLAGS.td, FLAGS.lc, Ic, FLAGS.fc2)
        ts.drop_panel(FLAGS.dp1A, FLAGS.dp2A, FLAGS.td, FLAGS.l2)


    elif FLAGS.type == 'tb_ext':
        sb.traverse_beam_exteria(FLAGS.c1A, FLAGS.c1B, FLAGS.bw, FLAGS.h, FLAGS.t,  FLAGS.l1,  FLAGS.l2, FLAGS.fc1)
        cs.kc(FLAGS.h, FLAGS.lc, Ic, FLAGS.fc2)
        ts.ext_beam(FLAGS.bw, FLAGS.h, FLAGS.t, FLAGS.c2A, FLAGS.l2)


    elif FLAGS.type == 'tb_int':
        sb.traverse_beam_interia(FLAGS.c1A, FLAGS.c1B, FLAGS.bw, FLAGS.h, FLAGS.t,  FLAGS.l1,  FLAGS.l2, FLAGS.fc1)
        cs.kc(FLAGS.h, FLAGS.lc, Ic, FLAGS.fc2)
        ts.ext_beam(FLAGS.bw, FLAGS.h, FLAGS.t, FLAGS.c2A, FLAGS.l2)

    # Default = Flat at interior
    else: 
        b = FLAGS.l2
        sb.flat(FLAGS.c1A, FLAGS.c1B, b, FLAGS.t, FLAGS.l1, FLAGS.fc1)
        cs.kc(FLAGS.t, FLAGS.lc, Ic, FLAGS.fc2)
        ts.flat(FLAGS.dp1A, FLAGS.dp2A, FLAGS.t, FLAGS.l2)

    

if __name__ == "__main__":
    app.run(main)

# python rc/efm.py --c1A=400 --c2A=400 --c1B=400 --c2B=400 --t=190 --l1=6000 --l2=4500 --lc=2750 --fc1=20 --fc2=35 --type=flat_ext
# python rc/efm.py --c1A=400 --c2A=400 --c1B=400 --c2B=400 --t=190 --l1=6000 --l2=4500 --lc=2750 --fc1=20 --fc2=35 --type=flat_int
# python rc/efm.py --c1A=400 --c2A=400 --c1B=400 --c2B=400 --t=190 --l1=4000 --l2=4500 --lc=2750 --fc1=20 --fc2=35 --type=flat_int
    


# python rc/efm.py --c1A=400 --c2A=400 --c1B=400 --c2B=400 --dp1A=950 --dp2A=1500 --dp1B=1335 --dp2B=1335 --t=180 --td=775 --l1=7500 --l2=6000 --lc=3000 --fc1=25 --fc2=35 --type=drop_int
# python rc/efm.py --c1A=400 --c2A=400 --c1B=400 --c2B=400 --dp1A=1335 --dp2A=1335 --dp1B=1335 --dp2B=1335 --t=180 --td=750 --l1=7500 --l2=6000 --lc=3000 --fc1=25 --fc2=25 --type=drop_int

    
   
# python rc/efm.py --c1A=250 --c2A=250 --c1B=250 --c2B=250 --bw=250 --h=500 --t=150 --l1=5000 --l2=5000 --lc=3000 --fc1=25 --fc2=35 --type=tb_ext
# python rc/efm.py --c1A=250 --c2A=250 --c1B=250 --c2B=250 --bw=250 --h=500 --t=150 --l1=5000 --l2=5000 --lc=3000 --fc1=25 --fc2=35 --type=tb_int
       


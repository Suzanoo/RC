import numpy as np

from tools.utils import Utils

class Factor:
    def __init__(self):
        pass
        
    # Location factor
    def alpha(self, a):
        match a:
            case 1: return 1.3
            case _: return 1

    # Coating factor
    def beta(self, b):
        match b:
            case "Epoxy coating 1": return 1.5
            case "Epoxy coating 2": return 1.2
            case _: return 1

    # Sizing
    def gamma(self, g):
        return 0.8 if g <= 19 else 1
    
    # Concrete
    def lamda(self, lm, fc, fct):
        match lm:
            case "light_wt": return 1.3
            case "splitting tensile strength": return max(1, (np.sqrt(fc) / (1.8 * fct)))
            case _: return 1


class DevLength:
    def __init__(self, fc, fy) -> None:
        self.fc = fc
        self.fy = fy
        self.factor = Factor()

        self.utils = Utils()

    # Dev-length: Deform bar under tensile
    def dbt(self, bw, c, db, N):
        '''
        Calculated ld/db ratio:
        s1 = spacing of rebar , cm
        s2 = clear spcing(surface to surface), cm
        c = concrete covering , cm
        '''
        s1, s2 = self.utils.spacing(bw, c, db, N) 
        a = self.factor.alpha(a=1)
        b = self.factor.beta(b=None)
        lm = self.factor.lamda("Normal", self.fc, 0)

        if db < 19:
            if (s2 > db/10 and c >= db/10) or (s1 > 2*db/10 and c >= db/10):
                ratio =  (12/25) * (self.fy/np.sqrt(self.fc)) * a * b * lm
            else:
                ratio =   (18/25) * (self.fy/np.sqrt(self.fc)) * a * b * lm
        else:
            if (s2 > db/10 and c >= db/10) or (s1 > 2*db/10 and c >= db/10):
                ratio =   (3/5) * (self.fy/np.sqrt(self.fc)) * a * b * lm
            else:
                ratio =   (9/10) * (self.fy/np.sqrt(self.fc)) * a * b * lm

        print(f"ld/db ratio = {ratio:.0f}")           

    # Dev-length: Deform bar under compression
    def dbc(self, db, As_req=1, As_prov=1, spiral=False):
        ldb0 = (db / 4) * (self.fy / self.fc)
        ldb = max(ldb0, 0.04 * db * self.fy)

        # Modify factor
        ldb = ldb * As_req/As_prov
        if spiral:
            ldb = 0.75 * ldb 
        print(f"ldb = {ldb} ") # mm

    # Bundle reinf.
    def bundle(self, N, ldb):
        if N in (3, 4):
            if N == 3:
                ldb = 1.2 * ldb
            if N == 4:
                ldb = 1.33 * ldb
        print(f"ldb = {ldb} ") # mm

    # Hook under tensile
    def hook(self, db, As_req=1, As_prov=1):
        lhb = 188 * db/np.sqrt(self.fc) # for fy = 420 MPa, mm

        # Modify factor
        if self.fy != 420: ldh = lhb * self.fy / 420 # mm
        ldh = ldh * As_req/As_prov
        ldh = max(ldh, 8*db, 150)

        print(f"Hook : ldh = {ldh:.0f} mm")

    # M+ reinf.
    def positive(self, d, db, Mu, Vu):
        '''
        d : effective depth, cm
        db : diameter, mm
        Mu : kN-m
        Vu : kN
        '''
        la = max(d * 10, 12 * db)

        # At end
        ld = (Mu / Vu) * 1e3 + la
        print(f"At support : ldh = {ld:.0f} mm")

        # At Turning point
        ldmax = 1.3 * (Mu / Vu) * 1e3 + la
        print(f"At support : ldh = {ldmax:.0f} mm")

    # M- reinf.
    def negative(self, d, db, ln):
        '''
        d : effective depth, cm
        db : diameter, mm
        ln : clear span, m
        '''
        ldmax = max(d, 12 * db, ln / 16)



class Splice:
    def __init__(self,) :
        pass

    # Lap splice: deform bar under tensile

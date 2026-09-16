from dataclasses import dataclass
from fractions import Fraction
@dataclass(frozen=True)
class FrameRate:
    exact: Fraction | float; drop_frame: bool = False
    def __post_init__(self):
        if self.drop_frame and self.nominal not in (30, 60): raise ValueError("drop-frame разрешён только для 29.97/59.94")
    @property
    def nominal(self): return round(float(self.exact))
@dataclass(frozen=True)
class Timecode:
    frame: int; rate: FrameRate
    @classmethod
    def parse(cls, value, rate):
        p = value.replace(';', ':').split(':')
        if len(p) != 4 or any(not x.isdigit() for x in p): raise ValueError(f"invalid timecode: {value}")
        h,m,s,f = map(int,p)
        if m >= 60 or s >= 60 or f >= rate.nominal: raise ValueError(f"invalid timecode label: {value}")
        mins = 60*h+m; dropped = 2*(mins-mins//10) if rate.drop_frame else 0
        return cls(((h*3600+m*60+s)*rate.nominal+f)-dropped, rate)
    def format(self):
        n=self.rate.nominal; frame=self.frame
        if self.rate.drop_frame:
            d,r=divmod(frame,17982); frame += 18*d + 2*max(0,(r-2)//1798)
        secs,f=divmod(frame,n); h,rem=divmod(secs,3600); m,s=divmod(rem,60)
        return f"{h:02d}:{m:02d}:{s:02d}:{f:02d}"

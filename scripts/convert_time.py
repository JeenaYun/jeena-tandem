# Last update: 2024.02.07.
import argparse

yrs_in_sec = 60*60*24*365

def sec2yrs(sec):
    val = sec/yrs_in_sec
    print('%1.6e s <=> %1.4f yrs'%(sec,val))
    return val

def yrs2sec(yrs):
    val = yrs*yrs_in_sec
    print('%d yrs <=> %d s'%(yrs,val))
    return val

def mps2mmpyr(mps):
    val = mps*1e3*yrs_in_sec
    print('%g m/s <=> %1.2f mm/yr'%(mps,val))
    return val

def mmpyr2mps(mmpyr):
    val = mmpyr*1e-3/yrs_in_sec
    print('%1.2f mm/yr <=> %g m/s'%(mmpyr,val))
    return val

parser = argparse.ArgumentParser()
parser.add_argument("number", type=float, help=": target number to convert")
parser.add_argument("--sec2yrs", action="store_true", help=": convert seconds to years", default=False)
parser.add_argument("--yrs2sec", action="store_true", help=": convert years to seconds", default=False)
parser.add_argument("--mps2mmpyr", action="store_true", help=": convert m/s to mm/yr", default=False)
parser.add_argument("--mmpyr2mps", action="store_true", help=": convert mm/yr to m/s", default=False)
args = parser.parse_args()

if args.sec2yrs + args.yrs2sec + args.mps2mmpyr + args.mmpyr2mps == 0: args.sec2yrs = True
if args.sec2yrs: sec2yrs(args.number)
if args.yrs2sec: yrs2sec(args.number)
if args.mps2mmpyr: mps2mmpyr(args.number)
if args.mmpyr2mps: mmpyr2mps(args.number)

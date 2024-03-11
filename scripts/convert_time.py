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

parser = argparse.ArgumentParser()
parser.add_argument("number", type=float, help=": target number to convert")
parser.add_argument("--sec2yrs", action="store_true", help=": convert seconds to years", default=True)
parser.add_argument("--yrs2sec", action="store_true", help=": convert years to seconds", default=False)
args = parser.parse_args()

if args.sec2yrs:
    sec2yrs(args.number)
if args.yrs2sec:
    yrs2sec(args.number)

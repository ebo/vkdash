from vkdash.tap import *
import os, sys

plan = Plan(atexit=True)

tap_file = os.path.splitext(sys.argv[0])[0]+".tap"
if os.path.exists(tap_file):
    os.remove(tap_file)

# terminate the plan to test exit without saving
plan._atexit_save()

exists = os.path.exists(tap_file)

# regenerate the plan with the answer...
plan = Plan(atexit=True)

plan.ok(exists, "test saving the test plan without explicitly writing it","failed by not creating the tap file with running _atexit_save()")

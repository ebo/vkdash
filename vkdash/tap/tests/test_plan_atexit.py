from vkdash.tap import *
import os, sys

def test_atexit():
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

    results = os.path.splitext(__file__)[0]+".tap"
    fout = open(results,'w')
    fout.write(str(plan))

if __name__ == '__main__':
    test_atexit()

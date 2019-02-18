from vkdash.tap import *
import os

def test_plan():
    plan = None
    try:
        meta = {"test":"of embedding YAML in the plan"}
        plan = Plan(data=meta)
    except:
        print ("ERROR: creating a plan failed...")
        exit(-1)

    plan.ok(0==len(plan.tests), "the Plan tests should be empty.")
    plan.ok(1==len(plan.tests), "and should be 1 after the previous test...")

    plan.diagnostic("a diagnosstic message.")
    plan.diagnostic("  and another...")
    plan.diagnostic("    and another...")

    plan.ok(True, "and another test after the diagnostic...")
    plan.ok(3==plan.tests[-1].number, "make sure that the diagnostic messaging does not advance the test number")

    tmp_plan = Plan()
    tmp_plan.ok(True,"just a test")
    plan.ok(bool(plan) and bool(tmp_plan), "verify that the boolean test for the plan is true when all tests pass")

    tmp_plan.ok(False,"just a failed test")
    plan.ok(bool(plan) and not bool(tmp_plan), "verify that the boolean test for the plan is False after the first failed test")

    # test parsing from a string
    parse_plan = Plan()
    ver_str = "TAP version 12"
    parse_plan.parse(ver_str+"\n1..1\nok")
    plan.ok(ver_str==parse_plan.version, "parsed the plan's version string")
    plan.ok(1==parse_plan.test_count, "and the number of plan items are as expected")

    # test parsing from a list of strings
    parse2_plan = Plan()
    ver_str = "TAP version 12"
    parse2_plan.parse([ver_str,"1..1","ok"])
    plan.ok(1==parse2_plan.test_count, "test if we can parse from lists of strings")

    # add a time stamp to a test
    plan.ok(True, "test setting runtime",message="this is a test",data={'data':{'RUN_TIME': 1234.56}})

    # add a random YAML field to a diagnostic message
    plan.diagnostic("test diagnostic YAML", data={'data':{'Random': "bla..."}})
    ################
    if False:
        newplan = Plan()
        orig_str = "TAP version 13\
1..1\
  ---\
  test: what??? of embedding YAML in the plan\
  ...\
ok 1 - the Plan tests should be empty.\
"
        newplan.parse(orig_str)
        print("****",newplan.data)
        plan.ok(newplan.data['test']=="of embedding YAML in the plan", "Testing embedded YAML in plan headder.")

    if True:
        orig_str = "TAP version 13\nok 1 - retrieving servers from the database\n# need to ping 6 servers\nok 2 - pinged diamond\nok 3 - pinged ruby\nnot ok 4 - pinged saphire\n  ---\n  message: 'hostname \"saphire\" unknown'\n  severity: fail\n  ...\nok 5 - pinged onyx\nnot ok 6 - pinged quartz\n  ---\n  message: 'timeout'\n  severity: fail\n  ...\nok 7 - pinged gold\n1..7\n"

        newplan = Plan()
        newplan.parse(orig_str)
        plan.ok(newplan.test_count==7, "Verifying post plan counted properly.")

    

    results = os.path.splitext(__file__)[0]+".tap"
    fout = open(results,'w')
    fout.write(str(plan))

if __name__ == '__main__':
    test_plan()

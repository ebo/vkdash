from vkdash.tap import *
import os

plan = Plan()

itm = Tap_Item()

orig_str = "ok"
itm.parse(orig_str)
itm_str = str(itm)
plan.ok(orig_str==itm_str, "Test 'ok' only properly parsed and converted back to a string.")

orig_str = "not ok"
itm.parse(orig_str)
itm_str = str(itm)
plan.ok(orig_str==itm_str, "Test 'not ok' only properly parsed and converted back to a string.")

orig_str = "ok - testing"
itm.parse(orig_str)
itm_str = str(itm)
plan.ok(orig_str==itm_str, "Test 'ok' with missing number and converted back to a string.")

orig_str = "not ok - testing"
itm.parse(orig_str)
itm_str = str(itm)
plan.ok(orig_str==itm_str, "Test 'not ok' with missing number and converted back to a string.")

orig_str = "ok 9 testing"
expect_str = "ok 9 - testing"
itm.parse(orig_str)
itm_str = str(itm)
plan.ok(expect_str==itm_str, "Test 'ok' with missing '-' and converted back to a string.")

orig_str = "not ok 2 testing"
expect_str = "not ok 2 - testing"
itm.parse(orig_str)
itm_str = str(itm)
plan.ok(expect_str==itm_str, "Test 'not ok' with missing '-' and converted back to a string.")

orig_str = "ok 1 - testing # SKIP something"
itm.parse(orig_str)
itm_str = str(itm)
plan.ok(orig_str==itm_str, "Test 'ok' with skip and converted back to a string.")

orig_str = "not ok 1 - testing # TODO something else"
itm.parse(orig_str)
itm_str = str(itm)
#print(itm_str)
plan.ok(orig_str==itm_str, "Test 'not ok' with todo and converted back to a string.")

orig_str = "# this is a test..."
itm.parse(orig_str)
itm_str = str(itm)
plan.ok(orig_str==itm_str, "Testing '# diagnostic...' and converted back to a string.")

orig_str = "ok 1 - testing something"
itm.parse(orig_str)
plan.ok(itm.type()=="pass", "testing item type directly")
plan.ok(itm=="pass", "testing item type infered")
plan.ok(itm=="PaSs", "testing item camilcase type")

orig_str = "ok 123 - a test # SKIP why are we skipping?"
itm.parse(orig_str)
itm_str = str(itm)
plan.ok(orig_str==itm_str, "Testing skip directive + some comments.")

orig_str = "ok 456 - a test # some comments..."
itm.parse(orig_str)
itm_str = str(itm)
plan.ok(orig_str==itm_str, "Testing comments in the directive filed.")

plan.diagnostic("just some diag to test if I am adding the test number correctly....")

orig_str = "ok 923 - test cased skip # Skip just to be sure"
itm.parse(orig_str)
plan.ok(itm.itype=="skip", "Testing case Skip directive + some comments.")

orig_str = "not ok 924 - test cased skip # ToDo just to be sure"
itm.parse(orig_str)
plan.ok(itm.itype=="todo", "Testing case ToDo directive + some comments.")

#orig_str = "not ok 924 - test cased skip # ToDo just to be sure"
#itm.parse(orig_str)
#print(itm.directive)
#plan.ok(itm.itype=="todo", "Testing case ToDo directive + some comments.")

# FIXME: need to find a way to grab the last item and parse it back.
# these are some tests in progress for verbosity metadata.
#plan.verbose = True
#plan.ok(True==False, "test todo", todo="not yet", message="cannot do")

#plan.ok(True==False, "test skip directives", skip="for now", message="cannot do")
#plan.ok(True==False, "test basic directives")

#plan.ok(True==True, "test basic directives", message="why am I doing this...", data=pdict)

results = os.path.splitext(__file__)[0]+".tap"
fout = open(results,'w')
fout.write(str(plan))

"""Base class for the Test Anything Protocol (TAP) Pan.

FIXME: ...

"""
#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import os, sys, logging

from vkdash.tap import Tap_Item
from copy import deepcopy
from collections import OrderedDict
import yaml, yamlordereddictloader

#-----------------------------------------------------------------------------
# Public interface
#-----------------------------------------------------------------------------
__all__ = ['Plan',
           'is_tap']


def is_tap(infile, ext=".tap"):
    """Check if the file specified conforms to the naming Perl test naming
       convention.  By default the extension is ".tap" for TAP output,
       but this is overwritable.

    """
    _base, _ext = os.path.splitext(os.path.basename(infile))
    if _ext != ext:
        return False
    
    logging.info(" '%s' is a TAP file." % infile)
    if os.path.getsize(infile) < 1:
        logging.error(" No TAP data! You probably forgot to have your tests output TAP.")
        return False

    return True


class Plan:
    """The Testing Anything Protocol (TAP) Plan contains collections of a
       single test run.

    """

    def __init__(self, atexit=False,
                 outname=os.path.splitext(sys.argv[0])[0]+".tap",
                 verbose=False, data=None):
        """Common constructor shared by all TAP Plans."""
        self.version = "TAP version 13"
        self.tests = deepcopy([])
        self.test_count = 0
        self.saved = False
        self.atexit = atexit
        self.file_name = outname
        self.verbose = verbose
        self.data = OrderedDict()
        if data:
            self.data.update(data)
            
        if atexit:
            import atexit
            atexit.register(self._atexit_save)

    def diagnostic(self, message, data=None):
        """Create an embedded diagnostic message in the plan."""
        ok = Tap_Item()
        ok.description = deepcopy(message)
        ok.itype = "diag"
        self.tests.append(ok)

        if data:
            ok.data.update(data)

    def eq_ok(self, inpt, expect, description='', message=None, skip=None,
              todo=None, severity=None, data=None):
        """Base function for evaluating a test and creating a reported TAP item."""

        ok = Tap_Item()

        if data is None:
            ok.data  = OrderedDict() 
        else:
            ok.data.update(data)

        self.test_count += 1
        ok.number = self.test_count
        ok.itype = "unknown"
            
        ok.description = deepcopy(description)

        if skip and todo:
            logging.warn("WARNING: skip and todo are both set. skip taking precidence")

        # allow empty skip and todo messages to be used
        if skip is not None:
            ok.ok = True
            ok.directive = skip
            ok.itype = "skip"
            self.tests.append(ok)
            return

        if todo is not None:
            ok.itype = "todo"
            ok.ok = False
            ok.directive = todo
            if message:
                ok.data['message'] = deepcopy(message)
            # This assumes that it is reporint failure from the todo
            # and not as a user defined severity.  This conforms to
            # the documented example.
            if self.verbose:
                ok.data['severity'] = deepcopy("todo")

            self.tests.append(ok)
            return

        if not skip and not todo:
            got = deepcopy(inpt)
            expect = deepcopy(expect)
            if callable(inpt):
                got = deepcopy(inpt())

            if got == expect:
                ok.ok = True
                ok.itype = "pass"
            else:
                ok.ok = False
                ok.itype = "fail"

            if not severity and self.verbose:
                severity = ok.itype
        else:
            got = None
            expect = None

        # if user specified they want the got, expect, message or
        # severity values displayed, then overwrite with the evaluated
        # values.
        if 'got' in ok.data or 'expect' in ok.data:
            ok.data['got'] = got
            ok.data['expect'] = expect
        if 'severity' in ok.data:
            ok.data['severity'] = deepcopy(severity)
        if 'message' in ok.data:
            if not message:
                message = "None"
            ok.data['message'] = deepcopy(message)

        if not ok.ok:
            if message:
                ok.data['message'] = deepcopy(message)
            if severity or self.verbose:
                ok.data['severity'] = deepcopy(severity)
            
            if not (type(got) is bool and type(expect) is bool):
                ok.data['got'] = got
                ok.data['expect'] = expect

        self.tests.append(ok)

    def ok(self, inpt, description='', message=None, skip=None,
           todo=None, severity=None, data=None):
        """wrapper for the most common case of 'eq_ok' usage."""
        self.eq_ok(inpt, True, description, message, skip, todo, severity, data)

    def __repr__(self):
        """Build a nice string representation of this plan"""
        if self.version:
            outstr = deepcopy(self.version)+'\n'

        outstr += "1..%d"%(self.test_count)
        if self.data:
            outstr += "\n  ---\n"

            stream = yaml.dump(self.data,
                               Dumper=yamlordereddictloader.Dumper,
                               default_flow_style=False, indent=4)
            stream = "  "+stream.replace('\n', '\n  ')
            outstr += stream

            outstr += "..."

        for t in self.tests:
            outstr += '\n'+str(t)
        return outstr

    def _atexit_save(self):
        """if the _atexit_save method is registered, then the contents of the
           plan are automatically saved when the plan goes out of
           scope or the program terminates."""
        if not self.saved and self.atexit:
            self.write()
    
    def __enter__(self):
        return self
    
    def __exit__(self):
        pass

    def __del__(self):
        pass

    def write(self, fname=None):
        if fname is None:
            fname = self.file_name

        fout = open(fname,'w')
        fout.write(self.__repr__())
        fout.close()
        self.saved = True

    def __nonzero__(self): # FIXME: how do we define standard behaviour between py2 and py3
        return self.__bool__()
    
    def __bool__(self):
        """Boolean pass/fail test for this plan. py3?"""
        for t in self.tests:
            if type(t.ok) is bool and not t.ok:
                return False
        return True

    def parse(self, lines):
        """Parse either a collection of TAP items as either a list of strings,
        or a single string made up of carrage return seperated test
        items.  This version of the code considers the version string
        and plan specification to be an item in itself -- which can
        both include YAML metadata

        """

        # convert the input to a list of strings if necessary
        if type(lines) is str:
            lines = lines.split('\n')
        elif type(lines) is list:
            pass
        else:
            logging.warn(" (TAP_Plan:parse) type '%s' not known." % str(type(lines)))
            return

        max_test = None
        while lines:
            # process each line (including metadata).  The nre tap
            # parser only strips off the lines it needs and returns
            # the rest of the input, and an empty list when done.
            itm = Tap_Item()
            lines = itm.parse(lines, fname=self.file_name)

            if itm.itype in ["pass","fail","skip","todo"]:
                self.test_count += 1
                if itm.number <= 0:
                    self.test_count
            elif itm.itype == "version":
                self.version = itm.description
                del itm
                continue
            elif itm.itype == "plan":
                spl = itm.description.split()
                logging.debug(" test range = '%s' .. '%s'"%(spl[0],spl[1]))
                max_test = int(spl[1])
                self.data.update(itm.data)
                continue
            self.tests.append(itm)

        # test that the tests are in range
        if isinstance(max_test, int):
            if max_test != self.test_count:
                logging.warn("")
                logging.warn(" in file: '%s'"%self.file_name)
                logging.warn(" The max test number (%d) and test count (%d) are not equal"%(max_test,self.test_count))
        else:
            logging.warn("")
            logging.warn(" in file: '%s'"%self.file_name)
            logging.warn(" Malformed Plan -- plan never defined.")

    def open(self, fname):
        """Open and parse a a TAP output file.

        """
        logging.debug(" open and reading '%s'"%fname)

        self.file_name = fname
        try:
            #lines = [l.strip() for l in open(fname,'r').readlines()]
            lines = [l.replace('\n','') for l in open(fname,'r').readlines()]
        except:
            lines = []

        self.parse(lines)

    def count(self, values=None):
        """Return how many of the plan's tests passed, failed, todos, or were skiped."""

        if values is None:
            values = {"pass": 0, "fail": 0, "todo": 0, "skip": 0}

        if type(values) is not dict:
            logging.error(" values must be a dictionary.")
            
        keys = values.keys()
        if "pass" not in keys: values["pass"] = 0
        if "fail" not in keys: values["fail"] = 0
        if "skip" not in keys: values["skip"] = 0
        if "todo" not in keys: values["todo"] = 0
            
        for t in self.tests:
            if t.passed(): values["pass"] += 1
            elif t.is_skip(): values["skip"] += 1
            elif t.is_todo(): values["todo"] += 1
            elif t.failed(): values["fail"] += 1
            elif t.is_unknown():
                #logging.error("")
                #logging.error(" in file: '%s'"%self.file_name)
                #logging.error(" unknown item type")
                pass # errors/warnings handled in item
            else:
                pass # ignore the diagnostics, plan and version strings.

            continue

        return values

    def passed(self, todo=True):
        """Return True if all of the tests pass.  If todo=True, then count
           todos a a failure.
        """
        current = self.count()
        if current["todo"] != 0:
            return False
        if current["fail"] != 0:
            return False
        return True

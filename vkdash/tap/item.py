"""Base class for a Test Anything Protocol (TAP) test item.

Each item can be made up of test 'ok' or 'not ok', or can contain diagnostic comments.

FIXME: more???

"""
#-----------------------------------------------------------------------------
# Public interface
#-----------------------------------------------------------------------------
__all__ = ['Tap_Item']

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import logging
from collections import OrderedDict
import yaml

# FIXME: this could use to be cleaned up a little more...

#import re
#class DummyLoader(yaml.SafeLoader):
#    pass
#DummyLoader.add_implicit_resolver(u'!yeah',re.compile(ur'Yeah'),first='Y')

class Tap_Item:
    # variables set in reset() function.
    
    def __init__(self, str=None): #str shadowing python's str
        """Common constructor shared by all TAP items."""
        self.reset()
        if str is not None:
            self.parse(str)

    def __repr__(self):
        """Build a nice string representation of this test item"""

        directive = ""
        if self.directive or self.is_skip() or self.is_todo():
            directive = " # "

        if self.passed():
            tap = "ok"
            directive += self.directive
        elif self.failed():
            tap = "not ok"
            directive += self.directive
        elif self.is_skip():
            tap = "ok"
            directive += "SKIP "+self.directive
        elif self.is_todo():
            tap = "not ok"
            directive += "TODO "+self.directive
        elif self.is_diagnostic():
            tap = "# %s" % self.description
        else:
            logging.error(" internal error: type currently not supported.")
            raise()
            #return "what type is this"

        if self.number > 0:
            tap += " %s" % str(self.number)
            
        if self.description and not self.is_diagnostic():
            tap += " - %s" % self.description

        tap += directive

        if self.dump or self.data:
            tap += "\n  ---\n"

            stream = yaml.dump(self.data,  default_flow_style=False, indent=4)
            stream = "  "+stream.replace('\n', '\n  ')
            tap += stream

            tap += "..."

        return tap

    def is_diagnostic(self):
        """Return True if this item is a diagnostic comment."""
        return self.itype == "diag"

    def is_todo(self):
        """Return True if this item is a todo item."""
        return self.itype == "todo"

    def is_skip(self):
        """Return True if this item is a skipped item."""
        return self.itype == "skip"

    def passed(self):
        """Return True if this item is ok."""
        return self.itype == "pass"

    def failed(self):
        """Return True if this item is not ok."""
        return self.itype == "fail"

    def reset(self):
        """ Reset the items internal variables"""
        self.ok = ''
        self.description = ''
        self.directive = ''
        self.number = -1
        self.data = OrderedDict()
        self.dump = OrderedDict()
        self.itype = ''

    def type(self,t=None):
        if t:
            self.itype = t.lower()
        return self.itype

    def __eq__(self, x):
        if type(x) is str:
            # assume that we are testing the type.
            return x.lower()==self.itype
        # FIXME: we might want to test other types as well, but we
        # have to define the meaning.
        return False


    def parse(self, line):

        """Parse the item from a collection of strings, or a single string
           that is carrage return seperated

        """

        self.reset()

        # assume that this is a diagnostic message unless it is parsed
        # to be something else.
        self.itype = "diag"

        # now parst the string
        if type(line) is str:
            lines = line.split('\n')
            line = lines[0]
        elif type(line) is list:
            lines = line
            line = lines[0]
        else:
            logging.error(" (TAP_Item:parse) type '%s' not known." % str(type(line)))
            return

        if line.strip().lower()[0] == '#':
            self.description = line.strip()[1:].strip()
        else:
            if line.strip().lower()[:2] == "ok":
                line = line.strip()[2:].strip()
                self.ok = True
                self.itype = "pass"
            elif line.strip().lower()[:6] == "not ok":
                line = line.strip()[6:].strip()
                self.ok = False
                self.itype = "fail"

            # check for empty -- isdigit pukes otherwise...
            if not line:
                return

            # parse optional test number
            if line.strip()[0].isdigit():
                spl = line.strip().split(' ')
                self.number = int(spl[0])
                line = line.strip()[len(spl[0]):]

            # remove optional dash
            if line.strip()[0] == '-':
                line = line.strip()[1:]

            # find the length of the descriptions
            try:
                ppos = line.strip().index('#')
                self.description = line.strip()[:ppos].strip()
            except: # 'too broad an exception clause' warning
                ppos = -1
                self.description = line.strip()

            # is there a directive?
            if ppos > -1:
                line = line.strip()[ppos+1:]
                spl = line.strip().split(' ')
                if spl[0].lower() == "skip":
                    # verify that the ok valuse is appropriate
                    if not self.ok:
                        logging.error(" TAP item should return 'ok' when it is skipped.")
                    ppos = 4
                    self.itype = "skip"
                elif spl[0].lower() == "todo":
                    if self.ok:
                        logging.error(" TAP item should return 'ok' when it is a ToDo.")
                    ppos = 4
                    self.itype = "todo"
                else:
                    ppos = 0

                self.directive = line.strip()[ppos:].strip()

        if len(lines) == 1:
            return

        # FIXME: might need to do something special to parse the dumps

        p = '\n'.join(lines[2:-1])
        self.data = yaml.load(p)

    def _parse_data(self, ln, lines):
        """ Helper function to subparse the data field."""
        length = len(lines)
        logging.info(" in parse_data:")
        while ln < length:
            spl = lines[ln].strip().split()
            if spl[0] in ["...", "data:"]:
                return ln -1  # the caller will increment after
                              # successful parse
                        
            k, v = lines[ln].strip().split(':')
            self.data[k] = v
            logging.info("     key = %s  value = %s" % (k, v))

            ln += 1
        logging.info("")  # NOTE used to be logging.error, but it's unclear why since it seems to serve as just a nl
        return ln

    def _parse_dump(self, ln, lines):
        """ Helper function to subparse the dump field."""
        length = len(lines)
        logging.info(" in parse_data:")
        while ln < length:
            spl = lines[ln].strip().split()
            if spl[0] in ["...", "data:"]:
                return ln - 1  # the caller will increment after
                              # successful parse
                        
            k, v = lines[ln].strip().split(':')
            self.dump[k] = []

            ln += 1
            while ln < length:
                if '-' != lines[ln].strip()[0]:
                    break
                dump_itm = lines[ln].strip()[1:].strip()
                self.dump[k].append(dump_itm)
                ln += 1

        logging.info("")  # NOTE used to be logging.error, but it's unclear why since it seems to serve as just a nl
        return ln

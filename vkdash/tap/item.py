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
import yaml, yamlordereddictloader

# FIXME: this could use to be cleaned up a little more...

class Tap_Item:
    def __init__(self, str=None, fname=None): #str shadowing python's str
        """Common constructor shared by all TAP items."""
        self.reset()
        if str is not None:
            self.parse(str, fname)

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
        elif self.is_empty():
            tap = ""
        else:
            logging.warn(" internal error: type currently not supported.")
            #raise()
            #return "what type is this"
            tap = "UNKNOWN"

        if self.number > 0:
            tap += " %s" % str(self.number)
            
        if self.description and not self.is_diagnostic():
            tap += " - %s" % self.description

        tap += directive

        if self.data:
            tap += "\n  ---\n"

            stream = yaml.dump(self.data,
                               Dumper=yamlordereddictloader.Dumper,
                               default_flow_style=False, indent=4)
            stream = "  "+stream.replace('\n', '\n  ')
            tap += stream

            tap += "..."

        return tap

    def is_version(self):
        """Return True of this is the version string."""
        return self.itype == "version"

    def is_diagnostic(self):
        """Return True if this item is a diagnostic comment."""
        return self.itype == "diag"

    def is_empty(self):
        """Return True if this item is an ampty string."""
        return self.itype == "empty"

    def is_unknown(self):
        """Return True if this item is of unknown type."""
        return self.itype == "unknown"

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

    def __parse_number__(self, pstr):
        num = 0

        pstr = pstr.lstrip()
        if not pstr[0].isdigit():
            return False,0,pstr
        
        for res in range(0,len(pstr)):
            if not pstr[res].isdigit():
                break

        if res == len(pstr)-1:
            res += 1

        num = int(pstr[:res])
        pstr = pstr[res:].lstrip()

        return True,num,pstr
    
    def parse(self, line, fname=None):

        """Parse the item from a collection of strings, or a single string
           that is carrage return seperated

        """

        self.reset()

        self.itype = "unknown"  # FIXME: make it unknown...

        # now parst the string
        if type(line) is str:
            lines = line.split('\n')
        elif type(line) is list:
            lines = line
        else:
            logging.warn("")
            logging.warn(" in file: '%s'"%fname)
            logging.warn(" (TAP_Item:parse) type '%s' not known." % str(type(line)))
            return []
        line = lines[0]

        # handle empty strings
        if not line:
            self.itype = "empty"
            if len(lines) > 0:
                # this line is empty, but the next is not
                return lines[1:]
            else:
                return []

        # now parse the items
        if line.strip()[0] == '#':
            self.itype = "diag"
            self.description = line.strip()[1:].strip()
        elif line.strip().lower()[:3] == 'tap':
            self.itype = "version"
            self.description = line.strip().strip()
            logging.debug(" version string = '%s'"%self.description)
        elif line.strip()[:3] == '1..':
            self.itype = "plan"
            spl = line.strip().lower().split("..")
            self.description = "%s %s"%(spl[0],spl[1])
            logging.debug(" plan = '%s'"%self.description)
        else:
            if line.strip().lower()[:2] == "ok":
                line = line.strip()[2:].strip()
                self.ok = True
                self.itype = "pass"
            elif line.strip().lower()[:6] == "not ok":
                line = line.strip()[6:].strip()
                self.ok = False
                self.itype = "fail"

            # check if the rest of the line is empty -- isdigit pukes
            # otherwise...
            if line:
                # parse optional test number
                # also remove the strips...
                tst,num,line = self.__parse_number__(line)
                if tst:
                    self.number = num

                # remove optional dash
                try:
                    if line.strip()[0] == '-':
                        line = line.strip()[1:].lstrip()
                except:
                    pass

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
                            logging.warn("")
                            logging.warn(" in file: '%s'"%fname)
                            logging.warn(" TAP item should return 'ok' when it is skipped.")
                        ppos = 4
                        self.itype = "skip"
                    elif spl[0].lower() == "todo":
                        if self.ok:
                            logging.warn("")
                            logging.warn(" in file: '%s'"%fname)
                            logging.warn(" TAP item should return 'ok' when it is a ToDo.")
                        ppos = 4
                        self.itype = "todo"
                    else:
                        ppos = 0

                    self.directive = line.strip()[ppos:].strip()

        if self.itype == "unknown":
            logging.warn("")
            logging.warn(" in file: '%s'"%fname)
            logging.warn(" undefined item type in '%s'"%lines[0])
            
        if len(lines) <= 1:
            return []

        yaml_head = None
        yaml_tail = None
        if lines[1].strip() == '---':
            yaml_head = 2
            # this is a YAML message.  Find the end string and parse
            # it.  Also return the index of the next item.
            for i in range(2,len(lines)):
                if lines[i].strip() == '...':
                    yaml_tail = i
                    break

        # sanity check
        if bool(yaml_head) != bool(yaml_tail):
            logging.warn("")
            logging.warn(" in file: '%s'"%fname)
            logging.warn(" Malformed YAML expression at or near: \n%s"%'\n'.join(lines))
            return []

        if yaml_head:
            self.data.update(yaml.safe_load('\n'.join(lines[yaml_head:yaml_tail])))
            return lines[yaml_tail+1:]
        else:
            return lines[1:]

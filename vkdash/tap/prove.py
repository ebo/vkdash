"""User accessible functions and main interface for VKDash's TAP
prover.

FIXME:... finds all test programs and executes them.  Then parses the
resultant TAP output for summary statistics.

"""

# -----------------------------------------------------------------------------
# Public interface
# -----------------------------------------------------------------------------
__all__ = ['prove', 'find_tests']

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import os
import logging
import shutil
from vkdash.tap import *
import datetime


def _is_test(infile, exts=None):
    """internal function to test if a file is recognized as a test
    program.  By convention, the test program names are prepended with
    a 'test_' or 't_' or appended with a '_test' or '_t'.

    """
    import re

    if exts is None:
        exts = [".py"]

    _base, _ext = os.path.splitext(os.path.basename(infile))
    tparse = re.compile('^test_|^t_|_test$|_t$', re.IGNORECASE)
    match = tparse.match(_base)
    if not (match and _ext in exts):
        return False

    logging.debug(" '%s' is a test." % infile)
    return True


def find_tests(inf=".", exts=None):
    """find all files in the collection of files or directores which are
    recognized as test programs.

    """

    if exts is None:
        exts = [".py"]

    if not os.path.exists(inf):
        logging.error(" (find_tests): input '%s' does not exist." % inf)
        return []
    if os.path.isfile(inf):
        return [inf]
    elif os.path.isdir(inf):
        # walk the dir tree...
        tree = []
        for root, dirs, files in os.walk(inf):
            for f in files:
                if _is_test(os.path.join(root, f), exts):
                    tree.append(os.path.join(root, f))
        return tree


def prove(inf=None, exts=None, config=None, outdir='', date=None, run=True):
    """find all files in the collection of files or directores which are
    recognized as test programs, run them, and then sumerize the
    results.

    """
    import subprocess

    if inf is None:
        inf = [os.getcwd()]

    if exts is None:
        exts = [".py", ""]

    plans = []

    total_tests = 0
    total_pass = 0
    total_fail = 0
    total_todo = 0
    total_skip = 0

    if type(inf) is not list:
        inf = [inf]

    tree = []
    for f in inf:
        if not os.path.exists(f):
            logging.error(" (Prove): input '%s' does not exist." % f)
            continue

        tree += find_tests(f, exts)

    proved = 0
    failed = 0

    # TODO condense the following two data structures into an assosciated array?
    configurations = []

    if config:
        if os.path.isfile(config):
            with open(config, 'r') as cfile:  # TODO config location?
                logging.info("Loading configuration file.")

                lines = map(str.strip, cfile.readlines())
                for line in lines:
                    if ':' not in line:  # NOTE obviously incomplete
                        configurations.append(line)
                    else:
                        config = line[:len(line) - 1] 
                        
                platform = os.name

                platform_cmd = ''

                if platform == 'nt':
                    platform_cmd = 'activate'
                
                elif platform == 'posix':
                    platform_cmd = 'source activate'

                else:
                    logging.error(platform + " is an unsupported platform!")  # TODO raise exception?
                    return

                for i, configuration in enumerate(configurations):
                    configurations[i] = platform_cmd + ' ' + configuration

        else:
            logging.info("No configuration file detected")
    else:
        configurations.append("")

    for fname in tree:
        for configuration in configurations:
            if configuration:
                cmd = configuration + ';' + "python " + fname
            else:
                cmd = "python " + fname
                
            if run and not fname.endswith(".tap"):
                logging.info("")
                logging.info(" running cmd: %s" % cmd)
                status = subprocess.call(cmd, shell=True)  # FIXME we have to ensure shell use is safe!
                if status != 0:
                    logging.error(" test '%s' returned a status of %s" % (fname, str(status)))
  
            plan = Plan()  # plan is shadowing another 'plan' decl somewhere, somehow (as claims by pycharm)

            tapname = os.path.splitext(fname)[0] + ".tap"

            # now move the output to the configuration name
            p, f = os.path.split(tapname)
            if outdir:
                p = outdir

            if not date:
                date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

            if config:
                new_tap = os.path.join(p, config + '_' + configuration.split()[-1] + ':' + date + ':' + f)
            else:
                new_tap = os.path.join(p, f)

            if os.path.exists(tapname):
                # when we have configurations set, we need to name
                # mangle the results
                logging.debug(" moving %s to %s" % (tapname, new_tap))
                shutil.move(tapname, new_tap)
            
            logging.info(" processing TAP file: %s" % new_tap)
            plan.open(new_tap)
            
            counts = plan.count()
            plans.append({"file": new_tap, "passed": counts['pass'], "failed": counts['fail'], "skipped": counts['skip'], "todos": counts['todo']})

            total_tests += counts['pass'] + counts['fail'] + counts['todo'] + counts['skip']
            total_pass += counts['pass']
            total_fail += counts['fail']
            total_todo += counts['todo']
            total_skip += counts['skip']

    # FIXME: this name should be the configuration name
    totals = {"name": config, "total_pass": total_pass,
              "total_fail": total_fail, "total_skip": total_skip, "total_todo": total_todo}

    return plans, totals


def main():
    """Main entry point for the vkprove program.

    """

    import argparse
    import sys
    parser = argparse.ArgumentParser(prog=os.path.basename(os.path.basename(sys.argv[0])))
    parser.add_argument("infiles", type=str, nargs='+',
                        help="input files or directorys")

    parser.add_argument("-O", "--outdir", type=str, default='',
                        help="output directory (used for archiving)")
    
    parser.add_argument("-C", "--config", type=str, default=None,
                        help="use a configuration")
    
    parser.add_argument("-D", "--date", type=str, default='',
                        help="use the date")
    
    parser.add_argument("-N", "--no-run", action="store_true", default=False, 
                        help="do not run as a command, and process existant TAP file: default=%(default)s]")

    parser.add_argument("-R", "--raw", action="store_true", default=False, 
                        help="process the taw TAP files: default=%(default)s]")
        
    parser.add_argument("-v", "--verbose", action="store_true", default=False, 
                        help="produce diagnostic output [optional: default=%(default)s]")
    parser.add_argument("-d", "--debug", action="store_true", default=False, 
                        help="produce diagnostic output [optional: default=%(default)s]")

    args = parser.parse_args()
    if args.verbose is not False:
        logging.basicConfig(level=logging.INFO)
    if args.debug is not False:
        logging.basicConfig(level=logging.DEBUG)

    if args.outdir and not os.path.exists(args.outdir):
        logging.warn(" output directory '%s' does not exist" % args.outdir)
        os.makedirs(args.outdir)

    logging.debug(" inputs = '%s'" % args.infiles)
    logging.debug(" ")

    date = args.date
    if args.config and not args.date:
        date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    if args.raw:
        tapfiles = []
        for f in args.infiles:
            logging.info(" processing raw '%s'"%f)
            for root, dir, files in os.walk("."):
                import fnmatch
                for items in fnmatch.filter(files, "*.tap"):
                    tapfiles.append(os.path.join(root,items))
    else:
        tapfiles = args.infiles
            
    results, totals = prove(tapfiles, config=args.config, date=date, outdir=args.outdir, run=not args.no_run)

    print ("\nTest Summary Report")
    if args.config:
        print ("  for config: %s" % args.config)
        
    print ("===================")

    for r in results:
        print ("Passed: %3d Failed: %3d ToDos: %3d Skips: %3d | %s" % (r['passed'], r['failed'], r['todos'], r['skipped'], r['file']))

    print ("===================")
    print ("Total Plans: %3d  Passed: %3d Failed: %3d ToDos: %3d Skips: %3d" %
           (len(results), totals['total_pass'], totals['total_fail'], totals['total_todo'], totals['total_skip']))
    #print ("Total Plans: %3d  Passed: %3d  Failed: %3d" % (len(results), totals['total_pass'], totals['total_fail']))
    if totals['total_fail'] == 0:
        print ("\nResult: Passed\n")
    else:
        print ("\nResult: Failed\n")

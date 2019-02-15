"""User accessible functions and main interface for VKDash's TAP
prover.

FIXME:... finds all test programs and executes them.  Then parses the
resultant TAP output for summary statistics.

"""

#-----------------------------------------------------------------------------
# Public interface
#-----------------------------------------------------------------------------
__all__ = ['prove', 'find_tests']

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import os
import logging
import shutil
from vkdash.tap import *
from collections import OrderedDict

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

    logging.info(" '%s' is a test."%infile)
    return True


def find_tests(inf=".", exts=None):
    """find all files in the collection of files or directores which are
    recognized as test programs.

    """

    if exts is None:
        exts = [".py"]

    if not os.path.exists(inf):
        logging.error(" (find_tests): input '%s' does not exist."%inf)
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


def prove(inf=None, exts=None, config=None, outdir=''):
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
            logging.error(" (Prove): input '%s' does not exist."%f)
            continue

        tree += find_tests(f, exts)

    proved = 0
    failed = 0

    '''
    # TODO condense the following two data structures into an assosciated array
    configurations = []
    config_name = []

    if os.path.isfile('config.yml'):
        with open('config.yml', 'r') as config:  # TODO standardize config location
            logging.info("Loading configuration file.")

            runtimes = []

            lines = map(str.strip, config.readlines())
            for line in lines:
                if ':' not in line:  # NOTE obviously incomplete
                    runtimes.append(line)
                else:
                    config_name.append(line[:len(line)-1])

            platform = os.name

            # NOTE - Preliminary support for anaconda python. 
            # NOTE - Supporting 'bare' python installs over nt / posix systems is a nightmare ...
            #        ... it is not great in anacoda, but it is much easier. This is tricky to design flexibly ...

            # The way my C++ projects build are with a single shell or bash script. No Make, Ninja, or any other build tool.
            # This is simple, portable, and understandable. All the information necessary to build is in 1 file.
            # The way our configuration system currently works is to, in essense, gather the necessary information from the config file ...
            # to build the build script. I think, in practice, we should support both approaches by general method. But that's for another day ...

            # Many containerized approaches use a container (or network of containers) as a configuration (variations on has-a, is-a relationships) ...
            # Testing configurations therefore just entails testing the containers.
            # This forces the user to do all the upfront configuration monkey puzzle. In practice, this is even more complicated than it sounds ...
            # because containers are not necessarily isomorphic with user systems due to state leak ... see below ...

            # Anaconda's environments feels like a container ... but pre-installed python can be both 'leaky' and 'sticky' ...
            # ... so I have developed a special fobia trying to confirm what environment we're really evaluating when we 'prove' a directory.

            if config_name[0] == "conda":  # TODO obviously incomplete
                platform_cmd = []

                if platform == 'nt':
                    platform_cmd = ["activate"]
                
                elif platform == 'posix':
                    platform_cmd = ["source", "activate"]

                else:
                    logging.error(platform + " is an unsupported platform!")  # TODO raise exception?
                    return

                for runtime in runtimes:
                    configurations.append([*platform_cmd, runtime])
            else:
                logging.error("Unsupported configuration!")

    else:
        logging.info("No configuration file detected")
    '''

    #build_dir = _dir
    #if not _dir or not _ConfirmFolderAccessAndPermissions(_dir):
    #    return
    if config:
        config += ':'
    for fname in tree:  # 'file' shadows python's file object name.
        '''
         for configuration in configurations:
            cmd = [*configuration, "; python ", file]  # NOTE 3.x list unpacking
        '''
        cmd = ["python", fname]
        logging.info("")
        logging.info(" running cmd: %s" % ' '.join(cmd))
        status = subprocess.call(cmd)
        if status != 0:
            logging.error(" test '%s' returned a status of %s" % (fname, str(status)))
            failed += 1
        else:
            proved += 1

  
            plan = Plan()  # plan is shadowing another 'plan' decl somewhere, somehow (as claims by pycharm)

            tapname = os.path.splitext(fname)[0]+".tap"

            # now move the output to the configuration name
            p,f = os.path.split(tapname)
            if outdir:
                p = outdir
            new_tap = os.path.join(p,config+f)
            if os.path.exists(tapname):
                logging.info(" moving %s to %s"%(tapname,new_tap))
                shutil.move(tapname, new_tap)
            
            plan.open(new_tap)
            
            counts = plan.count()
            plans.append({"file":new_tap,"passed":counts['pass'],"failed":counts['fail'],"skipped":counts['skip'],"todos":counts['todo']})

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
    import os, sys, logging
    parser = argparse.ArgumentParser(prog=os.path.basename(os.path.basename(sys.argv[0])))
    parser.add_argument("infiles", type=str, nargs='+',
                        help="input files or directorys")

    parser.add_argument("-O", "--outdir", type=str, default='',
                        help="output directory (used for archiving)")
    
    parser.add_argument("-C", "--config", type=str, default=None,
                        help="use a configuration")
    
    parser.add_argument("-D", "--date", type=str, default='',
                        help="use the date")
    
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

    logging.info(" inputs = '%s'" % args.infiles)
    logging.info(" ")

    config_name = ''
    date = args.date
    if args.config:
        import datetime

        if not args.date:
            date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        config_name = "%s:%s"%(args.config,date)

    results, totals = prove(args.infiles, config=config_name,outdir=args.outdir)

    print ("\nTest Summary Report")
    if config_name:
        print ("  for config: %s"%config_name)
        
    print ("===================")

    for r in results:
        print ("%s (Tests: %d Failed: %d" % (r['file'], r['passed'], r['failed'])),
        if r['todos']:
             print (" ToDos: %d"%r['todos']),
        if r['skipped']:
             print (" ToDos: %d"%r['skipped']),
        print (")")

                
    print ("===================")
    print ("Total Plans: %d  Tests: %d  Failed: %d" % (len(results), totals['total_pass'], totals['total_fail']))
    if totals['total_fail'] == 0:
        print ("\nResult: Passed\n")
    else:
        print ("\nResult: Failed\n")

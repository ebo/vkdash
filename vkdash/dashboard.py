from vkdash.header import *
from vkdash.tap import *
from vkdash.tap import is_tap

import yaml # FIXME: clean up yaml.bla...

def dumper(key, itm, indent=4, level=0):
    stream = " " * (indent * level) + key + ":"
    if isinstance(itm, dict):
        stream += "\n"
        for k in itm:
            stream += dumper(k, itm[k], indent, level+1)
    else:
        stream += " " + str(itm) + "\n"
    
    return stream

# TODO refactor open / walk recursive confusion
# TODO NOSHIP FIXME dashboard output different (too many configurations) on OSX and LINUX. May be a problem with VKprove.

import os
import logging

__all__ = ['find_tap_files',
           'Dashboard'
           ]

accessible = False

class Dashboard:
    name = "Generic"
    plans = []
    format = "html"

    def __init__(self):
        pass

    def _yaml2html(self, data):
        if not data:
            return ""
        
        htmlstr  = '\t\t<details>\n'
        htmlstr += '\t\t<summary> YAML </summary>\n'
        htmlstr += "<pre>\n"

        for k in data:
            htmlstr += dumper(k,data[k],indent=4)

        htmlstr += "</pre>\n"
        htmlstr += '\t\t</details>\n'
        
        return htmlstr
    
    def _plan_html(self, plan, test_number=0):
        """Build output as HTML output"""
        passed = 0
        overview_passed = ""

        failed = 0
        overview_failed = ""

        skipped = 0
        overview_skipped = ""

        todos = 0
        overview_todo = ""

        plan.saved = True

        def _color_it(itm):
            this_item = '<tr>\n'

            if itm.is_todo():
                this_item += '  <td><div class="report todo"></div></td><td>\n'
                msg = "not ok"
            elif itm.is_skip():
                msg = "ok"
                this_item += '  <td><div class="report skip"></div></td>\n'
            elif itm.is_diagnostic():
                this_item += '  <td><div class="report diag"></div></td>\n'
                msg = "#"
            elif itm.failed():
                this_item += '  <td><div class="report fail"></div></td>\n'
                msg = "not ok"
            elif itm.passed():
                this_item += '  <td><div class="report pass"></div></td>\n'
                msg = "ok"
            else:
                print("warning: bad item type... look into it...")
                msg = "UNKNOWN"

            this_item += '  <td>'+str(msg)+'</td>\n'

            if itm.number > 0:
                this_item += '  <td>'+str(itm.number)+'</td>\n'
            else:
                this_item += '  <td></td>\n'

            this_item += '  <td>'+ str(i.description) +'</td>\n'
            this_item += '  <td>'+ i.directive +'</td>\n'
            this_item += '  <td>'+ self._yaml2html(i.data) +'</td>\n'
            this_item += '</tr>\n'

            return this_item
        
        ordered_tests = ""

        ordered_tests += '<table style="width:100%">'
        ordered_tests += '<tr>'
        ordered_tests += '<th></th>'
        ordered_tests += '<th>Pass</th>'
        ordered_tests += '<th>Test #</th>'
        ordered_tests += '<th>Description</th>'
        ordered_tests += '<th>Directive</th>'
        ordered_tests += '<th>Metadata</th>'
        ordered_tests += '</tr>'

        for i in plan.tests: 
            test_number += 1
            ordered_tests += _color_it(i)
            if i.passed():
                passed += 1
                overview_passed += '<a href="#' + str(test_number) + \
                                   '"><div class="view pass"' + ' ' + \
                                   'title="' + i.description + \
                                   '"></div></a>\n\t'
            elif i.failed():
                failed += 1
                overview_failed += '<a href="#' + str(test_number) + \
                                   '"><div class="view fail"' + ' ' + \
                                   'title="' + i.description + \
                                   '"></div></a>\n\t'
            elif i.is_skip():
                skipped += 1
                overview_skipped += '<a href="#' + str(test_number) + \
                                    '"><div class="view skip"' + ' ' + \
                                    'title="' + i.description + \
                                    '"></div></a>\n\t'
            elif i.is_todo():
                todos += 1
                overview_todo += '<a href="#' + str(test_number) + \
                                 '"><div class="view todo"' + ' ' + \
                                 'title="' + i.description + \
                                 '"></div></a>\n\t'
            elif not i.is_diagnostic():
                print("error: unknown item type for (%s)"%str(i))

        ordered_tests += '</table>'

        stats = ''
        if passed or failed or todos or skipped:
            stats = '<div class="report"></div>\n<div class="stat">\n'

            if failed:
                stats += '<b><div class="report fail"> Fail:' + str(failed) + '</div></b>\n'

            if todos:
                stats += '<b><div class="report todo"> ToDo:' + str(todos) + '</div></b>\n'

            if skipped:
                stats += '<b><div class="report skip"> Skip:' + str(skipped) + '</div></b>\n'

            if passed:
                stats += '<b><div class="report pass"> Pass:' + str(passed) + '</div></b>\n'

            stats += '</div>\n'

        overview_html = '<div class="overview">\n'
        overview_html += overview_failed + overview_todo + overview_skipped + overview_passed
        overview_html += '</div>\n'
        test_html = ordered_tests

        return stats, overview_html, test_html, test_number

    def __repr__(self):
        # default colors
        VK_SKIP = '#38B9ED'
        VK_PASS = '#60E589'
        VK_FAIL = '#FF5C5A'
        VK_TODO = '#FFF171'
        VK_DIAG = '#000000'

        if self.accessible:
            VK_SKIP = os.getenv('VK_SKIP',VK_SKIP)
            VK_PASS = os.getenv('VK_PASS',VK_PASS)
            VK_FAIL = os.getenv('VK_FAIL',VK_FAIL)
            VK_TODO = os.getenv('VK_TODO',VK_TODO)
            VK_DIAG = os.getenv('VK_DIAG',VK_DIAG)

        colors = '\n\
        .skip{background-color: '+VK_SKIP+';}\n\
        .pass{background-color: '+VK_PASS+';}\n\
        .fail{background-color: '+VK_FAIL+';}\n\
        .todo{background-color: '+VK_TODO+';}\n\
        .diag{background-color: '+VK_DIAG+';}\n\
        .name{}\n'

        outstr = header_lead + colors + header_end

        # find the totals and report on top
        totals = {}
        if not self.plans:
            logging.warn(" no plans found")
            outstr += footer
            return outstr

        uc = []
        ud = []
        ut = []
        for p in self.plans:
            totals = p.count(totals)
            f = os.path.basename(p.file_name)
            if ':' in f:
                c, d, t = f.split(':')
                uc.append(c)
                ud.append(d)
            else:
                t = f
            ut.append(t)
        uc = list(set(uc))
        ud = list(set(ud))
        ut = list(set(ut))

        unique_configs = len(uc)
        unique_dates = len(ud)
        unique_plans = len(ut)
        logging.info("configs: %s   %s" % (unique_configs, uc))
        logging.info("dates: %s   %s" % (unique_dates, ud))
        logging.info("plans: %s   %s" % (unique_plans, ut))

        if unique_configs >= 1:
            outstr += '<h2>' + "Number of configurations: " + str(unique_configs) + str(uc) + '</h2>\n'

        if unique_dates >= 1:
            outstr += '<h2>' + "Number of Unique Dates: " + str(unique_dates) + str(ud) + '</h2>\n'

        if unique_configs < 1:
            outstr += '<h2>' + "Plans: " + str(ut) + '</h2>\n'
        else:
            outstr += '<h2>' + "Number of Unique Plans: " + str(unique_plans) + str(ut) + '</h2>\n'

        outstr += '<h2>' + "Total Number of Plans: " + str(len(self.plans)) + '</h2>\n'

        outstr += '<h2> Result&#160Totals: </h2>\n'

        outstr += '<div class="stat">\n'

        if totals["fail"]:  # failed:
            outstr += '&#160<h2><div class="report fail"> Fail:' + str(totals["fail"]) + '</div></h2>&#160\n'
        if totals["todo"]:  # todos:
            outstr += '&#160<h2><div class="report todo"> ToDo:' + str(totals["todo"]) + '</div></h2>\n'
        if totals["skip"]:  # skipped:
            outstr += '&#160<h2><div class="report skip"> Skip:' + str(totals["skip"]) + '</div></h2>\n'
        if totals["pass"]:  # passed:
            outstr += '&#160<h2><div class="report pass"> Pass:' + str(totals["pass"]) + '</div></h2>\n'

        outstr += '</ul></div>\n'

        old_config = None
        tn = 0
        for p in self.plans:
            stats, overview, body, test_number = self._plan_html(p, tn)

            tn += test_number
            totals = p.count()

            spl = os.path.split(p.file_name)
            test_config = spl[-1]
            config = test_config.split(':')
            fname = config[-1]
            if len(config) > 1:
                config_name = config[0]
                run_date = config[1]
                config = ':'.join([config_name, run_date])

            else:
                config = ''

            if old_config != config:
                outstr += '<hr>'
                old_config = config

            outstr += '<div class="stat">\n'
            outstr += '<h2>' + config + ' ' + fname + '&#160</h2>\n'

            if totals["fail"]:  # failed:
                outstr += '<h2><div class="report fail"> Fail:' + str(totals["fail"]) + '</div></h2>\n'
            if totals["todo"]:  # todos:
                outstr += '<h2><div class="report todo"> ToDo:' + str(totals["todo"]) + '</div></h2>\n'
            if totals["skip"]:  # skipped:
                outstr += '<h2><div class="report skip"> Skip:' + str(totals["skip"]) + '</div></h2>\n'
            if totals["pass"]:  # passed:
                outstr += '<h2><div class="report pass"> Pass:' + str(totals["pass"]) + '</div></h2>\n'
                
            outstr += '</div>\n'
            if p.data:
                outstr += self._yaml2html(p.data)

            outstr += overview
            outstr += '<details><summary>\n'\
                      + '</summary>\n' + body + '</details>\n'

        outstr += '<hr>'
        outstr += footer

        return outstr

    def open(self, fname):
        # check to see if it exists.
        if not os.path.exists(fname):
            logging.error(" filname '%s' does not exist." % fname)
            return

        # use the walk function for any directories
        if os.path.isdir(fname):
            self.walk(fname)
            return  # note: self.walk() calls open() recursively here.

        # now we are ready to open the file and add it to the list.
        p = Plan()
        p.open(fname)
        self.plans.append(p)

    def walk(self, fname, ext=".tap"):
        tree = []
        for root, dirs, files in os.walk(fname):
            for f in files:
                if is_tap(os.path.join(root, f), ext):
                    tree.append(os.path.join(root, f))

        # sort the plans
        for f in sorted(tree):
            self.open(f)

    def set_accessible(self, acc):
        self.accessible = acc


# FIXME: possible to generalise to work for tests and tap files...
def find_tap_files(inf=".", ext=".tap"):
    if not os.path.exists(inf):
        logging.error(" (find_tap_files): input '%s' does not exist." % inf)
        return []
    if os.path.isfile(inf):
        return [is_tap(inf)]
    elif os.path.isdir(inf):
        # walk the dir tree...
        tree = []
        for root, dirs, files in os.walk(inf):
            for f in files:
                if is_tap(os.path.join(root, f), ext):
                    tree.append(os.path.join(root, f))
        return tree


def main():
    import argparse
    import sys
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]))
    parser.add_argument("infiles", type=str, nargs='+',
                        help="input files or directories")

    parser.add_argument("-o", "--outfile", default="index.html",
                        help="output file [optional: default=%(default)s]")

    parser.add_argument("-O", "--outdir", default=".",
                        help="output directory [optional: default=%(default)s]")

    parser.add_argument("-R", "--raw", action="store_true", default=False, 
                        help="process the taw TAP files: default=%(default)s]")
        
    parser.add_argument("-v", "--verbose", action="store_true", default=False, 
                        help="produce diagnostic output [optional: default=%(default)s]")
    parser.add_argument("-d", "--debug", action="store_true", default=False, 
                        help="produce diagnostic output [optional: default=%(default)s]")    
    parser.add_argument("-a", "--accessible", action="store_true", default=False, 
                        help="produce color blind friendly colors in VKDashboard [optional: default=%(default)s]")

    args = parser.parse_args()
    if args.verbose is not False:
        logging.basicConfig(level=logging.INFO)
    if args.debug is not False:
        logging.basicConfig(level=logging.DEBUG)

    outfile = os.path.join(args.outdir, args.outfile)

    accessible = args.accessible

    logging.info(" input = '%s'" % args.infiles)
    logging.info(" outfile = '%s'" % outfile)
    logging.info(" accessible = '%s'" % accessible)
    logging.info(" ")

    dash = Dashboard()
    dash.set_accessible(args.accessible)

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
            
    for f in tapfiles:
        dash.open(f)

    if outfile is not None:
        fout = open(outfile, 'w')
        fout.write(str(dash))
        fout.close()

from vkdash.header import *
from vkdash.tap import *
from vkdash.tap import is_tap
import simplejson as json
import yaml, yamlordereddictloader

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
        import yaml, yamlordereddictloader

        if not data:
            return ""
        
        htmlstr  = '\t\t<details>\n'
        htmlstr += '\t\t<summary> YAML </summary>\n'
        htmlstr += "<pre>\n"
        htmlstr += yaml.dump(data, Dumper=yamlordereddictloader.Dumper,
                             default_flow_style=False, indent=4)
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
            if itm.is_todo():
                return ' <div class="report todo"> '
            elif itm.is_skip():
                return ' <div class="report skip"> '
            elif itm.is_diagnostic():
                return ' <div class="result diagnostic"></div> '
            elif itm.failed():
                return ' <div class="report fail"> '
            elif itm.passed():
                return ' <div class="report pass"> '
            return ""
        
        ordered_tests = ""

        ordered_tests += '<table style="width:100%">'
        ordered_tests += '<tr>'
        ordered_tests += '<th>Pass</th>'
        ordered_tests += '<th>Test #</th>'
        ordered_tests += '<th>Description</th>'
        ordered_tests += '<th>Directive</th>'
        ordered_tests += '<th>Metadata</th>'
        ordered_tests += '</tr>'

        for i in plan.tests: 
            test_number += 1
            if i.is_diagnostic():
                this_test  = '<tr>'
                this_test += '<td>'+_color_it(i)+' </div></td>'
                this_test += '<td></td>'
                this_test += '<td> # '+ str(i.description) +'</td>'
                this_test += '<td>'+ i.directive +'</td>'
                this_test += '<td>'+ self._yaml2html(i.data) +'</td>'
                this_test += '</tr>'

                ordered_tests += this_test

            elif i.passed():
                this_test  = '<tr>'
                this_test += '<td>'+_color_it(i)+' ok </div></td>'
                this_test += '<td>'+ str(i.number) +'</td>'
                this_test += '<td>'+ i.description +'</td>'
                this_test += '<td>'+ i.directive +'</td>'
                this_test += '<td>'+ self._yaml2html(i.data) +'</td>'
                this_test += '</tr>'

                passed += 1

                ordered_tests += this_test

                overview_passed += '<a href="#' + str(test_number) + '"><div class="view pass"' + ' ' + 'title="' \
                                   + i.description + '"></div></a>\n\t'
            elif i.failed():
                this_test  = '<tr>'
                this_test += '<td>'+_color_it(i)+' not ok </div></td>'
                this_test += '<td>'+ str(i.number) +'</td>'
                this_test += '<td>'+ i.description +'</td>'
                this_test += '<td>'+ i.directive +'</td>'
                this_test += '<td>'+ self._yaml2html(i.data) +'</td>'
                this_test += '</tr>'

                failed += 1

                ordered_tests += this_test

                overview_failed += '<a href="#' + str(test_number) + '"><div class="view fail"' + ' ' + 'title="' \
                                   + i.description + '"></div></a>\n\t'
            elif i.is_skip():
                this_test  = '<tr>'
                this_test += '<td>'+_color_it(i)+' ok </div></td>'
                this_test += '<td>'+ str(i.number) +'</td>'
                this_test += '<td>'+ i.description +'</td>'
                this_test += '<td> SKIP'+ i.directive +'</td>'
                this_test += '<td>'+ self._yaml2html(i.data) +'</td>'
                this_test += '</tr>'

                skipped += 1
                
                ordered_tests += this_test

                overview_skipped += '<a href="#' + str(test_number) + '"><div class="view skip"' + ' ' + 'title="' \
                                    + i.description + '"></div></a>\n\t'
            elif i.is_todo():
                this_test  = '<tr>'
                this_test += '<td>'+_color_it(i)+' not ok </div></td>'
                this_test += '<td>'+ str(i.number) +'</td>'
                this_test += '<td>'+ i.description +'</td>'
                this_test += '<td> # TODO '+ i.directive +'</td>'
                this_test += '<td>'+ self._yaml2html(i.data) +'</td>'
                this_test += '</tr>'

                todos += 1

                ordered_tests += this_test

                overview_todo += '<a href="#' + str(test_number) + '"><div class="view todo"' + ' ' + 'title="' \
                                 + i.description + '"></div></a>\n\t'

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
        .diagnostic{background-color: '+VK_DIAG+';}\n\
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
    import os, sys, logging
    parser = argparse.ArgumentParser(prog=os.path.basename(os.path.basename(sys.argv[0])))  # TODO pep complains about line length. is the double basename function necessary?
    parser.add_argument("infiles", type=str, nargs='+',
                        help="input files or directories")

    parser.add_argument("-o", "--outfile", default="index.html",
                        help="output file [optional: default=%(default)s]")

    parser.add_argument("-O", "--outdir", default=".",
                        help="output directory [optional: default=%(default)s]")

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
    
    for f in args.infiles:
        dash.open(f)

    if outfile is not None:
        fout = open(outfile, 'w')
        fout.write(str(dash))
        fout.close()

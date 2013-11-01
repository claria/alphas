#!/usr/bin/env python2

import sys
import argparse
import logging

#import numpy
from src.alphas import perform_chi2test, plot, batch_processing

logger = logging.getLogger('root')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def main():
    # Parse args
    logger.info('Parsing command line args')

    #Parent
    parent_parser = argparse.ArgumentParser(add_help=False, prog='PROG')
    parent_parser.add_argument('-a', '--analysis', help='analysis name')
    parent_parser.add_argument('-p', '--pdf_family', help='PDF family', default=None)
    parent_parser.add_argument('--pdf_sets', type=str, nargs='+', default=[],
                               help='PDF Sets')
    #Fitting
    parser = argparse.ArgumentParser(add_help=False, prog='PROG')
    subparsers = parser.add_subparsers()
    parser_fit = subparsers.add_parser('fit', help='Do the Fit',
                                       parents=[parent_parser])
    parser_fit.add_argument('-u', '--pdf_unc_source', help='PDF Unc Source')
    parser_fit.add_argument('-s', '--scenario', default='all',
                            help='PDF Unc Source')
    parser_fit.set_defaults(func=perform_chi2test)

    #Plotting
    parser_plot = subparsers.add_parser('plot', help='Do the plotting',
                                        parents=[parent_parser])
    parser_plot.add_argument('plot',
                             type=str,
                             choices=['ratio', 'asratio', 'chi2'],
                             help='Types of plots')

    parser_plot.add_argument('-s', '--scenario', default='all',
                             help='PDF Unc Source')

    parser_plot.set_defaults(func=plot)

    parser_batch = subparsers.add_parser('batch', help='Do Batch processing',
                                         parents=[parent_parser])
    parser_batch.set_defaults(func=batch_processing)

    kwargs = vars(parser.parse_args())
    print kwargs
    kwargs['func'](**kwargs)


if __name__ == '__main__':
    sys.exit(main())

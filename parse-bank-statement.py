#!/usr/bin/python3

# SPDX-FileCopyrightText: 2019 Felix Gruber <felgru@posteo.net>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import os
import sys

from parsers.banks import parsers

aparser = argparse.ArgumentParser(
        description='parse a bank statement into hledger format')
aparser.add_argument('-o', metavar='OUTFILE', dest='outfile', default=None,
                     help='write to OUTFILE instead of stdout')
aparser.add_argument('--raw', dest='raw', default=False,
                     action='store_true',
                     help='write raw parsing results (useful when creating filters)')
aparser.add_argument('--meta', dest='meta', default=False,
                     action='store_true',
                     help='parse only metadata')
aparser.add_argument('--json', dest='json', default=False,
                     action='store_true',
                     help='when coupled with meta, write output as JSON dict')
aparser.add_argument('bank', action='store',
                     help='bank to parse from ({})'.format(', '.join(sorted(parsers))))
aparser.add_argument('infile', action='store',
                     help='the account statement file downloaded from your bank'
                          ' (probably a pdf or csv file)')

args = aparser.parse_args()

def open_outfile():
    if args.outfile is None:
        outfile = sys.stdout
    else:
        outfile = open(args.outfile, 'w')
    return outfile

try:
    bank_parsers = parsers[args.bank]
except KeyError:
    print(f'Unknown bank: {args.bank}', file=sys.stderr)
    exit(1)

try:
    extension = os.path.splitext(args.infile)[1].lower()
    Parser = bank_parsers[extension]
except KeyError:
    print(f"Don't know how to parse file of type {extension}", file=sys.stderr)
    exit(1)

transactions_parser = Parser(args.infile)
if args.meta:
    try:
        metadata = transactions_parser.parse_metadata()
    except NotImplementedError as e:
        print(f'Warning: couldn\'t parse {args.infile}:', e.args,
              file=sys.stderr)
        exit(0)
    if args.json:
        metadata.write_json(open_outfile())
    else:
        metadata.write(open_outfile())
else:
    try:
        bank_statement = transactions_parser.parse()
    except NotImplementedError as e:
        print(f'Warning: couldn\'t parse {args.infile}:', e.args,
              file=sys.stderr)
        exit(0)
    if not args.raw:
        bank_statement.write_ledger(open_outfile())
    else:
        bank_statement.write_raw(open_outfile())

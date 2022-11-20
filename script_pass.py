#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import base64
import csv
import sys
import subprocess
import pandas as pd

PASS_PROG = 'pass'
DEFAULT_USERNAME = 'login'


def main():
    """\
    Import password(s) exported by Password Exporter for chrome in csv
    format to pass format.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filepath", type=str,
        help="The password Exporter generated file")
    parser.add_argument(
        "-p", "--prefix", type=str,
        help="Prefix for pass store path, you may want to use: sites")
    args = parser.parse_args()

    passimport(args.filepath, prefix=args.prefix, force=args.force,
               verbose=args.verbose, quiet=args.quiet)


def passimport(filepath, prefix=None, force=False, verbose=False, quiet=False):
    df = pd.read_csv(filepath)
    for row in df.to_dict('records'):
        username = row['username']
        password = row['password']
        name = row['name']
        url = row['url']

        # Remove the protocol prefix for http(s)
        if name == '':
            name = url.replace(
            'https://', '').replace('http://', '')

        text = '{}\n'.format(password)
        if username:
            text += '{}: {}\n'.format(
                row.get('usernameField', DEFAULT_USERNAME), username)
        if name:
            text += 'Hostname: {}\n'.format(name)
        if url:
            text += 'httpRealm: {}\n'.format(url)

        # Rough protection for fancy username like “; rm -Rf /\n”
        storepath = prefix + "/" + str(name) + "/" + str(username)
        cmd = [PASS_PROG, 'insert', '--multiline']
        cmd.append(storepath)
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate(input=str.encode(text))
        retcode = proc.wait()
        print("okay ---  " + prefix + "/" + str(name) + "/" + str(username))
if __name__ == '__main__':
    main()

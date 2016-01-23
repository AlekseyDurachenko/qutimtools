#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright 2016, Durachenko Aleksey V. <durachenko.aleksey@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import json
import argparse


def version():
    return 'v0.1.0'


def description():
    return 'Merging the qutIM message history. Please close '   \
           'the qutIM before use this script.'


def create_parser():
    parser = argparse.ArgumentParser(description=description())
    parser.add_argument('--version', action='version',
                        version="%(prog)s " + version())
    parser.add_argument('--verbose', action='store_true',
                        help='print various debugging information')
    parser.add_argument('--src', action='store', required=True,
                        help='the source qutIM directory')
    parser.add_argument('--dst', action='store', required=True,
                        help='the destination qutIM directory.')
    return parser.parse_args()


def get_icq_accounts(src_dir):
    return [uin
            for uin in os.listdir(src_dir)
            if os.path.isdir(os.path.join(src_dir, uin)) and
            uin.startswith("icq")]


def get_jabber_accounts(src_dir):
    return [jid
            for jid in os.listdir(src_dir)
            if os.path.isdir(os.path.join(src_dir, jid)) and
            jid.startswith("jabber")]


def get_json_files(dir):
    return [name
            for name in os.listdir(dir)
            if os.path.isfile(os.path.join(dir, name)) and
            name.endswith(".json")]


def load_json_file(filename):
    with open(filename) as data_file:
        return json.load(data_file)


def write_json_file(filename, data):
    with open(filename, 'w', encoding='utf8') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=1, ensure_ascii=False)


def main():
    parser = create_parser()

    src_dir = parser.src
    dst_dir = parser.dst
    verbose = parser.verbose

    print("Summary:")
    print("|  Input Directory:", src_dir)
    print("| Output Directory:", dst_dir)

    accounts = []
    accounts.extend(get_icq_accounts(os.path.join(src_dir, "history")))
    accounts.extend(get_jabber_accounts(os.path.join(src_dir, "history")))

    for account in accounts:
        src_prefix = os.path.join(src_dir, "history", account)
        dst_prefix = os.path.join(dst_dir, "history", account)
        os.makedirs(dst_prefix, exist_ok=True)
        json_files = get_json_files(src_prefix)
        for json_file in json_files:
            src_json_file = os.path.join(src_prefix, json_file)
            dst_json_file = os.path.join(dst_prefix, json_file)
            if os.path.exists(dst_json_file):
                if verbose:
                    print("MERGE:", src_json_file, "<>", dst_json_file)

                messages = []
                messages.extend(load_json_file(dst_json_file))
                for item in load_json_file(src_json_file):
                    if not item in messages:
                        messages.append(item)

                messages.sort(key=lambda x: x['datetime'])

                write_json_file(dst_json_file, messages)
            else:
                if verbose:
                    print("COPY:", src_json_file, ">>", dst_json_file)
                data = load_json_file(src_json_file)
                write_json_file(dst_json_file, data)


if __name__ == "__main__":
    main()

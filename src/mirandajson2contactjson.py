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
import datetime
import argparse
from unittest import result


def version():
    return 'v0.1.0'


def description():
    return 'This utility convert the miranda json message history to the '  \
           'contact json'


def create_parser():
    parser = argparse.ArgumentParser(description=description())
    parser.add_argument('--version', action='version',
                        version="%(prog)s " + version())
    parser.add_argument('--src', action='store', required=True,
                        help='the input miranda json message history file')
    parser.add_argument('--dst', action='store', required=True,
                        help='the output contact json file')
    return parser.parse_args()


def save_json_file(filename, h):
    f = open(filename, 'w', encoding='utf8')
    f.write(json.dumps(h, sort_keys=True, indent=1, ensure_ascii=False))
    f.close()


def load_json_file(filename):
    with open(filename) as data_file:
        return json.load(data_file)


def main():
    parser = create_parser()

    src_file = parser.src
    dst_file = parser.dst

    print("Summary:")
    print("|  Input Miranda Json File:", src_file)
    print("| Output Contact Json File:", dst_file)

    in_data = load_json_file(src_file)
    out_data = dict()
    out_data["accounts"] = in_data["accounts"]
    out_data["contacts"] = in_data["contacts"]
    save_json_file(dst_file, out_data)


if __name__ == "__main__":
    main()

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
import re
from xml.dom import minidom
import argparse


def version():
    return 'v0.1.0'


def description():
    return 'This utility convert the miranda xml message history to the '   \
           'qutIM message history. Please, do not use '                     \
           'the qutIM working copy as the output directory. '               \
           'It may damage the your message history. Just select '           \
           'an empty directory as the output directory.'


def create_parser():
    parser = argparse.ArgumentParser(description=description())
    parser.add_argument('--version', action='version',
                        version="%(prog)s " + version())
    parser.add_argument('--verbose', action='store_true',
                        help='print various debugging information')
    parser.add_argument('--uin', action='store', default=None,
                        help='set your UIN to convert '
                             'the ICQ message history')
    parser.add_argument('--src', action='store', required=True,
                        help='the input directory with '
                             'the miranda xml message history')
    parser.add_argument('--dst', action='store', required=True,
                        help='the output directory. '
                             'WARNING: do not use the qutIM working copy '
                             'as the output directory. It may damage the '
                             'your message history. '
                             'Just select an empty directory')
    return parser.parse_args()


def get_icq_contacts(src_dir):
    # filename format: "Full History [XXX] - [0987654321].xml"
    return [[uin, re.findall("- \[(.*)\]$", uin[:-4])[-1]]
            for uin in os.listdir(src_dir)
            if os.path.isfile(os.path.join(src_dir, uin)) and
            uin[-4:].lower() == ".xml" and
            re.findall("- \[(.*)\]$", uin[:-4])[-1].isnumeric()]


def create_message_object(msg_is_incoming, msg_date, msg_time, msg_text):
    return {
        "in": msg_is_incoming,
        "datetime": msg_date + "T" + msg_time,
        "text": msg_text.rstrip()
    }


def node_to_text(node, name):
    if len(node.getElementsByTagName(name)) == 0:
        return None
    x = node.getElementsByTagName(name)[0].firstChild
    if x is None:
        return None
    return x.nodeValue


def file_to_messages(filename, uin, verbose=False):
    objects = []
    xmldoc = minidom.parse(filename)
    for imhistory in xmldoc.getElementsByTagName('IMHISTORY'):
        for event in imhistory.getElementsByTagName('EVENT'):
            date = node_to_text(event, "DATE")
            time = node_to_text(event, "TIME")
            id = node_to_text(event, "ID")
            type = node_to_text(event, "TYPE")
            msg = node_to_text(event, "MESSAGE")

            if date is None or time is None or id is None or msg is None:
                if verbose:
                    print("SKIP:", date, time, id, type, msg)
                continue

            objects.append(create_message_object(id != uin, date, time, msg))

    return objects


def save_qutim_icq_history(dst_dir, uin, contact, messages, verbose=False):
    # format:
    #   history/icq.12345678/987654321.201409.json
    if messages is None:
        return

    ym_hash = {}
    for message in messages:
        key = message['datetime'][0:4] + message['datetime'][5:7]
        if key not in ym_hash:
            ym_hash[key] = []
        ym_hash[key].append(message)

    path = os.path.join(dst_dir, "history", "icq." + uin)
    os.makedirs(path, exist_ok=True)

    for key in ym_hash:
        filename = os.path.join(path, contact + "." + key + ".json")
        f = open(filename, 'w', encoding='utf8')
        f.write(json.dumps(ym_hash[key],
                           sort_keys=True, indent=1, ensure_ascii=False))
        f.close()


def main():
    parser = create_parser()

    uin = parser.uin
    src_dir = parser.src
    dst_dir = parser.dst
    verbose = parser.verbose

    print("Summary:")
    print("|              UIN:", uin)
    print("|  Input Directory:", src_dir)
    print("| Output Directory:", dst_dir)

    if uin is not None:
        for filename, contact in get_icq_contacts(src_dir):
            src_filename = os.path.join(src_dir, filename)
            if verbose:
                print("FILENAME:", src_filename)

            save_qutim_icq_history(
                   dst_dir,
                   uin,
                   contact,
                   file_to_messages(src_filename, uin, verbose),
                   verbose)


if __name__ == "__main__":
    main()

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
import datetime
import argparse


def version():
    return 'v0.1.0'


def description():
    return 'This utility convert the QIP message history to the '       \
           'qutIM message history. Please, do not use '                 \
           'the qutIM working copy as the output directory. '           \
           'It may damage the your message history. Just select '       \
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
                             'the QIP message history')
    parser.add_argument('--dst', action='store', required=True,
                        help='the output directory. '
                             'WARNING: do not use the qutIM working copy '
                             'as the output directory. It may damage the '
                             'your message history. '
                             'Just select an empty directory')
    return parser.parse_args()


def get_icq_contacts(src_dir, my_uin):
    path = os.path.join(src_dir, my_uin)
    return [uin[:-4]
            for uin in os.listdir(path)
            if os.path.isfile(os.path.join(path, uin)) and
            uin[-4:].lower() == ".txt" and
            uin[:-4].isnumeric()]


def get_datetime_from_header(str):
    # format: UserName (21:57:03 10/12/2006)
    dt = re.findall("\((.*)\)", str)
    return datetime.datetime.strptime(dt[-1], "%H:%M:%S %d/%m/%Y")


def create_message_object(message_incoming, message_header, message_lines):
    msg_is_incoming = message_incoming
    msg_time = get_datetime_from_header(message_header)
    msg_text = "\n".join(message_lines)

    return {
        "in": msg_is_incoming,
        "datetime": msg_time.strftime('%Y-%m-%dT%H:%M:%S'),
        "text": msg_text.rstrip()
    }


def file_to_messages(filename, verbose=False):
    objects = []

    message_header = ""
    message_lines = []
    message_incoming = False

    for line in open(filename, 'r').readlines():
        line = line.rstrip()
        if line == "--------------------------------------<-":
            if message_header != "" and len(message_lines) > 0:
                objects.append(create_message_object(message_incoming,
                                                     message_header,
                                                     message_lines))
            message_incoming = True
            message_header = ""
            message_lines = []
            continue
        if line == "-------------------------------------->-":
            if message_header != "" and len(message_lines) > 0:
                objects.append(create_message_object(message_incoming,
                                                     message_header,
                                                     message_lines))
            message_incoming = False
            message_header = ""
            message_lines = []
            continue

        if message_header == "":
            message_header = line
            continue

        message_lines.append(line)

    if message_header != "" and len(message_lines) > 0:
        objects.append(create_message_object(message_incoming,
                                             message_header,
                                             message_lines))

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
        for contact in get_icq_contacts(src_dir, uin):
            src_filename = os.path.join(src_dir, uin, contact + ".txt")
            save_qutim_icq_history(
                   dst_dir,
                   uin,
                   contact,
                   file_to_messages(src_filename, verbose),
                   verbose)


if __name__ == "__main__":
    main()

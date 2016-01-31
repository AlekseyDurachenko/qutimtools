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
import sqlite3


def version():
    return 'v0.1.0'


def description():
    return 'This utility convert the skype database to the ' \
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
    parser.add_argument('--id', action='store', default=None,
                        help='your skype id')
    parser.add_argument('--src', action='store', required=True,
                        help='the input skype database')
    parser.add_argument('--dst', action='store', required=True,
                        help='the output directory. '
                             'WARNING: do not use the qutIM working copy '
                             'as the output directory. It may damage the '
                             'your message history. '
                             'Just select an empty directory')
    return parser.parse_args()


# def get_icq_contacts(src_dir):
#     return [uin
#             for uin in os.listdir(src_dir)
#             if os.path.isdir(os.path.join(src_dir, uin)) and
#             uin.isnumeric()]
#
#
# def get_jabber_contacts(src_dir):
#     return [jid[1:]
#             for jid in os.listdir(src_dir)
#             if os.path.isdir(os.path.join(src_dir, jid)) and
#             jid[0] == 'j']
#
#
# def file_to_messages(filename, verbose=False):
#     objects = []
#     for message in open(filename, 'r').read().split('\x0C'):
#         parts = [s.strip() for s in message.strip().split('\n', maxsplit=4)]
#         if len(parts) != 5 or parts[1].upper() != 'MSG':
#             if verbose:
#                 print('MESSAGE SKIPPED:', parts)
#             continue
#
#         msg_is_incoming = (parts[0].upper() == "IN")
#         msg_time = datetime.datetime.fromtimestamp(int(parts[3]))
#         msg_text = parts[4]
#
#         objects.append({
#             "in": msg_is_incoming,
#             "datetime": msg_time.strftime('%Y-%m-%dT%H:%M:%S'),
#             "text": msg_text
#         })
#
#     return objects
#
#
# def get_contact_messages(src_dir, contact, account_type, verbose=False):
#     if account_type.upper() == "ICQ":
#         path = os.path.join(src_dir, contact)
#     elif account_type.upper() == "JABBER":
#         path = os.path.join(src_dir, 'j' + contact)
#     else:
#         raise ValueError("account type is not in ['ICQ', 'JABBER']")
#
#     history_files = [os.path.join(path, f)
#                      for f in ['history', '_history', 'history_']
#                      if os.path.exists(os.path.join(path, f))]
#
#     messages = []
#     for filename in history_files:
#         messages.extend(file_to_messages(filename, verbose))
#
#     if len(messages) == 0:
#         return None
#     else:
#         messages.sort(key=lambda x: x['datetime'])
#         return messages

def get_messages(messages, contact, verbose=False):
    objects = []
    for message in messages:
        if message['contact'] != contact:
            continue

        objects.append({
            "in": message['incomming'],
            "datetime": message['timestamp'].strftime('%Y-%m-%dT%H:%M:%S'),
            "text": message['text']
        })

    objects.sort(key=lambda x: x['datetime'])

    return objects


def read_database(filename, sid, verbose=False):
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()
    contacts = set()
    messages = []
    for row in cursor.execute("SELECT chatname, author, timestamp, body_xml, id FROM messages"):
        if row[0] is None:
            if verbose:
                print("SKIP:", row[4])
            continue
        [n1, n2] = row[0].split(";")[0].split("/")
        n1 = n1[1:]
        n2 = n2[1:]
        contact = n1
        if contact == sid:
            contact = n2

        key_value = dict()
        key_value['contact'] = contact
        key_value['incomming'] = (row[1] != sid)
        key_value['timestamp'] = datetime.datetime.fromtimestamp(int(row[2]))
        if row[3]:
            key_value['text'] = row[3]
        else:
            key_value['text'] = ""
        contacts.add(contact)
        messages.append(key_value)

    return contacts, messages


def jid_escaped(jid):
    return jid.replace("@", "%0040").replace("_", "%005f").replace("-", "%002d")


def save_qutim_skype_history(dst_dir, sid, contact, messages, verbose=False):
    # format:
    #   history/skype.account/user.201409.json
    if messages is None:
        return

    ym_hash = {}
    for message in messages:
        key = message['datetime'][0:4] + message['datetime'][5:7]
        if key not in ym_hash:
            ym_hash[key] = []
        ym_hash[key].append(message)

    path = os.path.join(dst_dir, "history", "skype." + jid_escaped(sid))
    os.makedirs(path, exist_ok=True)

    for key in ym_hash:
        filename = os.path.join(path, jid_escaped(contact) + "." + key + ".json")
        f = open(filename, 'w', encoding='utf8')
        f.write(json.dumps(ym_hash[key],
                           sort_keys=True, indent=1, ensure_ascii=False))
        f.close()


def main():
    parser = create_parser()

    sid = parser.id
    src_sdb = parser.src
    dst_dir = parser.dst
    verbose = parser.verbose

    print("Summary:")
    print("|              SKYPE ID:", sid)
    print("|  Input Skype Database:", src_sdb)
    print("|      Output Directory:", dst_dir)
    print("|               Verbose:", verbose)

    contacts, messages = read_database(src_sdb, sid, verbose)
    if verbose:
        print("CONTACTS:", contacts)

    if sid is not None:
        for contact in contacts:
            save_qutim_skype_history(
                    dst_dir,
                    sid,
                    contact,
                    get_messages(messages, contact, verbose),
                    verbose)


if __name__ == "__main__":
    main()

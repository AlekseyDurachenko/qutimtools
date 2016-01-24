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


def version():
    return 'v0.1.0'


def description():
    return 'This utility convert the CenterICQ message history to the ' \
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
    parser.add_argument('--jid', action='store', default=None,
                        help='set your JID to convert '
                             'the JABBER message history')
    parser.add_argument('--src', action='store', required=True,
                        help='the input directory with '
                             'the CenterICQ message history')
    parser.add_argument('--dst', action='store', required=True,
                        help='the output directory. '
                             'WARNING: do not use the qutIM working copy '
                             'as the output directory. It may damage the '
                             'your message history. '
                             'Just select an empty directory')
    return parser.parse_args()


def get_icq_contacts(src_dir):
    return [uin
            for uin in os.listdir(src_dir)
            if os.path.isdir(os.path.join(src_dir, uin)) and
            uin.isnumeric()]


def get_jabber_contacts(src_dir):
    return [jid[1:]
            for jid in os.listdir(src_dir)
            if os.path.isdir(os.path.join(src_dir, jid)) and
            jid[0] == 'j']


def file_to_messages(filename, verbose=False):
    objects = []
    for message in open(filename, 'r').read().split('\x0C'):
        parts = [s.strip() for s in message.strip().split('\n', maxsplit=4)]
        if len(parts) != 5 or parts[1].upper() != 'MSG':
            if verbose:
                print('MESSAGE SKIPPED:', parts)
            continue

        msg_is_incoming = (parts[0].upper() == "IN")
        msg_time = datetime.datetime.fromtimestamp(int(parts[3]))
        msg_text = parts[4]

        objects.append({
            "in": msg_is_incoming,
            "datetime": msg_time.strftime('%Y-%m-%dT%H:%M:%S'),
            "text": msg_text
        })

    return objects


def get_contact_messages(src_dir, contact, account_type, verbose=False):
    if account_type.upper() == "ICQ":
        path = os.path.join(src_dir, contact)
    elif account_type.upper() == "JABBER":
        path = os.path.join(src_dir, 'j' + contact)
    else:
        raise ValueError("account type is not in ['ICQ', 'JABBER']")

    history_files = [os.path.join(path, f)
                     for f in ['history', '_history', 'history_']
                     if os.path.exists(os.path.join(path, f))]

    messages = []
    for filename in history_files:
        messages.extend(file_to_messages(filename, verbose))

    if len(messages) == 0:
        return None
    else:
        messages.sort(key=lambda x: x['datetime'])
        return messages


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


def jid_escaped(jid):
    return jid.replace("@", "%0040").replace("_", "%005f")


def save_qutim_jabber_history(dst_dir, jid, contact, messages, verbose=False):
    # format:
    #   history/jabber.user%0040jabber.org/user2%0040jabber.org.201409.json
    if messages is None:
        return

    ym_hash = {}
    for message in messages:
        key = message['datetime'][0:4] + message['datetime'][5:7]
        if key not in ym_hash:
            ym_hash[key] = []
        ym_hash[key].append(message)

    path = os.path.join(dst_dir, "history", "jabber." + jid_escaped(jid))
    os.makedirs(path, exist_ok=True)

    for key in ym_hash:
        filename = os.path.join(path, jid_escaped(contact) + "." + key + ".json")
        f = open(filename, 'w', encoding='utf8')
        f.write(json.dumps(ym_hash[key],
                           sort_keys=True, indent=1, ensure_ascii=False))
        f.close()


def main():
    parser = create_parser()

    uin = parser.uin
    jid = parser.jid
    src_dir = parser.src
    dst_dir = parser.dst
    verbose = parser.verbose

    print("Summary:")
    print("|              UIN:", uin)
    print("|              JID:", jid)
    print("|  Input Directory:", src_dir)
    print("| Output Directory:", dst_dir)

    if uin is not None:
        for contact in get_icq_contacts(src_dir):
            save_qutim_icq_history(
                    dst_dir,
                    uin,
                    contact,
                    get_contact_messages(src_dir, contact, "ICQ", verbose),
                    verbose)

    if jid is not None:
        for contact in get_jabber_contacts(src_dir):
            save_qutim_jabber_history(
                    dst_dir,
                    jid,
                    contact,
                    get_contact_messages(src_dir, contact, "JABBER", verbose),
                    verbose)


if __name__ == "__main__":
    main()

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
import csv
from xml.dom import minidom


def version():
    return 'v0.1.0'


def description():
    return 'This utility convert sms xml file to the ' \
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
    parser.add_argument('--phone', action='store', default=None,
                        help='your phone')
    parser.add_argument('--src', action='store', required=True,
                        help='sms xml file')
    parser.add_argument('--dst', action='store', required=True,
                        help='the output directory. '
                             'WARNING: do not use the qutIM working copy '
                             'as the output directory. It may damage the '
                             'your message history. '
                             'Just select an empty directory')
    return parser.parse_args()


def get_messages(messages, contact, verbose=False):
    objects = []
    for message in messages:
        objects.append({
            "in": message['incomming'],
            "datetime": message['datetime'].strftime('%Y-%m-%dT%H:%M:%S'),
            "text": message['text']
        })

    objects.sort(key=lambda x: x['datetime'])

    return objects


def jid_escaped(jid):
    return jid.replace("@", "%0040").replace("_", "%005f").replace("-", "%002d")


def save_qutim_sms_history(dst_dir, phone, contact, messages, verbose=False):
    # format:
    #   history/sms.phone/user.201409.json
    if messages is None:
        return

    ym_hash = {}
    for message in messages:
        key = message['datetime'][0:4] + message['datetime'][5:7]
        if key not in ym_hash:
            ym_hash[key] = []
        ym_hash[key].append(message)

    path = os.path.join(dst_dir, "history", "sms." + jid_escaped(phone))
    os.makedirs(path, exist_ok=True)

    for key in ym_hash:
        filename = os.path.join(path, jid_escaped(contact) + "." + key + ".json")
        f = open(filename, 'w', encoding='utf8')
        f.write(json.dumps(ym_hash[key],
                           sort_keys=True, indent=1, ensure_ascii=False))
        f.close()


def read_sms_file_1(filename):
    records = []
    for line in open(filename, 'r').readlines():
        parts = line.split(";")
        date = parts[0].replace(".04 ", ".2004 ").replace(".05 ", ".2005 ").replace(".06 ", ".2006 ").replace(".07 ", ".2007 ").replace(".08 ", ".2008 ").replace(".09 ", ".2009 ")
        try:
            date = datetime.datetime.strptime(date, "%d.%m.%Y %H:%M:%S")
        except:
            date = datetime.datetime(2000, 1, 1)
        phone = parts[1].replace("'", "").replace("+", "")
        name = parts[2]
        msg = parts[3]
        records.append({
            "datetime": date,
            "phone": phone.strip(),
            "name": name.strip(),
            "text": msg.strip(),
            "incomming": True
        })
    return records


def split_name_phone(data):
    for i in range(0, len(data)):
        pos = len(data) - i - 1
        if data[pos] == "[":
            return data[pos+1:len(data)-1].strip().replace("+", "").replace(" ", "").replace(">", "").replace("<", ""), data[0:pos].strip()
    return None, None


def read_sms_file_2(filename):
    records = []
    csvfile = open(filename, 'r', encoding="utf-8")
    csvreader = csv.reader(csvfile, delimiter=';')
    n = 0
    for row in csvreader:
        n += 1
        contact_from = row[0]
        contact_to = row[1]
        contact_name = row[1]
        text = row[2]
        date = datetime.datetime.strptime(row[3], "%Y.%m.%d") + datetime.timedelta(seconds=n)
        if contact_from:
            incomming = True
            phone, name = split_name_phone(contact_from)
        else:
            incomming = False
            phone, name = split_name_phone(contact_to)

        records.append({
           "datetime": date,
           "phone": phone.strip(),
           "name": name.strip(),
           "text": text.strip(),
           "incomming": incomming
        })
    return records


def node_to_text(node, name):
    if len(node.getElementsByTagName(name)) == 0:
        return None
    x = node.getElementsByTagName(name)[0].firstChild
    if x is None:
        return None
    return x.nodeValue


def read_sms_file_3(filename):
    records = []
    xmldoc = minidom.parse(filename)
    for imhistory in xmldoc.getElementsByTagName('mpe_messages'):
        for event in imhistory.getElementsByTagName('sms'):
            contact_from = node_to_text(event, "from")
            if contact_from is not None:
                contact_from = contact_from.replace("+", "").replace(" ", "").replace(">", "").replace("<", "").strip()
                phone = contact_from
            contact_to = node_to_text(event, "to")
            if contact_to is not None:
                contact_to = contact_to.replace("+", "").replace(" ", "").replace(">", "").replace("<", "").strip()
                phone = contact_to
            date = node_to_text(event, "timestamp")
            body = node_to_text(event, "body")
            if body is not None:
                body = body.strip()
            date = datetime.datetime.strptime(date, "%d.%m.%Y %H:%M:%S")
            incomming = contact_from is not None
            records.append({
                "datetime": date,
                "phone": phone.strip(),
                "name": "",
                "text": body,
                "incomming": incomming
            })

    return records


def read_sms_file_4(filename):
    records = []
    xmldoc = minidom.parse(filename)
    for imhistory in xmldoc.getElementsByTagName('smses'):
        for event in imhistory.getElementsByTagName('sms'):
            phone = event.attributes["address"].value.replace("+", "").replace(" ", "").replace(">", "").replace("<", "").strip()
            date = datetime.datetime.fromtimestamp(int(event.attributes["date"].value)/1000)
            incomming = event.attributes["type"].value == "1"
            text = event.attributes["body"].value.strip()
            records.append({
                "datetime": date,
                "phone": phone,
                "name": "",
                "text": text,
                "incomming": incomming
            })

    return records


def main():
    parser = create_parser()

    phone = parser.phone
    src_file = parser.src
    dst_dir = parser.dst
    verbose = parser.verbose

    print("Summary:")
    print("|         PHONE ID:", phone)
    print("|     SMS XML File:", src_file)
    print("| Output Directory:", dst_dir)
    print("|          Verbose:", verbose)

    records = read_sms_file_4(src_file)
    contacts = list(set([rec["phone"] for rec in records]))
    messages = {}
    for contact in contacts:
        for rec in records:
            if contact == rec["phone"]:
                if contact not in messages:
                    messages[contact] = []
                messages[contact].append(rec)

    if verbose:
        print("CONTACTS:", contacts)

    if phone is not None:
        for contact in contacts:
            save_qutim_sms_history(
                    dst_dir,
                    phone,
                    contact,
                    get_messages(messages[contact], contact, verbose),
                    verbose)

    # save contact_list
    # result = []
    # for contact in contacts:
    #     result.append(messages[contact][0]["phone"] + ";" + messages[contact][0]["name"])
    # open(dst_dir + "/contacts.csv", "w").write("\n".join(result)+"\n")

if __name__ == "__main__":
    main()

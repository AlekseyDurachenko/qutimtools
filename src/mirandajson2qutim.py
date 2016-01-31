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
    parser.add_argument('--json', action='store', required=True,
                        help='the input miranda json message history file')
    parser.add_argument('--dst', action='store', required=True,
                        help='the output directory. '
                             'WARNING: do not use the qutIM working copy '
                             'as the output directory. It may damage the '
                             'your message history. '
                             'Just select an empty directory')
    parser.add_argument('--seq', action='store', required=True,
                        help='the first sequence number for unattached '
                             'message chains')
    return parser.parse_args()


def get_icq_contacts(json_data):
    contacts = []
    for item in json_data["contacts"]:
        if "icq" in item["settings"]:
            contacts.append(item)

    return contacts


def get_jabber_contacts(json_data):
    contacts = []
    for item in json_data["contacts"]:
        if "jabber" in item["settings"]:
            contacts.append(item)

    return contacts


def get_vk_contacts(json_data):
    contacts = []
    for item in json_data["contacts"]:
        if "vk" in item["settings"]:
            contacts.append(item)

    return contacts


def get_contact_ids(json_data):
    ids = []
    for item in json_data["contacts"]:
        ids.append(item["id"])

    return ids


def get_event_ids(json_data):
    ids = []
    for item in json_data["events"]:
        ids.append(item["id"])

    return ids


def get_events_by_id(json_data):
    events = {}
    for item in json_data["events"]:
        events[item["id"]] = item

    return events


def get_icq_events(events):
    result = []
    for item in events:
        if events[item]["module_name"] == "ICQ":
            result.append(events[item])

    return result


def get_jabber_events(events):
    result = []
    for item in events:
        if events[item]["module_name"] == "JABBER":
            result.append(events[item])

    return result


def get_contact_events(contact, events):
    result = []
    result_ids = {}
    id = contact["first_event_id"]
    while True:
        if id in events.keys():
            x = events[id]
            del events[id]
            result.append(x)
            result_ids[id] = 1
            id = x["next_id"]
        else:
            break

    id = contact["first_unread_event_id"]
    while True:
        if id in events.keys():
            x = events[id]
            del events[id]
            result.append(x)
            result_ids[id] = 1
            id = x["next_id"]
        else:
            break

    id = contact["last_event_id"]
    while True:
        if id in events.keys():
            x = events[id]
            del events[id]
            result.append(x)
            result_ids[id] = 1
            id = x["prev_id"]
        else:
            break

    # try to restore
    for key in list(events.keys()):
        # already processed
        if key not in events.keys():
            continue

        if events[key]["prev_id"] == contact["id"]:
            id = key
            while True:
                if id in events.keys():
                    x = events[id]
                    del events[id]
                    result.append(x)
                    result_ids[id] = 1
                    id = x["next_id"]
                else:
                    break
        elif events[key]["next_id"] in result_ids.keys():
            id = key
            while True:
                if id in events.keys():
                    x = events[id]
                    del events[id]
                    result.append(x)
                    result_ids[id] = 1
                    id = x["next_id"]
                else:
                    break
            id = key
            while True:
                if id in events.keys():
                    x = events[id]
                    del events[id]
                    result.append(x)
                    result_ids[id] = 1
                    id = x["prev_id"]
                else:
                    break
        elif events[key]["prev_id"] in result_ids.keys():
            id = key
            while True:
                if id in events.keys():
                    x = events[id]
                    del events[id]
                    result.append(x)
                    result_ids[id] = 1
                    id = x["next_id"]
                else:
                    break
            id = key
            while True:
                if id in events.keys():
                    x = events[id]
                    del events[id]
                    result.append(x)
                    result_ids[id] = 1
                    id = x["prev_id"]
                else:
                    break
    return result


def get_next_lost_chain(events):
    if not events:
        return None

    result = []
    result_ids = {}

    main_key, main_value = events.popitem()
    result.append(main_value)
    result_ids[main_key] = 1

    id = main_value["next_id"]
    while True:
        if id in events.keys():
            x = events[id]
            del events[id]
            result.append(x)
            result_ids[id] = 1
            id = x["next_id"]
        else:
            break

    id = main_value["prev_id"]
    while True:
        if id in events.keys():
            x = events[id]
            del events[id]
            result.append(x)
            result_ids[id] = 1
            id = x["prev_id"]
        else:
            break

    # try to restore
    for key in list(events.keys()):
        # already processed
        if key not in events.keys():
            continue

        if events[key]["next_id"] in result_ids.keys():
            id = key
            while True:
                if id in events.keys():
                    x = events[id]
                    del events[id]
                    result.append(x)
                    result_ids[id] = 1
                    id = x["next_id"]
                else:
                    break
            id = key
            while True:
                if id in events.keys():
                    x = events[id]
                    del events[id]
                    result.append(x)
                    result_ids[id] = 1
                    id = x["prev_id"]
                else:
                    break
        elif events[key]["prev_id"] in result_ids.keys():
            id = key
            while True:
                if id in events.keys():
                    x = events[id]
                    del events[id]
                    result.append(x)
                    result_ids[id] = 1
                    id = x["next_id"]
                else:
                    break
            id = key
            while True:
                if id in events.keys():
                    x = events[id]
                    del events[id]
                    result.append(x)
                    result_ids[id] = 1
                    id = x["prev_id"]
                else:
                    break
    return result


def event_list_to_messages(event_list, verbose=False):
    objects = []
    for event in event_list:
        objects.append({
            "in": event["incomming"],
            "datetime": datetime.datetime.fromtimestamp(event["timestamp"]).strftime('%Y-%m-%dT%H:%M:%S'),
            "text": event["text"]
        })

    objects.sort(key=lambda x: x['datetime'])

    return objects


def jid_escaped(jid):
    return jid.replace("@", "%0040").replace("_", "%005f").replace("-", "%002d")


def save_qutim_other_history(dst_dir, userid, contact, messages, verbose=False):
    # format:
    #   history/other.useremail/987654321.201409.json
    if messages is None:
        return

    ym_hash = {}
    for message in messages:
        key = message['datetime'][0:4] + message['datetime'][5:7]
        if key not in ym_hash:
            ym_hash[key] = []
        ym_hash[key].append(message)

    path = os.path.join(dst_dir, "history", "other." + jid_escaped(userid))
    os.makedirs(path, exist_ok=True)

    for key in ym_hash:
        filename = os.path.join(path, contact + "." + key + ".json")
        f = open(filename, 'w', encoding='utf8')
        f.write(json.dumps(ym_hash[key],
                           sort_keys=True, indent=1, ensure_ascii=False))
        f.close()


def save_qutim_vk_history(dst_dir, userid, contact, messages, verbose=False):
    # format:
    #   history/vk.useremail/987654321.201409.json
    if messages is None:
        return

    ym_hash = {}
    for message in messages:
        key = message['datetime'][0:4] + message['datetime'][5:7]
        if key not in ym_hash:
            ym_hash[key] = []
        ym_hash[key].append(message)

    path = os.path.join(dst_dir, "history", "vk." + jid_escaped(userid))
    os.makedirs(path, exist_ok=True)

    for key in ym_hash:
        filename = os.path.join(path, contact + "." + key + ".json")
        f = open(filename, 'w', encoding='utf8')
        f.write(json.dumps(ym_hash[key],
                           sort_keys=True, indent=1, ensure_ascii=False))
        f.close()


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


def load_json_file(filename):
    with open(filename) as data_file:
        return json.load(data_file)


def main():
    parser = create_parser()

    json_file = parser.json
    dst_dir = parser.dst
    first_seq_number = parser.seq
    verbose = parser.verbose

    json_data = load_json_file(json_file)
    try:
        uin = json_data["accounts"]["icq"]["uin"]
    except:
        uin = None
    try:
        jid = json_data["accounts"]["jabber"]["jid"]
    except:
        jid = None
    try:
        vkid = json_data["accounts"]["vk"]["useremail"]
    except:
        vkid = None

    print("Summary:")
    print("|  Input Miranda Json File:", json_file)
    print("|         Output Directory:", dst_dir)
    print("|                      UIN:", uin)
    print("|                      JID:", jid)
    print("|                       VK:", vkid)
    print("|         First Seq Number:", first_seq_number)

    contact_ids = get_contact_ids(json_data)
    event_ids = get_event_ids(json_data)
    events = get_events_by_id(json_data)

    if vkid is not None:
        for contact in get_vk_contacts(json_data):
            contact_vkid = contact["settings"]["vk"]["id"]
            contact_events = get_contact_events(contact, events)
            print("VK:", contact_vkid, "COUNT:", len(contact_events))
            save_qutim_vk_history(
                    dst_dir,
                    str(vkid),
                    str(contact_vkid),
                    event_list_to_messages(contact_events, verbose),
                    verbose)
        print("ICQ LOST:", len(get_icq_events(events)))

    if uin is not None:
        for contact in get_icq_contacts(json_data):
            contact_uin = contact["settings"]["icq"]["uin"]
            contact_events = get_contact_events(contact, events)
            print("ICQ:", contact_uin, "COUNT:", len(contact_events))
            save_qutim_icq_history(
                    dst_dir,
                    str(uin),
                    str(contact_uin),
                    event_list_to_messages(contact_events, verbose),
                    verbose)
        print("ICQ LOST:", len(get_icq_events(events)))

    if jid is not None:
        for contact in get_jabber_contacts(json_data):
            contact_jid = contact["settings"]["jabber"]["jid"]
            contact_events = get_contact_events(contact, events)
            print("JABBER:", contact_jid, "COUNT:", len(contact_events))
            save_qutim_jabber_history(
                    dst_dir,
                    str(jid),
                    str(contact_jid),
                    event_list_to_messages(contact_events, verbose),
                    verbose)
        print("JABBER LOST:", len(get_jabber_events(events)))

    print("TOTAL LOST:", len(events))

    # extract unattached chains
    seq = int(first_seq_number)
    while True:
        chain = get_next_lost_chain(events)
        if chain is None:
            break
        print("LOST CHAIN", seq, "(", chain[0]["module_name"], ")", ":", len(chain))
        if chain[0]["module_name"] == "IRC":
            continue
        elif chain[0]["module_name"] == "ICQ":
            save_qutim_icq_history(
                    dst_dir,
                    str("unknow"),
                    str(seq),
                    event_list_to_messages(chain, verbose),
                    verbose)
        elif chain[0]["module_name"] == "JABBER":
            save_qutim_jabber_history(
                    dst_dir,
                    str("unknow"),
                    str(seq),
                    event_list_to_messages(chain, verbose),
                    verbose)
        elif chain[0]["module_name"] == "VKontakte":
            save_qutim_jabber_history(
                    dst_dir,
                    str("unknow"),
                    str(seq),
                    event_list_to_messages(chain, verbose),
                    verbose)
        else:
            save_qutim_other_history(
                    dst_dir,
                    str("unknow"),
                    str(seq),
                    event_list_to_messages(chain, verbose),
                    verbose)

        seq += 1


if __name__ == "__main__":
    main()

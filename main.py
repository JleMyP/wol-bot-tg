#!/usr/bin/env python3

import json
import os
import sys

import telebot
from environs import Env
from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from wakeonlan import send_magic_packet

bot = telebot.TeleBot(None)


@bot.message_handler(commands=['hosts', 'start'])
def handle_hosts(message):
    username = message.from_user.username
    if users_whitelist and username not in users_whitelist:
        bot.send_message(message.chat.id, "not allowed")
        print(f"cmd from {username} rejected")
        return

    mu = InlineKeyboardMarkup()
    for host in hosts:
        mu.add(InlineKeyboardButton(host['name'], callback_data=host['name']))
    bot.send_message(message.chat.id, "available hosts", reply_markup=mu)
    print(f"cmd from {username} handled")


@bot.callback_query_handler(func=bool)
def callback_handler(call):
    username = call.from_user.username
    if users_whitelist and username not in users_whitelist:
        bot.answer_callback_query(call.id)
        bot.send_message(message.chat.id, "not allowed")
        print("cb from {username} rejected")
        return

    host = list(filter(lambda h: h['name'] == call.data, hosts))
    if not host:
        bot.answer_callback_query(call.id)
        bot.send_message(message.chat.id, "host not found")
        print(f"host {call.data} not found")
        return

    host = host[0]
    send_magic_packet(host['mac'], ip_address=host.get('ip', '255.255.255.255'),
                      port=host.get('port', 9))
    print(f"wakeup {host['mac']}")
    bot.answer_callback_query(call.id)


if __name__ == '__main__':
    env = Env()
    env.read_env()
    token = env('TG_BOT_TOKEN')
    if not token:
        print("not found env TG_BOT_TOKEN", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists('hosts.json'):
        print("not found file hosts.json", file=sys.stderr)
        sys.exit(1)

    with open('hosts.json') as f:
        hosts = json.load(f)

    users_whitelist = env('TG_USERS_WHITELIST')

    if users_whitelist:
        users_whitelist = users_whitelist.split(';')

    bot.token = token
    print("start polling")
    bot.polling(none_stop=True)

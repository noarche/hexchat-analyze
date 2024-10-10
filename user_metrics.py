# -*- coding: utf-8 -*-
"""
User Metrics Script for HexChat
Tracks message counts, connects, disconnects, status changes, and known aliases from the same host.
"""

import hexchat
import time
from datetime import datetime

__module_name__ = "User Metrics"
__module_version__ = "1.4"
__module_description__ = "Tracks user metrics including message counts, connects, disconnects, status changes, and known aliases."

user_metrics = {}
user_aliases = {}
last_report_time = datetime.now()

def count_messages(word, word_eol, userdata):
    """Count messages for each user."""
    nick = word[0]
    host = word[1]

    if nick not in user_metrics:
        user_metrics[nick] = {'count': 0, 'host': host, 'connects': 0, 'disconnects': 0, 'away_count': 0, 'away_time': 0, 'last_away_time': None}
    user_metrics[nick]['count'] += 1

    if host not in user_aliases:
        user_aliases[host] = set()
    user_aliases[host].add(nick)

    return hexchat.EAT_NONE

def user_connect(word, word_eol, userdata):
    """Track user connects."""
    nick = word[0]
    if nick not in user_metrics:
        user_metrics[nick] = {'count': 0, 'host': "", 'connects': 0, 'disconnects': 0, 'away_count': 0, 'away_time': 0, 'last_away_time': None}
    user_metrics[nick]['connects'] += 1

    return hexchat.EAT_NONE

def user_disconnect(word, word_eol, userdata):
    """Track user disconnects."""
    nick = word[0]
    if nick in user_metrics:
        user_metrics[nick]['disconnects'] += 1

    return hexchat.EAT_NONE

def user_away(word, word_eol, userdata):
    """Track when a user goes away."""
    nick = word[0]
    if nick in user_metrics:
        user_metrics[nick]['away_count'] += 1
        user_metrics[nick]['last_away_time'] = time.time()

    return hexchat.EAT_NONE

def user_back(word, word_eol, userdata):
    """Track when a user comes back."""
    nick = word[0]
    if nick in user_metrics and user_metrics[nick]['last_away_time']:
        away_duration = time.time() - user_metrics[nick]['last_away_time']
        user_metrics[nick]['away_time'] += away_duration
        user_metrics[nick]['last_away_time'] = None

    return hexchat.EAT_NONE

def send_metrics():
    """Send user metrics in a private message."""
    global last_report_time
    current_time = datetime.now()

    if current_time.minute == 0 and current_time.second == 0 and (current_time - last_report_time).seconds >= 3600:
        metrics_message = "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\nUser Metrics:\n"

        for user, data in user_metrics.items():
            away_percentage = (data['away_time'] / (current_time - last_report_time).total_seconds() * 100) if (current_time - last_report_time).total_seconds() > 0 else 0
            known_aliases = ', '.join(user_aliases.get(data['host'], []))
            user_metrics_line = (f"{user}: {data['count']} messages, {data['connects']} connects, "
                                 f"{data['disconnects']} disconnects, {data['away_count']} away changes, "
                                 f"{data['away_time'] / 60:.2f} min away, {away_percentage:.2f}% away, "
                                 f"Known Aliases: {known_aliases}")
            metrics_message += user_metrics_line + "\n"

        metrics_message += "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-"
        
        hexchat.command(f"msg {hexchat.get_info('nick')} {metrics_message}")

        last_report_time = current_time

def metrics_timer(userdata):
    """Check every second to see if we should send metrics."""
    send_metrics()
    return hexchat.EAT_NONE

hexchat.hook_print("Channel Message", count_messages)
hexchat.hook_print("Private Message", count_messages)
hexchat.hook_print("Connect", user_connect)
hexchat.hook_print("Disconnect", user_disconnect)
hexchat.hook_print("You Were Away", user_away)
hexchat.hook_print("You Are Back", user_back)
hexchat.hook_timer(1000, metrics_timer)

hexchat.prnt(f"{__module_name__} {__module_version__} loaded!")

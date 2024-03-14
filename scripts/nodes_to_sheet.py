"""
Save nodes to sheet

Ugly. Quick. Dirty mod to meshtastic shownodes function.
But it works.

Another option is to parse tabluate data.
 ¯\_(ツ)_/¯

"""

import meshtastic
import meshtastic.tcp_interface
from datetime import datetime
import timeago
import pandas as pd


radio_hostname = "meshtastic.local"  # Can also be an IP
iface = meshtastic.tcp_interface.TCPInterface(radio_hostname)

'''
functions from shownodes
https://python.meshtastic.org/mesh_interface.html#meshtastic.mesh_interface.MeshInterface.showNodes
'''


def formatFloat(value, precision=2, unit=''):
    """Format a float value with precsion."""
    return f'{value:.{precision}f}{unit}' if value else None


def getLH(ts):
    """Format last heard"""
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') if ts else None


def getTimeAgo(ts):
    """Format how long ago have we heard from this node (aka timeago)."""
    return timeago.format(datetime.fromtimestamp(ts), datetime.now()) if ts else None


if iface.nodes:
    for n in iface.nodes.values():
        if n["num"] == iface.myInfo.my_node_num:
            print(n["user"]["hwModel"])
            break
rows = []
for node in iface.nodes.values():
    row = {"N": 0}

    user = node.get('user')
    if user:
        row.update({
            "User": user['longName'],
            "AKA":  user['shortName'],
            "ID":   user['id'],
        })

    pos = node.get('position')
    if pos:
        row.update({
            "Latitude":  formatFloat(pos.get("latitude"),     4, "°"),
            "Longitude": formatFloat(pos.get("longitude"),    4, "°"),
            "Altitude":  formatFloat(pos.get("altitude"),     0, " m"),
        })

    metrics = node.get('deviceMetrics')
    if metrics:
        batteryLevel = metrics.get('batteryLevel')
        if batteryLevel is not None:
            if batteryLevel == 0:
                batteryString = "Powered"
            else:
                batteryString = str(batteryLevel)+"%"
            row.update({"Battery":   batteryString})
        row.update({
            "Channel util.": formatFloat(metrics.get('channelUtilization'), 2, "%"),
            "Tx air util.": formatFloat(metrics.get('airUtilTx'), 2, "%"),
        })

    row.update({
        "SNR":       formatFloat(node.get("snr"), 2, " dB"),
        "LastHeard": getLH(node.get("lastHeard")),
        "Since":     getTimeAgo(node.get("lastHeard")),
    })

    rows.append(row)

    rows.sort(key=lambda r: r.get('LastHeard') or '0000', reverse=True)
    for i, row in enumerate(rows):
        row['N'] = i+1

# Create pandas DataFrame directly from the list
df = pd.DataFrame(rows)

# Save as spreadsheet (replace 'mesh_nodes.xlsx' with your desired filename)
df.to_excel('mesh_nodes.xlsx', index=False)


iface.close()

"""Written to take an exported CSV from nautobot, and convert to json for use in "Intended state Job"""
import pandas as pd
import json

def convert_to_string(lst):
    result = [dict([a, str(x)] for a, x in b.items()) for b in lst]
    return result

df = pd.read_csv("nautobot_devices.csv", usecols=["device_role", "device_type", "status", "site", "rack", "position", "face"], header=0)
list_of_devices = df.to_dict(orient="records")
string_list_of_devices = convert_to_string(list_of_devices)


new_list_of_devices = []
for device in string_list_of_devices:
    temp_dict = {
      "device_role": "#ref:dcim.devicerole:name:" + device.get("device_role"),
      "device_type": "#ref:dcim.devicetype:model:" + device.get("device_type"),
      "site": "#ref:dcim.site:name:" + device.get("site"),
      "status": "#ref:extras.status:slug:" + device.get("status"),
      "rack": "#ref:dcim.rack:name:" + device.get(str("rack")) + ":site__name:" + device.get("site"),
      "position": device.get("position"),
      "face": device.get("face"),
    }
    new_list_of_devices.append(temp_dict)

jsonified = json.dumps(new_list_of_devices)




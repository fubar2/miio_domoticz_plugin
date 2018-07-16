#!/usr/bin/python3
import miio

good = {'ok'}
foo = miio.chuangmi_plug.ChuangmiPlug(ip="192.168.1.112",debug=1,token="3530efcedbd24a95df4716de429a7b0c")
res = foo.on()
res2 = foo.status()
print(res2)
if res==good:
    exit(0)
else:
    exit(1)


import asyncio
from kasa import SmartPlug

DEVICES = {
    "tv_lights": "192.168.4.66",
}

async def _control(ip, action):
    plug = SmartPlug(ip)
    await plug.update()
    if action == "on":
        await plug.turn_on()
    elif action == "off":
        await plug.turn_off()
    elif action == "toggle":
        if plug.is_on:
            await plug.turn_off()
        else:
            await plug.turn_on()
    return plug.is_on

async def _get_state(ip):
    plug = SmartPlug(ip)
    await plug.update()
    return plug.is_on

def turn_on(device):
    if device in DEVICES:
        asyncio.run(_control(DEVICES[device], "on"))

def turn_off(device):
    if device in DEVICES:
        asyncio.run(_control(DEVICES[device], "off"))

def toggle(device):
    if device in DEVICES:
        asyncio.run(_control(DEVICES[device], "toggle"))

def get_state(device):
    if device in DEVICES:
        return asyncio.run(_get_state(DEVICES[device]))
    return False
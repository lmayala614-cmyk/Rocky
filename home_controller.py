import asyncio
from kasa import Discover

DEVICES = {
    "tv_lights": "192.168.4.66",
}


async def _control(ip, action):
    device = await Discover.discover_single(ip)
    await device.update()
    if action == "on":
        await device.turn_on()
    elif action == "off":
        await device.turn_off()
    elif action == "toggle":
        if device.is_on:
            await device.turn_off()
        else:
            await device.turn_on()
    await device.update()
    return device.is_on


async def _get_state(ip):
    device = await Discover.discover_single(ip)
    await device.update()
    return device.is_on


def turn_on(device_name):
    if device_name in DEVICES:
        asyncio.run(_control(DEVICES[device_name], "on"))


def turn_off(device_name):
    if device_name in DEVICES:
        asyncio.run(_control(DEVICES[device_name], "off"))


def toggle(device_name):
    if device_name in DEVICES:
        asyncio.run(_control(DEVICES[device_name], "toggle"))


def get_state(device_name):
    if device_name in DEVICES:
        return asyncio.run(_get_state(DEVICES[device_name]))
    return False
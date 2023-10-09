from enum import Enum
import asyncio
from bleak import BleakClient, discover
from struct import pack

# UUID
CORE_INDICATE_UUID = "72c90005-57a9-4d40-b746-534e22ec9f9e"
CORE_NOTIFY_UUID = "72c90003-57a9-4d40-b746-534e22ec9f9e"
CORE_WRITE_UUID = "72c90004-57a9-4d40-b746-534e22ec9f9e"

# Constant values
MESSAGE_TYPE_INDEX = 0
EVENT_TYPE_INDEX = 1
STATE_INDEX = 2
MESSAGE_TYPE_ID = 1
EVENT_TYPE_ID = 0


class MESH_MSG(Enum):
    EXIT = 0
    HOGE = 1
    LE_R = 2
    LE_G = 3
    LE_B = 4


class MESH_TYPE(Enum):
    MESH_100BU = "MESH-100BU"
    MESH_100LE = "MESH-100LE"
    MESH_100GP = "MESH-100GP"
    MESH_100AC = "MESH-100AC"


class MESH_EVENT:
    def __init__(self):
        self.name = ""
        self.event_counter = 0

    def on_receive_indicate(self, sender, data: bytearray):
        data = bytes(data)
        print("[indicate]", data)

    def on_receive_notify(self, sender, data: bytearray):
        if (
            data[MESSAGE_TYPE_INDEX] != MESSAGE_TYPE_ID
            and data[EVENT_TYPE_INDEX] != EVENT_TYPE_ID
        ):
            return

        # use data[..]
        print(self.name, "'s Event is Received.", self.event_counter)
        self.event_counter = self.event_counter + 1

        return


class MESH_COMMAND:
    def __init__(self):
        pass

    def generate_command(red, green, blue):
        messagetype = 1
        # red = 127
        # green = 0
        # blue = 0
        duration = 5 * 1000  # 5,000[ms]
        on = 1 * 1000  # 1,000[ms]
        off = 500  # 500[ms]
        pattern = 1  # 1:blink, 2:firefly
        command = pack(
            "<BBBBBBBHHHB",
            messagetype,
            0,
            red,
            0,
            green,
            0,
            blue,
            duration,
            on,
            off,
            pattern,
        )
        return command


class MESH:
    def __init__(self, mesh_type: MESH_TYPE, event: MESH_EVENT = None):
        self.name = mesh_type.value
        self.event = MESH_EVENT() if event == None else event
        self.event.name = self.name
        self.queue = asyncio.Queue()
        self.client = None

    async def push_msg(self, msg: MESH_MSG):
        await self.queue.put(msg)

    async def send_command(self, command):
        if self.client == None:
            print("client is None!")
            return

        checksum = 0
        for x in command:
            checksum += x

        command = command + pack("B", checksum & 0xFF)
        print("command", command)

        try:
            await self.client.write_gatt_char(CORE_WRITE_UUID, command, response=True)
        except Exception as e:
            print("error", e)
            return

        await asyncio.sleep(0.01)

    async def scan(self):
        while True:
            print("scan ", self.name, "...")
            try:
                return next(
                    d
                    for d in await discover()
                    if d.name and d.name.startswith(self.name)
                )
            except StopIteration:
                continue

    async def main(self):
        device = await self.scan()
        print("found", device.name, device.address)

        async with BleakClient(device, timeout=None) as client:
            self.client = client
            await client.start_notify(CORE_NOTIFY_UUID, self.event.on_receive_notify)
            await client.start_notify(
                CORE_INDICATE_UUID, self.event.on_receive_indicate
            )
            await client.write_gatt_char(
                CORE_WRITE_UUID, pack("<BBBB", 0, 2, 1, 3), response=True
            )
            print(device.name, "is connected.")
            self.queue = asyncio.Queue()

            while True:
                await asyncio.sleep(0.01)  # need to recieve BLE event
                if not self.queue.empty():
                    msg = await self.queue.get()
                    match msg:
                        case MESH_MSG.EXIT:
                            print(device.name, "Exit msg is received.")
                            self.client = None
                            await client.disconnect()  # ?
                            self.event.event_counter = self.event.event_counter - 1
                            break
                        case MESH_MSG.HOGE:
                            print("hoge!")
                        case MESH_MSG.LE_R:
                            print("SEND!")
                            command = MESH_COMMAND.generate_command(127, 0, 0)
                            await self.send_command(command)
                        case MESH_MSG.LE_G:
                            print("SEND!")
                            command = MESH_COMMAND.generate_command(0, 127, 0)
                            await self.send_command(command)
                        case MESH_MSG.LE_B:
                            print("SEND!")
                            command = MESH_COMMAND.generate_command(0, 0, 127)
                            await self.send_command(command)

                # if not self.queue.empty() and await self.queue.get() == MESH_MSG.EXIT:
                #     print(device.name, "Exit msg is received.")
                #     await client.disconnect()  # ?
                #     self.event.event_counter = self.event.event_counter - 1
                #     break
                # if not self.queue.empty() and await self.queue.get() == MESH_MSG.HOGE:
                #     print("hoge!")

            print(device.name, "is Ended.")

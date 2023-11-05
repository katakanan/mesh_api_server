# from quart_trio import QuartTrio
import signal
from quart import render_template, Quart, request, websocket
# import trio
import asyncio
# import signal
# import datetime
from meshlib import *

le_block = MESH(MESH_TYPE.MESH_100LE)

class MESH_BU_EVENT(MESH_EVENT):
    def on_receive_notify(self, sender, data: bytearray):
        if (
            data[MESSAGE_TYPE_INDEX] != MESSAGE_TYPE_ID
            and data[EVENT_TYPE_INDEX] != EVENT_TYPE_ID
        ):
            return

        # use data[..]
        msg = f"{self.name}'s Event is Received!!! {self.event_counter}"
        print(msg)
        self.event_counter = self.event_counter + 1
        self.event_queue.put(MESH_EVENT_MSG.BU_PUSH)
        return

bu_block = MESH(MESH_TYPE.MESH_100BU, MESH_BU_EVENT())

app = Quart(__name__)

@app.get('/')
async def index():
    return await render_template("ControlUI.html")

@app.route("/send_cmd", methods=["GET"])
async def send_cmd():
    params = request.args
    response = {}
    color_msg = MESH_MSG.LE_R
    if "color" in params:
        # print(params)
        match params.get("color"):
            case "R":
                color_msg = MESH_MSG.LE_R
            case "G":
                color_msg = MESH_MSG.LE_G
            case "B":
                color_msg = MESH_MSG.LE_B

    app.add_background_task(le_block.push_msg, color_msg)
    return 'Sending MSG'

@app.route("/find")
async def find_mesh_block():
    app.add_background_task(le_block.main)
    app.add_background_task(bu_block.main)
    # app.add_background_task(loop.run_until_complete, le_block.main())
    return "finding mesh block"

@app.route("/exit", methods=["GET"])
async def exit_mesh():
    app.add_background_task(le_block.push_msg, MESH_MSG.EXIT)
    app.add_background_task(bu_block.push_msg, MESH_MSG.EXIT)
    return 'Disconnecting Mesh'

@app.websocket('/ws')
async def ws():
    while True:
        await asyncio.sleep(0.01)
        if not bu_block.event.event_queue.empty():
            msg = bu_block.event.event_queue.get()
            await websocket.send(msg)

        # data = await websocket.receive()
        # await websocket.send(data)

if __name__ == "__main__":
    # app.run(debug=True)
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(app.run_task(debug=True))
    except KeyboardInterrupt:
        pass
    finally:
        # app.add_background_task(le_block.push_msg, MESH_MSG.EXIT)
        # app.add_background_task(bu_block.push_msg, MESH_MSG.EXIT)
        loop.run_until_complete(app.shutdown())
        
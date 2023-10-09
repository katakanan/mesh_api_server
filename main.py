# from quart_trio import QuartTrio
from quart import render_template, Quart, request
# import trio
# import asyncio
# import signal
# import datetime
from meshlib import MESH, MESH_TYPE, MESH_MSG

le_block = MESH(MESH_TYPE.MESH_100LE)

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
    return "finding mesh block"

@app.route("/exit", methods=["GET"])
async def exit_mesh():
    app.add_background_task(le_block.push_msg, MESH_MSG.EXIT)
    return 'Disconnecting Mesh'

if __name__ == "__main__":
    app.run(debug=True)
from quart_trio import QuartTrio
from quart import render_template
import trio
import datetime

app = QuartTrio(__name__)

@app.before_serving
async def startup():
    app.nursery.start_soon(background_task)

@app.get('/')
async def index():
    return await render_template("ControlUI.html")

@app.route("/hoge")
async def hello():
    app.nursery.start_soon(heavy_task)
    print(f"heavy task start at {datetime.datetime.now()}")
    return 'world'

async def background_task():
    while True:
        print('background_task working!!!!!')
        await trio.sleep(2)

async def heavy_task():
    await trio.sleep(20)
    print(f"heavy task finished at {datetime.datetime.now()}")

if __name__ == "__main__":
    app.run()

import tkinter as tk
import asyncio


def run_tkinter():
    root = tk.Tk()
    root.geometry("800x600")
    root.title("Tkinter GUI")
    label = tk.Label(root, text="Hello")
    label.pack()
    root.mainloop()


from flask import Flask, request, jsonify, make_response

app = Flask(__name__)


@app.route("/hoge", methods=["GET"])
def getHoge():
    params = request.args
    response = {}
    if "param" in params:
        # print(params)
        response.setdefault("res", "param is:" + params.get("param"))
        # response.setdefault("res", "param is :", params.get("param"))
    return make_response(jsonify(response))


@app.route("/hoge", methods=["POST"])
def postHoge():
    params = request.json
    response = {}
    if "param" in params:
        response.setdefault("res", "param is :" + params.get("param"))
    return make_response(jsonify(response))


async def run_flask():
    await asyncio.sleep(1)
    app.run(host="127.0.0.1", port=5000)


if __name__ == "__main__":
    run_tkinter()
    asyncio.run(run_flask())

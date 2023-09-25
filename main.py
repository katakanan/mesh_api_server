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
    if "param" in paras:
        response.setdefault("res", "param is :" + params.get("param"))
    return make_response(jsonify(response))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)

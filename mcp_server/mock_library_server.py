from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/add_user", methods=["POST"])
def add_user():
    data = request.get_json()
    print(f"Library service received: {data}")
    return jsonify({ "status": "success", "service": "library", "data_received": data }), 200

if __name__ == "__main__":
    app.run(port=8081)

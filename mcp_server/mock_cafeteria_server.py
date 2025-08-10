from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/order_meal", methods=["POST"])
def order_meal():
    data = request.get_json()
    print(f"Cafeteria service received: {data}")
    return jsonify({ "status": "success", "service": "cafeteria", "data_received": data }), 200

if __name__ == "__main__":
    app.run(port=8082)

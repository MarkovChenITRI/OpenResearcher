from flask import Flask, jsonify, render_template

app = Flask(__name__)

# API (回傳封包)
@app.route("/api/data")
def get_data():
    return jsonify({
        "message": "Hello, this is demo data!",
        "values": [1, 2, 3, 4, 5]
    })

# WebUI (回傳html)
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
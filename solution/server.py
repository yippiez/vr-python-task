
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/v1/post_csv_data', methods=['POST'])
def post_csv_data():
    print("POST request received")
    print(request.data)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    # run app in debug mode on port 8080
    app.run(debug=True, port=8080)

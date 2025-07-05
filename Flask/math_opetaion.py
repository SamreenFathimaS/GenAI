from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "✅ Flask Math API is running! Use /calculate with parameters."})

@app.route("/calculate", methods=["GET"])
def calculate():
    # Get query params
    operation = request.args.get("operation", "").lower()
    num1 = request.args.get("num1")
    num2 = request.args.get("num2")

    # Validate input
    if not all([operation, num1, num2]):
        return jsonify({"error": "Please provide operation, num1 and num2 in query params."}), 400

    try:
        num1 = float(num1)
        num2 = float(num2)
    except ValueError:
        return jsonify({"error": "num1 and num2 must be numbers."}), 400

    # Do the operation
    if operation == "add":
        result = num1 + num2
    elif operation == "subtract":
        result = num1 - num2
    elif operation == "multiply":
        result = num1 * num2
    elif operation == "divide":
        if num2 == 0:
            return jsonify({"error": "Cannot divide by zero!"}), 400
        result = num1 / num2
    else:
        return jsonify({"error": "Unsupported operation. Use add, subtract, multiply, divide."}), 400

    return jsonify({
        "operation": operation,
        "num1": num1,
        "num2": num2,
        "result": result
    })

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

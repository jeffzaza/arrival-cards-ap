import os
import boto3
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

region = os.environ.get('AWS_REGION', 'ap-southeast-1')
table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'arrival-cards')

print(f"Now starting app with region={region}, table={table_name}")

try:
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)
    print("DynamoDB table initialized.")
except Exception as e:
    print("Error initializing DynamoDB:", str(e))

@app.route("/arrival-card", methods=["POST"])
def create_card():
    print("Received POST /arrival-card")
    try:
        data = request.json
        print(f"Payload: {data}")
        item = {
            'id_number': data['id_number'],
            'arrival_date': data['arrival_date'],
            'name': data['name'],
            'created_at': datetime.datetime.utcnow().isoformat()
        }
        table.put_item(Item=item)
        print("Item written to DynamoDB.")
        return jsonify({"message": "Arrival card created successfully"}), 201
    except Exception as e:
        print("Error in create_card:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/arrival-cards", methods=["GET"])
def query_cards():
    print("Received GET /arrival-cards")
    try:
        response = table.scan()
        items = response.get('Items', [])
        print(f"Items returned: {len(items)}")
        return jsonify(items), 200
    except Exception as e:
        print("Error in query_cards:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/arrival-card/<id_number>", methods=["DELETE"])
def delete_card(id_number):
    print(f"Received DELETE /arrival-card/{id_number}")
    try:
        table.delete_item(Key={'id_number': id_number})
        print("Item deleted.")
        return jsonify({"message": "Arrival card deleted successfully"}), 200
    except Exception as e:
        print("Error in delete_card:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health_check():
    print("Received ALB health check")
    return "OK", 200


if __name__ == "__main__":
    print("Flask app starting on port 5000...")
    app.run(host="0.0.0.0", port=5000)


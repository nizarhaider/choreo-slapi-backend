import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import json
from dotenv import load_dotenv


app = Flask(__name__)

load_dotenv()  

URI = os.getenv("URI")

client = MongoClient(URI)


@app.route('/api/health', methods=['GET'])
def health_check():
    # Health check endpoint, return 200 OK
    return jsonify({"status": "OK"}), 200

@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        # Connect to the "indicators" database and the specified collection
        database = client.indicators
        collection_name = request.args.get('collection_name')
        date_param = request.args.get('date')  # Get date parameter
        
        if not date_param:
            # date parameter is missing
            return jsonify({"error": "Date parameter is missing"}), 400
        
        if not date_param.strip():
            # date value is missing 
            return jsonify({"error": "Date value is missing"}), 400
            
        if collection_name == "tourists":
            collection = database.Tourists
            pipeline = [
                {"$match": {"date": {"$gte": datetime.strptime(date_param, '%Y-%m-%d')}}},  # Filter by date
                {"$project": {"_id": 0, "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}}, "Tourists": 1}}
            ]
        elif collection_name == "inflation":
            collection = database.Inflation
            pipeline = [
                {"$match": {"date": {"$gte": datetime.strptime(date_param, '%Y-%m-%d')}}},  # Filter by date
                {"$project": {"_id": 0, "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}}, "Inflation": 1}}
            ]
        elif collection_name == "land_inflation":
            collection = database.Land_inflation
            pipeline = [
                {"$match": {"date": {"$gte": datetime.strptime(date_param, '%Y-%m-%d')}}},  # Filter by date
                {"$project": {"_id": 0, "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}}, "indice": 1}}
            ]
        else:
            return jsonify({"error": "Collection Not Found"}), 404

        # Execute the aggregation pipeline
        result = list(collection.aggregate(pipeline))
        return jsonify(result), 200
    
    except KeyError:
        # Handle missing query string parameters
        return jsonify({"error": "Missing collection_name or date parameter"}), 400
    except Exception as e:
        # Handle other unexpected errors
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

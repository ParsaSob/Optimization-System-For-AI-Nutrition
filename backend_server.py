#!/usr/bin/env python3
"""
Backend Server for Meal Optimization
Simple server with only two endpoints: /health and /optimize-meal
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from rag_optimization_engine import RAGMealOptimizer

app = Flask(__name__)
CORS(app)

# Initialize optimizer
rag_meal_optimizer = RAGMealOptimizer()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "message": "Server is running"
    })

@app.route('/optimize-meal', methods=['POST'])
def optimize_meal():
    """Advanced single meal optimization endpoint with automatic helper ingredients"""
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({"error": "No request data provided"}), 400
        
        # Validate required fields
        required_fields = ['rag_response', 'target_macros', 'user_preferences', 'meal_type']
        for field in required_fields:
            if field not in request_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Extract data
        rag_response = request_data['rag_response']
        target_macros = request_data['target_macros']
        user_preferences = request_data['user_preferences']
        meal_type = request_data['meal_type']
        
        print(f"🚀 Starting advanced optimization for {meal_type} meal...")
        print(f"🎯 Target macros: {target_macros}")
        
        # Run advanced optimization with request_data for helper selection
        result = rag_meal_optimizer.optimize_single_meal(
            rag_response=rag_response,
            target_macros=target_macros,
            user_preferences=user_preferences,
            meal_type=meal_type,
            request_data=request_data  # Pass full request data for proper helper selection
        )
        
        print(f"✅ Advanced optimization completed!")
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "error": f"Advanced meal optimization failed: {str(e)}",
            "status": "error"
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Meal Optimization Server...")
    print("📡 Endpoints:")
    print("   - GET  /health")
    print("   - POST  /optimize-meal")

    # Get port from environment variable (for Render) or use default
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🌐 Server will run on port: {port}")
    print(f"🔧 Debug mode: {debug_mode}")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug_mode)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
            exit(1)

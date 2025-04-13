# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import redis
import json
import uuid
import time

app = Flask(__name__)
CORS(app)  # This allows cross-origin requests

# Connect to Redis
# Make sure Redis server is running
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Home route to serve the web interface
@app.route('/')
def home():
    return render_template('index.html')

# API route to generate code
@app.route('/api/generate', methods=['POST'])
def generate_code():
    data = request.json
    language = data.get('language', 'python')
    requirements = data.get('requirements', '')
    
    # Generate a unique ID for this code snippet
    snippet_id = str(uuid.uuid4())
    
    # Simple code generation based on templates
    # In a real app, this could be more sophisticated
    if language == 'python':
        generated_code = f"""
# Generated code for: {requirements}
def main():
    print("Implementation for: {requirements}")
    # TODO: More logic has to be written. It will come soon here..\n \t Till then praise me for this.
    
if __name__ == "__main__":
    main()
"""
    elif language == 'javascript':
        generated_code = f"""
// Generated code for: {requirements}
function main() {{
    console.log("Implementation for: {requirements}");
    // TODO: Add actual implementation
}}

main();
"""
    else:
        generated_code = f"// Template for {language} not available yet"
    
    # Store in Redis with 1-hour expiration
    redis_client.setex(
        f"code:{snippet_id}", 
        3600,  # 1 hour in seconds
        json.dumps({
            'language': language,
            'requirements': requirements,
            'code': generated_code,
            'created_at': time.time()
        })
    )
    
    return jsonify({
        'snippet_id': snippet_id,
        'language': language,
        'code': generated_code
    })

# API route to retrieve a saved snippet
@app.route('/api/snippet/<snippet_id>', methods=['GET'])
def get_snippet(snippet_id):
    snippet_data = redis_client.get(f"code:{snippet_id}")
    
    if snippet_data is None:
        return jsonify({'error': 'Snippet not found or expired'}), 404
    
    return jsonify(json.loads(snippet_data))

# Run the app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

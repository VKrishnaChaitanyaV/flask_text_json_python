from flask import Flask, request, jsonify
from openai import OpenAI
import re
import os
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

def get_firestore_client():
    if not firebase_admin._apps:
        firebase_credentials_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        cred_dict = json.loads(firebase_credentials_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    return firestore.client()

@app.route('/users')
def get_users():
    db = get_firestore_client()
    users_ref = db.collection('users')
    docs = users_ref.stream()
    users = [{doc.id: doc.to_dict()} for doc in docs]
    return jsonify(users)

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello, world!'})

@app.route('/api/texttojson', methods=['POST'])
def ocr_base64():
    data = request.get_json()

    if not data or 'content' not in data:
        return jsonify({'error': 'Missing content in request'}), 400

    try:
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        print("Openai start"+data['content'])
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[
                {"role": "user",
                 "content": data['content'] + data['format']
                 }
            ]
        )
        
        #res = completion.choices[0].message.content #replace('Here is the job details converted into JSON format:\n\n```json\n{\n  "job_details": ',"").replace("\n}\n```\n\nFeel free to let me know if there's anything else you need!","")
        #match = re.search(r"json\s*(\{.*?\})\s*", res, re.DOTALL)

        #job_details=""
        #if match:
        #    job_details = match.group(1)  # Extracted JSON string
        #else:
        #    print("No JSON block found.")"""

        #return jsonify({'results': completion.choices[0].message})
        text = completion.choices[0].message.content
        text = text.replace("```json","").replace("```","")
        return jsonify({'result': text}) #job_details

    except Exception as e:
        return jsonify({'error mesage': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use Render's PORT or default to 5000
    app.run(host='0.0.0.0', port=port, debug=True)

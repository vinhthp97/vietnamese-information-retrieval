from flask import Flask, request, jsonify
import os
import json
import numpy as np
# from services.preprocessing import get_cleaned_query_request, vectorize_query, cosine_similarity, get_relevant_doc_ids
from services.preprocessing import get_cleaned_query_request, vectorize_query
from flask_cors import CORS

# ====== Khởi tạo Flask App ======
app = Flask(__name__)
CORS(app)

# ====== Load dữ liệu một lần khi start server ======
BASE_DIR = os.path.join(os.path.dirname(__file__), 'data', 'processed-data')

with open(os.path.join(BASE_DIR, 'tfidf_vectors.json'), 'r', encoding='utf-8') as f:
    tfidf_vectors = json.load(f)

with open(os.path.join(BASE_DIR, 'token_idf.json'), 'r', encoding='utf-8') as f:
    token_idf = json.load(f)

with open(os.path.join(BASE_DIR, 'ordered-data.json'), 'r', encoding='utf-8') as f:
    articles = json.load(f)

with open(os.path.join(BASE_DIR, 'inverted-index.json'), 'r', encoding='utf-8') as f:
    inverted_index = json.load(f)

vocab = list(token_idf.keys())
token2idx = {token: idx for idx, token in enumerate(vocab)}

# ====== API Endpoint ======


@app.route('/api/search', methods=['POST'])
def search_api():
    data = request.get_json()
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Missing query"}), 400

    # Xử lý truy vấn
    query_tokens = get_cleaned_query_request(query)
    query_vec = vectorize_query(query, token_idf, token2idx)

    # Lọc tài liệu liên quan
    relevant_doc_ids = get_relevant_doc_ids(query_tokens, inverted_index)

    results = []
    for doc_id_str in relevant_doc_ids:
        doc_vec = np.array(tfidf_vectors.get(doc_id_str, []))
        if len(doc_vec) == 0:
            continue
        score = cosine_similarity(query_vec, doc_vec)
        if score > 0:
            doc_id = int(doc_id_str)
            doc_info = next((a for a in articles if a["id"] == doc_id), None)
            if doc_info:
                results.append({
                    "title": doc_info["title"],
                    "description": doc_info["path"],
                    "similarity": round(score, 4)
                })

    results.sort(key=lambda x: x["similarity"], reverse=True)

    return jsonify(results[:5])  # trả về top 5 kết quả


# ====== Run Server ======
if __name__ == '__main__':
    app.run(debug=True)

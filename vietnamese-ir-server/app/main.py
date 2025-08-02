from flask import Flask, request, jsonify
from services.action_service import load_articles, create_inverted_index, calculate_idf, calculate_tfidf, search_optimized
from flask_cors import CORS
import time

# ====== Khởi tạo Flask App ======
app = Flask(__name__)
CORS(app)

# ====== Load dữ liệu một lần khi start server ======

articles = load_articles()
inverted_index = create_inverted_index(articles)
total_documents = len(articles)
idf_dict = calculate_idf(inverted_index, total_documents)
tfidf_matrix, token_to_idx = calculate_tfidf(articles, idf_dict)

# ====== API Endpoint ======


@app.route('/api/search', methods=['POST'])
def search_api():
    data = request.get_json()
    query = data.get("query", "").strip()
    results = []

    if not query:
        return jsonify({"error": "Missing query"}), 400

    # Xử lý truy vấn

    search_results = search_optimized(
        query, inverted_index, tfidf_matrix, token_to_idx, idf_dict, articles, 5)
    if not search_results:
        return jsonify({"message": "Không tìm thấy kết quả"}), 404
    for doc_id, sim in search_results:
        title = next((article['title'] for article in articles if article['id']
                     == doc_id), "Không tìm thấy tiêu đề")
        content = next((article['content'] for article in articles if article['id']
                       == doc_id), "Không tìm thấy nội dung")
        results.append({
            "id": doc_id,
            "title": title,
            "content": content,
            "similarity": round(sim, 3)
        })

    return jsonify(results) if len(results) > 0 else jsonify({"message": "Không tìm thấy kết quả"}), 200


# ====== Run Server ======
if __name__ == '__main__':
    app.run(debug=True)

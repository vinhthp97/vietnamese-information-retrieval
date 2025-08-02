import json
from flask import Flask, request, jsonify
from services.action_service import load_articles, create_inverted_index, calculate_idf, calculate_tfidf, search_optimized
from flask_cors import CORS
import os

# ====== Khởi tạo Flask App ======
app = Flask(__name__)
CORS(app)

# ====== Load dữ liệu một lần khi start server ======

# # Kiểm tra các file tài nguyên cần thiết
prepared_resource = "articles.json"
is_missing = False
processed_data_dir = os.path.join(os.path.dirname(__file__), 'data', 'processed-data')
if os.path.exists(processed_data_dir) and os.path.isdir(processed_data_dir):
    # Lấy danh sách các file trong thư mục
    files = os.listdir(processed_data_dir)
    if prepared_resource not in files:
        is_missing = True
else:
    is_missing = True
# Nếu chưa tồn tại file articles.json, đọc tập tài liệu và tạo 1 file mới
if is_missing:
    articles = load_articles()
    inverted_index = create_inverted_index(articles)
    total_documents = len(articles)
    idf_dict = calculate_idf(inverted_index, total_documents)
    tfidf_matrix, token_to_idx = calculate_tfidf(articles, idf_dict)

    # Xuất ra file inverted-index.json
    output_dir = os.path.join(os.path.dirname(__file__), 'data', 'processed-data')
    os.makedirs(output_dir, exist_ok=True)
    
    articles_output_path = os.path.join(output_dir, 'articles.json')

    with open(articles_output_path, 'w', encoding='utf-8') as json_file:
        json.dump(articles, json_file, ensure_ascii=False, indent=4)
else:
    with open(os.path.join(os.path.dirname(__file__), 'data', 'processed-data', 'articles.json'), 'r', encoding='utf-8') as f:
        articles = json.load(f)
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

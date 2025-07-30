from collections import defaultdict
import math
import re
import os
import numpy as np
from underthesea import word_tokenize
import json

global number_of_doc
number_of_doc = 0


class ProcessedData:
    def __init__(self, title: str, topic: str, path: str):
        self.title = title
        self.topic = topic
        self.path = path

    def __repr__(self):
        return f"ProcessedData(title={self.title!r}, topic={self.topic!r}, path={self.path!r})"

# Đọc các bài viết từ thư mục vnexpress
# Thực hiện định danh tạm thời cho mỗi bài viết sau khi đã làm sạch nội dung


def read_articles():
    # Lấy đường dẫn của file hiện tại
    vnexpress_dir = os.path.join(os.path.dirname(
        __file__), '..', 'data', 'vnexpress')
    # Đường dẫn tương đối đến tệp bạn muốn truy cập
    data_dir = os.path.abspath(vnexpress_dir)

    articles = []
    id = 0  # Tạo 1 id định danh cho mỗi bài viết
    for topic in os.listdir(data_dir):
        topic_path = os.path.join(data_dir, topic)
        if os.path.isdir(topic_path):
            for filename in os.listdir(topic_path):
                file_path = os.path.join(topic_path, filename)
                if os.path.isfile(file_path) and filename.endswith(".txt"):
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        if lines:
                            title = lines[0].strip()
                            relative_path = os.path.relpath(file_path)
                            # Lấy toàn bộ nội dung trừ dòng đầu tiên
                            content = "".join(lines[1:]).strip()
                            # Xử lý lấy danh sách word token bằng clean_text
                            cleaned_tokens = clean_text(content)
                            articles.append({
                                "id": id,
                                "title": title,
                                "topic": topic,
                                "path": relative_path,
                                "tokens": cleaned_tokens
                            })
                            id += 1
    # Chuyển đổi articles thành json và ghi ra file ordered-data.json
    output_dir = os.path.join(os.path.dirname(
        __file__), '..', 'data', 'processed-data')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'ordered-data.json')

    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(articles, json_file, ensure_ascii=False, indent=4)
    return articles


# Chuẩn hóa văn bản
# Input: text
# Output: danh sách các từ đã được loại bỏ stopwords và chuyển đổi thành chữ thường
def clean_text(text):
    stopwords_path = os.path.join(os.path.dirname(
        __file__), '..', 'data', 'stopwords', 'vietnamese-stopwords.txt')
    with open(stopwords_path, 'r', encoding='utf-8') as f:
        stopwords = set(line.strip() for line in f if line.strip())

    clean_doc = re.sub('\W+', ' ', text)

    # Tokenize the text, lowercase it, and split into array of words
    tokens = word_tokenize(clean_doc, format="text").lower().split()

    # Tiến hành thay thế các khoảng trắng ' ' trong các từ ghép thành '_'
    tokens = [token.replace(' ', '_') for token in tokens]

    # Remove stopwords
    cleaned_tokens = [token for token in tokens if token not in stopwords]

    return cleaned_tokens

# Tạo chỉ mục ngược


def create_inverted_index():
    global number_of_doc
    overall_token_freq = {}
    overall_token_df = {}

    # đọc file orded-data.json
    with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'processed-data', 'ordered-data.json'), 'r', encoding='utf-8') as f:
        articles = json.load(f)

    # Lấy số lượng bài viết
    number_of_doc = len(articles)

    # lăp qua từng đối tượng (bài viết đã được xử lý) trong danh sách articles
    for article in articles:
        current_doc_max_freq = 0
        # Lấy id của bài viết
        doc_id = article['id']
        doc_tokens = article['tokens']

        # 1- Tìm từ có tần suất xuất hiện cao nhất trong tài liệu
        current_doc_max_freq = find_max_freq_token(doc_tokens)

        # 2- Tạo từ điển cho tần suất từ trong tài liệu
        for token in doc_tokens:
            if token not in overall_token_freq.keys():
                overall_token_freq[token] = [(doc_id, 1)]
            else:
                # Nếu từ đã có trong overall_token_freq, cập nhật tần suất
                found = False
                for i, (existing_doc_id, freq) in enumerate(overall_token_freq[token]):
                    if existing_doc_id == doc_id:
                        overall_token_freq[token][i] = (
                            existing_doc_id, freq + 1)
                        found = True
                        break
                # Trường hợp chưa tồn tại
                if found == False:
                    overall_token_freq[token].append((doc_id, 1))

            # 2- Tìm từ có tần suất xuất hiện cao nhất trong tài liệu
            current_doc_max_freq = find_max_freq_token(doc_tokens)

            # 3- Cập nhật chỉ mục ngược
            D_t = overall_token_freq[token]
            for inverted_data_idx, (doc_id, freq) in enumerate(D_t):
                # Tính toán tần suất từ (TF) cho mỗi từ trong tài liệu hiện tại
                update_tf = freq / current_doc_max_freq
                # Cập nhật lại tần suất từ trong overall_token_freq
                overall_token_freq[token][inverted_data_idx] = (
                    doc_id, update_tf)

    # Xuất ra file inverted-index.json
    output_dir = os.path.join(os.path.dirname(
        __file__), '..', 'data', 'processed-data')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'inverted-index.json')

    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(overall_token_freq, json_file,
                  ensure_ascii=False, indent=4)


# Tính toán số lượng tài liệu chứa từ khóa (df) cho mỗi từ trong chỉ mục ngược
# và xuất ra file token_df.json
def calculate_word_idf():
    global number_of_doc
    token_idf = {}
    # Đọc dữ liệu từ file inverted-index.json
    with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'processed-data', 'inverted-index.json'), 'r', encoding='utf-8') as f:
        articles = json.load(f)

    for key, value in articles.items():
        # Tính toán số lượng tài liệu chứa từ khóa (df)
        idf = math.log2(number_of_doc / len(value))
        token_idf[key] = idf

    # Xuất ra file token_df.json
    output_dir = os.path.join(os.path.dirname(
        __file__), '..', 'data', 'processed-data')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'token_idf.json')

    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(token_idf, json_file, ensure_ascii=False, indent=4)

    return token_idf


def find_max_freq_token(doc_tokens):
    max_freq = 0
    freq_dict = {}

    for token in doc_tokens:
        if token in freq_dict:
            freq_dict[token] += 1
        else:
            freq_dict[token] = 1

    # Duyệt qua từng token trong tài liệu
    for token, freq in freq_dict.items():
        # Nếu tần suất của token lớn hơn tần suất tối đa hiện tại
        if freq > max_freq:
            max_freq = freq

    return max_freq


def build_tfidf_vector(inverted_index, token_idf, token2idx):
    # Lấy tất cả doc_id
    all_doc_ids = set()
    for doc_tf_list in inverted_index.values():
        for doc_id, _ in doc_tf_list:
            all_doc_ids.add(doc_id)

    # Với mỗi tài liệu, lưu {token: normalized_tf}
    docid_token_tf = defaultdict(dict)

    for token, doc_tf_list in inverted_index.items():
        for doc_id, tf_norm in doc_tf_list:
            docid_token_tf[doc_id][token] = tf_norm

    vectors = {}
    for doc_id in all_doc_ids:
        vec = np.zeros(len(token2idx))
        tf_dict = docid_token_tf.get(doc_id, {})
        for token, idx in token2idx.items():
            tf = tf_dict.get(token, 0)  # Nếu token không xuất hiện thì là 0
            idf = token_idf.get(token, 0)
            vec[idx] = tf * idf
            print(vec)
        vectors[doc_id] = vec
    # print(vectors)
    return vec


# Gọi các hàm để thực hiện tiền xử lý dữ liệu
read_articles()
create_inverted_index()
vocab = list(calculate_word_idf())
token2id = {token: idx for idx, token in enumerate(vocab)}
with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'processed-data', 'inverted-index.json'), 'r', encoding='utf-8') as f:
    inverted_index = json.load(f)
with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'processed-data', 'token_idf.json'), 'r', encoding='utf-8') as f:
    token_idf = json.load(f)
# print()
build_tfidf_vector(inverted_index, token_idf, token2id)

################ Xử lý cho truy vấn ################


def get_cleaned_query_request(query: str):
    # Tiền xử lý truy vấn
    query = query.strip().lower()
    # Tokenize và loại bỏ stopwords
    tokens = clean_text(query)
    return tokens

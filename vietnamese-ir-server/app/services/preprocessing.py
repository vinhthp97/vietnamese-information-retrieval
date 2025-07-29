import re
import os
from underthesea import word_tokenize
import json

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
    vnexpress_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'vnexpress')
    # Đường dẫn tương đối đến tệp bạn muốn truy cập
    data_dir = os.path.abspath(vnexpress_dir)

    articles = []
    id = 0 # Tạo 1 id định danh cho mỗi bài viết
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
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed-data')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'ordered-data.json')

    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(articles, json_file, ensure_ascii=False, indent=4)
    return articles


# Chuẩn hóa văn bản
# Input: text
# Output: danh sách các từ đã được loại bỏ stopwords và chuyển đổi thành chữ thường
def clean_text(text):
    stopwords_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'stopwords', 'vietnamese-stopwords.txt')
    with open(stopwords_path, 'r', encoding='utf-8') as f:
        stopwords = set(line.strip() for line in f if line.strip())

    clean_doc = re.sub('\W+',' ', text)
    
    # Tokenize the text, lowercase it, and split into array of words
    tokens = word_tokenize(clean_doc, format="text").lower().split()

    # Tiến hành thay thế các khoảng trắng ' ' trong các từ ghép thành '_'
    tokens = [token.replace(' ', '_') for token in tokens]
    
    # Remove stopwords
    cleaned_tokens = [token for token in tokens if token not in stopwords]
    
    return cleaned_tokens

# Tạo chỉ mục ngược
def create_inverted_index(tokens_id, tokens):

    # Xây dựng tập từ vựng (V) dạng cấu trúc chỉ mục ngược
    # (V) là cấu trúc dữ liệu dạng dictionary <key: token_1, value: [(doc_idx_1, tf(token_1)), (doc_idx_2, tf(token_1)), v.v.>
    inverted_index = {}

    # Chúng cũng cần xác định trọng số lớn nhất của từ xuất hiện trong mỗi tài liệu/văn bản để cập nhật lại tf
    # Cấu trúc dữ liệu dạng dictionary <key: doc_idx, value: <key: token, value: token_freq>>
    doc_idx_token_token_freq = {}

    # Duyệt qua từng token
    for token in tokens:
        # Kiểm tra xem token đã tồn tại trong tập từ vựng (V) hay chưa
        if token not in inverted_index.keys():
            inverted_index[token] = [(tokens_id, 1)]
        else:
            # Kiểm tra xem tài liệu doc_idx đã có trong danh sách các tài liệu chỉ mục ngược của token này hay chưa
            is_existed = False
            for inverted_data_idx, (target_doc_idx, target_tf) in enumerate(inverted_index[token]):
                if target_doc_idx == tokens_id:
                    # Tăng tần số xuất hiện của token trong tài liệu (target_doc_idx) lên 1
                    target_tf+=1
                    # Cập nhật lại dữ liệu
                    inverted_index[token][inverted_data_idx] = (target_doc_idx, target_tf)
                    is_existed = True
                    break
            # Trường hợp chưa tồn tại
            if is_existed == False:
                inverted_index[token].append((tokens_id, 1))
            
            if tokens_id not in doc_idx_token_token_freq.keys():
                doc_idx_token_token_freq[tokens_id] = {}
                doc_idx_token_token_freq[tokens_id][token] = 1
            else:
                if token not in doc_idx_token_token_freq[tokens_id].keys():
                    doc_idx_token_token_freq[tokens_id][token] = 1
                else:
                    doc_idx_token_token_freq[tokens_id][token] += 1
    

    

    return inverted_index, doc_idx_token_token_freq                                                                 


def get_cleaned_query_request(query: str):
    # Tiền xử lý truy vấn
    query = query.strip().lower()
    # Tokenize và loại bỏ stopwords
    tokens = clean_text(query)
    return tokens

# def calculate_tf

read_articles()



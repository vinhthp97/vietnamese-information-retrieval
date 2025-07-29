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
    # đọc file orded-data.json
    with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'processed-data', 'ordered-data.json'), 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    # lăp qua từng đối tượng (bài viết đã được xử lý) trong danh sách articles
    for article in articles:
        doc_id = article['id']
        doc_tokens = article['tokens']
        
        # Tạo từ điển cho tần suất từ trong tài liệu
        token_freq = {}
        for token in doc_tokens:
            if token in tokens_id:
                token_freq[token] = token_freq.get(token, 0) + 1
        
        # Cập nhật chỉ mục ngược
        for token, freq in token_freq.items():
            if token not in tokens:
                tokens[token] = []
            tokens[token].append((doc_id, freq))

    

    return inverted_index, doc_idx_token_token_freq                                                                 


def get_cleaned_query_request(query: str):
    # Tiền xử lý truy vấn
    query = query.strip().lower()
    # Tokenize và loại bỏ stopwords
    tokens = clean_text(query)
    return tokens

# def calculate_tf

read_articles()



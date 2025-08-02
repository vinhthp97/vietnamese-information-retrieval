from underthesea import word_tokenize
import numpy as np
import os
import re
from collections import defaultdict
import math


def clean_text(text):  # xử lý văn bản, gồm tách từ, stopword, lower
    stopwords_path = os.path.join(os.path.dirname(
        __file__), '..', 'data', 'stopwords', 'vietnamese-stopwords.txt')
    with open(stopwords_path, 'r', encoding='utf-8') as f:
        stopwords = set(line.strip() for line in f if line.strip())
    clean_doc = re.sub('\W+', ' ', text)
    tokens = word_tokenize(clean_doc, format="text").lower().split()
    cleaned_tokens = [token for token in tokens if token not in stopwords]
    return cleaned_tokens


def load_articles():
    # Lấy đường dẫn của file hiện tại
    vnexpress_dir = os.path.join(os.path.dirname(
        __file__), '..', 'data', 'vnexpress')
    # Đường dẫn tương đối đến tệp bạn muốn truy cập
    data_dir = os.path.abspath(vnexpress_dir)
    articles = []
    id = 0
    for topic_folder in os.listdir(data_dir):
        topic_path = os.path.join(data_dir, topic_folder)
        if os.path.isdir(topic_path):  # check
            for file_name in os.listdir(topic_path):
                file_path = os.path.join(topic_path, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if lines:
                            title = lines[0].strip()
                            relative_path = os.path.relpath(file_path)
                            # Lấy toàn bộ nội dung trừ dòng đầu tiên
                            content = "".join(lines[1:]).strip()
                            # Xử lý lấy danh sách word token bằng clean_text
                            trimmed_content = content.strip()
                            cleaned_tokens = clean_text(content)
                            articles.append({
                                "id": id,
                                "title": title,
                                "topic": topic_folder,
                                "content": trimmed_content,
                                "path": relative_path,
                                "tokens": cleaned_tokens
                            })
                            id += 1
    ###########################################################
                except Exception as e:
                    print(f"lỗii {file_path}: {e}")
    return articles


def create_inverted_index(articles_data):
    """
    output của hàm ra 1 dict có key là từ; value là tập tài liệu xuất hiện từ đó, kiểu như này:
    {
      'báo_cáo': [0, 10, 33, 68, 75, 77, 82, 84, 100, 108, 109, 170, 177, 178, 180, 188],
      'bắt_đầu': [0, 7, 13, 15, 19, 29, 32, 33, 57, 61, 67, 78, 94, 112, 116, 121, 123, 127,...],
      từ_1: [docid_1,docid_9,docid_1000,...],
      ...
    }

    """

    inverted_index = defaultdict(list)
    for article in articles_data:
        doc_id = article['id']
        # set này để chống trùng lặp từ
        unique_tokens_in_doc = set(article['tokens'])
        for token in unique_tokens_in_doc:
            inverted_index[token].append(doc_id)
    return inverted_index


def calculate_idf(inverted_index, total_documents):
    """
    Tính toán IDF cho mỗi từ.

    Args:
        inverted_index: tập cmn.
        total_documents: là |D|.

    Returns:
        trả về dict với key là từ còn value là giá trị IDF của token đó.
    """
    idf_dict_local = {}
    for token, doc_ids in inverted_index.items():
        df = len(doc_ids)  # Document Frequency (DF) là số tài liệu chứa token
        # Công thức IDF: log(N / df)
        idf_dict_local[token] = round(math.log(total_documents / df), 5)

    return idf_dict_local


def calculate_tfidf(D, idf_values):
    """
   tập các vector TF-IDF cho mỗi tài liệu (d).

    Args:
        D: D
        idf_values: dict chứa giá trị IDF của các từ.

    Returns:
        dict chứa các vector TF-IDF: key = id tài liệu, value = vector tfidf của tài liệu đó
        với return thứ 2 là một dict có chức năg ánh xạ từ sang index từ.
    """
    vocab = list(idf_values.keys())  # tập từ vựng
    # tập từ vựng có ánh xạ id
    token_to_idx = {token: i for i, token in enumerate(vocab)}

    doc_vectors = {}

    for article in D:
        doc_id = article['id']
        tokens = article['tokens']

        tf_dict = defaultdict(int)
        for token in tokens:
            tf_dict[token] += 1

        max_freq = max(tf_dict.values()) if tf_dict else 1
        for token in tf_dict:
            tf_dict[token] = tf_dict[token] / max_freq

############################################################################################

        vector = np.zeros(len(vocab))
        for token, tf in tf_dict.items():
            if token in token_to_idx:
                idx = token_to_idx[token]
                idf = idf_values[token]
                vector[idx] = round((tf * idf), 5)

        # lưu vector đã tính vào ma trận với key là doc id hiện tại và value là vector tfidf đã tính
        doc_vectors[doc_id] = vector

    return doc_vectors, token_to_idx


def vectorize_query(query, token_to_idx, idf_values):
    """
    chuyển đổi q thành vector TF-IDF.
    """

    cleaned_tokens = clean_text(query)

    tf_dict_now = defaultdict(int)
    for token in cleaned_tokens:
        tf_dict_now[token] += 1

    max_freq = max(tf_dict_now.values()) if tf_dict_now else 1
    for token in tf_dict_now:
        tf_dict_now[token] = round((tf_dict_now[token] / max_freq), 5)

    query_vector = np.zeros(len(token_to_idx))
    for token, tf in tf_dict_now.items():
        if token in token_to_idx:
            idx = token_to_idx[token]
            # lấy IDF, nếu mà chưa có trong tập đã tính thì mình cho IDF=0
            idf = idf_values.get(token, 0)
            query_vector[idx] = round((tf * idf), 5)

    return query_vector


def my_cosine_similarity(vec1, vec2):

    tich_vo_huong = np.dot(vec1, vec2)  # ngày mai bỏ cái này luôn

    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)

    if norm_vec1 == 0 or norm_vec2 == 0:  # cái nào có giá trị 0 thì khỏi tính - hog có chia cho 0
        return 0.0

    return tich_vo_huong / (norm_vec1 * norm_vec2)


def search_optimized(query, inverted_index, tfidf_vectors, token_to_idx, idf_values, articles_data, top_n=5):
    """
    Thực hiện tìm kiếm tối ưu bằng cách sử dụng chỉ mục ngược để lọc tài liệu ứng viên.
    """

    query_vector = vectorize_query(query, token_to_idx, idf_values)

    # tìm danh sách ứng viên từ chỉ mục ngược
    query_tokens = clean_text(query)
    candidate_docs = set()
    for token in query_tokens:
        if token in inverted_index:  # nếu mà nó có trong tập CMN thì...
            # ...thêm cái danh sách ứng viên (các tài liệu chứa token đang xét) vào tập ứng viên
            candidate_docs.update(inverted_index[token])

    if not candidate_docs:
        return

    # chỉ tính toán trên các tập ứng viên
    candidate_vectors = {doc_id: tfidf_vectors[doc_id]
                         for doc_id in candidate_docs if doc_id in tfidf_vectors}

    similarities = {}
    for doc_id, doc_vector in candidate_vectors.items():

        similarities[doc_id] = my_cosine_similarity(query_vector, doc_vector)

    # ################
    sorted_docs = sorted(similarities.items(),
                         key=lambda item: item[1], reverse=True)

    return sorted_docs[:top_n]  # trả về top N kết quả

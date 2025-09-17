import json
import pathlib
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask import request
import os
from google import genai
from google.genai import types

app = Flask(__name__)
load_dotenv()

@app.route('/hello', methods=['GET'])
def hello_world():
    return jsonify({'message': 'hello world'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    inp = data.get('prompt', '')
    if not inp or not str(inp).strip():
        return jsonify({'text': 'No prompt provided'}), 400
    
    client = genai.Client()
    model="gemini-2.5-flash"

    # Bước 1: Đọc file JSON để lấy mục lục
    table_content = {}
    with open('assets/table_content.json', 'r', encoding='utf-8') as file:
        table_content = file.read()
    list_page=[]
    # try:
    response = client.models.generate_content(
        model=model,
        contents=[
            'Dựa vào câu hỏi của người dùng và mục lục của cuốn Sổ tay sinh viên K65 - 2024, hãy trả về các trang bạn cần để lấy thông tin dưới dạng json mà không có lời dẫn gì thêm. Số lượng trang phải ít nhất có thể. Json bạn trả về cần có định dạng như sau: {"pages":[1,2,4,...]}. Nếu câu hỏi không liên quan, trả về {"pages":[0]}. Nếu bạn không cần bất cứ thông tin nào trong file, trả về {"pages":[]}',
            f"Câu hỏi của người dùng: {inp}",
            f"Mục lục: {table_content}"
        ]
    )
    print(response.text)
    if response.usage_metadata:
        input_tokens = response.usage_metadata.prompt_token_count
        output_tokens = response.usage_metadata.candidates_token_count
        total_tokens = response.usage_metadata.total_token_count
        
        print(f"Số token của prompt: {input_tokens}")
        print(f"Số token của response: {output_tokens}")
        print(f"Tổng số token: {total_tokens}")
    
    list_page = json.loads(response.text).get("pages",[])
    if list_page[0]==0:
        return jsonify({'text': 'Xin lỗi, chúng tôi không tìm thấy câu trả lời của cho câu hỏi của bạn trong tài liệu này'})

    contents=[]
    for page in list_page:
        filepath = pathlib.Path(f'assets/sotaysinhvien/Sổ tay sinh viên K65 - 2024_compressed-{page}.pdf')
        contents.append(
            types.Part.from_bytes(
                data=filepath.read_bytes(),
                mime_type='application/pdf',
            )
        )
    contents.append(f"danh sách số trang theo thứ tự file: {json.dumps(list_page)}")
# Nội dung câu trả lời hoàn chỉnh được tách thành các phần nhỏ mà mỗi phần nhỏ này nằm trong các page khác nhau. 
    contents.append(
    f"""
        Dựa vào tất cả các file trên đây, hãy trả lời câu hỏi của người dùng ngắn gọn nhất có thể, càng ngắn càng tốt, khoảng 100 đến 200 từ.
        Trả về dưới dạng nội dung markdown đính kèm với số trang tương ứng, ví dụ:
        Đây là nội dung 1 <ScorllButton page="10"/> và nội dung 2 <ScorllButton page="13"/> cho câu trả lời
        Câu hỏi người dùng có nội dung như sau: {inp}
    """)
    response = client.models.generate_content(
        model=model,
        contents=contents
    )
    if response.usage_metadata:
        input_tokens = response.usage_metadata.prompt_token_count
        output_tokens = response.usage_metadata.candidates_token_count
        total_tokens = response.usage_metadata.total_token_count
        
        print(f"Số token của prompt: {input_tokens}")
        print(f"Số token của response: {output_tokens}")
        print(f"Tổng số token: {total_tokens}")
    print(response.text)
    return jsonify({'text': response.text})
    # except Exception as e:
    #     return jsonify({'text': f'Xin lỗi, đã có lỗi xảy ra {e}'}),500

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    app.run(debug=True)
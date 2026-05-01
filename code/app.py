from flask import Flask, render_template, request, send_file
import os
from dbfread import DBF
import pandas as pd
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 最大上传50MB

ALLOWED_EXTENSIONS = {'dbf'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert_dbf_to_excel():
    if 'file' not in request.files:
        return '没有选择文件', 400
    
    file = request.files['file']
    
    if file.filename == '':
        return '没有选择文件', 400
    
    if not allowed_file(file.filename):
        return '只支持DBF文件格式', 400
    
    try:
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())[:8]
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{filename}")
        
        file.save(input_path)
        
        output_filename = filename.rsplit('.', 1)[0] + '.xlsx'
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{unique_id}_{output_filename}")
        
        table = DBF(input_path, encoding='gbk')
        df = pd.DataFrame(iter(table))
        df.to_excel(output_path, index=False)
        
        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    except Exception as e:
        return f'转换失败: {str(e)}', 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

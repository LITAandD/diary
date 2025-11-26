from flask import Flask, render_template_string, request, redirect, url_for
from datetime import datetime
import os
import json
import base64

app = Flask(__name__)
DIARY_FILE = "flask_diary.json"
UPLOAD_FOLDER = "diary_photos"

# 사진 폴더 생성
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# HTML 템플릿
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📔 나의 일기장</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Malgun Gothic', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .tabs {
            display: flex;
            background: #f5f5f5;
        }
        
        .tab {
            flex: 1;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            border: none;
            background: #f5f5f5;
            font-size: 16px;
            transition: all 0.3s;
        }
        
        .tab:hover {
            background: #e0e0e0;
        }
        
        .tab.active {
            background: white;
            border-bottom: 3px solid #667eea;
            font-weight: bold;
        }
        
        .content {
            padding: 30px;
            max-height: 70vh;
            overflow-y: auto;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #333;
        }
        
        input[type="date"],
        input[type="file"],
        textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 16px;
            transition: border 0.3s;
        }
        
        input[type="date"]:focus,
        input[type="file"]:focus,
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        textarea {
            resize: vertical;
            min-height: 150px;
            font-family: 'Malgun Gothic', sans-serif;
        }
        
        .photo-preview {
            margin-top: 10px;
            display: none;
        }
        
        .photo-preview img {
            max-width: 100%;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .photo-preview-text {
            margin-top: 10px;
            color: #667eea;
            font-size: 14px;
        }
        
        .btn {
            padding: 12px 20px;
            border: none;
            border-radius: 10px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            margin: 5px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            width: 100%;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-edit {
            background: #FF9800;
            color: white;
        }
        
        .btn-edit:hover {
            background: #F57C00;
        }
        
        .btn-delete {
            background: #f44336;
            color: white;
        }
        
        .btn-delete:hover {
            background: #d32f2f;
        }
        
        .btn-cancel {
            background: #9E9E9E;
            color: white;
        }
        
        .btn-cancel:hover {
            background: #757575;
        }
        
        .btn-success {
            background: #4CAF50;
            color: white;
            width: 100%;
        }
        
        .btn-info {
            background: #2196F3;
            color: white;
            width: 100%;
        }
        
        .diary-entry {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }
        
        .diary-entry h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .diary-photo {
            margin: 15px 0;
            text-align: center;
        }
        
        .diary-photo img {
            max-width: 100%;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            cursor: pointer;
            transition: transform 0.3s;
        }
        
        .diary-photo img:hover {
            transform: scale(1.02);
        }
        
        .diary-entry p {
            color: #555;
            line-height: 1.6;
            margin-bottom: 15px;
            white-space: pre-wrap;
        }
        
        .diary-actions {
            display: flex;
            gap: 10px;
        }
        
        .alert {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        .alert-warning {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #999;
        }
        
        .empty-state .emoji {
            font-size: 4em;
            margin-bottom: 20px;
        }
        
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            overflow-y: auto;
        }
        
        .modal.active {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 15px;
            max-width: 500px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
        }
        
        .modal-content h3 {
            margin-bottom: 20px;
            color: #333;
            text-align: center;
        }
        
        .modal-actions {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        
        .image-modal {
            background: rgba(0,0,0,0.9);
        }
        
        .image-modal .modal-content {
            background: transparent;
            max-width: 90%;
            max-height: 90%;
            padding: 0;
        }
        
        .image-modal img {
            width: 100%;
            height: auto;
            border-radius: 10px;
        }
        
        .close-image {
            position: absolute;
            top: 20px;
            right: 20px;
            color: white;
            font-size: 30px;
            cursor: pointer;
            background: rgba(0,0,0,0.5);
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 1.5em;
            }
            
            .content {
                padding: 20px;
            }
            
            .tab {
                font-size: 14px;
                padding: 12px 5px;
            }
            
            .diary-actions {
                flex-direction: column;
            }
            
            .btn {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📔 나의 일기장</h1>
            <p>오늘 하루를 기록해보세요</p>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="openTab(event, 'write')">✍️ 쓰기</button>
            <button class="tab" onclick="openTab(event, 'view')">📚 보기</button>
            <button class="tab" onclick="openTab(event, 'search')">🔍 검색</button>
        </div>
        
        <div class="content">
            {% if message %}
            <div class="alert alert-{{ message_type }}">
                {{ message }}
            </div>
            {% endif %}
            
            <!-- 일기 쓰기 탭 -->
            <div id="write" class="tab-content active">
                <form method="POST" action="/save" enctype="multipart/form-data">
                    <div class="form-group">
                        <label>📅 날짜</label>
                        <input type="date" name="date" value="{{ today }}" required>
                    </div>
                    
                    <div class="form-group">
                        <label>📸 사진 (선택)</label>
                        <input type="file" name="photo" accept="image/*" onchange="previewPhoto(event)" capture="environment">
                        <div class="photo-preview" id="photoPreview">
                            <img id="previewImg" src="" alt="미리보기">
                            <p class="photo-preview-text">✅ 사진이 선택되었습니다</p>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>✍️ 오늘 있었던 일</label>
                        <textarea name="content" placeholder="오늘 하루는 어땠나요? 자유롭게 적어보세요..." required></textarea>
                    </div>
                    
                    <button type="submit" class="btn btn-primary">💾 저장하기</button>
                </form>
            </div>
            
            <!-- 모든 일기 보기 탭 -->
            <div id="view" class="tab-content">
                <h2 style="margin-bottom: 20px;">📖 모든 일기</h2>
                
                {% if entries %}
                    <p style="color: #666; margin-bottom: 20px;">총 {{ entries|length }}개의 일기</p>
                    {% for entry in entries %}
                    <div class="diary-entry">
                        <h3>📅 {{ entry.date }}</h3>
                        {% if entry.photo %}
                        <div class="diary-photo">
                            <img src="data:image/jpeg;base64,{{ entry.photo }}" alt="일기 사진" onclick="showImage(this.src)">
                        </div>
                        {% endif %}
                        <p>{{ entry.content }}</p>
                        <div class="diary-actions">
                            <button class="btn btn-edit" onclick="editDiary('{{ entry.id }}', '{{ entry.date }}', `{{ entry.content|replace('\n', '\\n')|replace('`', '\\`') }}`, '{{ entry.photo or '' }}')">✏️ 수정</button>
                            <button class="btn btn-delete" onclick="showDeleteModal('{{ entry.id }}', '{{ entry.date }}')">🗑️ 삭제</button>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="empty-state">
                        <div class="emoji">📭</div>
                        <p>아직 작성된 일기가 없습니다.<br>첫 일기를 작성해보세요!</p>
                    </div>
                {% endif %}
            </div>
            
            <!-- 검색 탭 -->
            <div id="search" class="tab-content">
                <form method="POST" action="/search">
                    <div class="form-group">
                        <label>🔍 날짜로 검색</label>
                        <input type="date" name="search_date" required>
                    </div>
                    <button type="submit" class="btn btn-info">검색하기</button>
                </form>
                
                {% if search_result %}
                    {% if search_result.found %}
                    <div style="margin-top: 30px;">
                        <div class="alert alert-success">✅ 일기를 찾았습니다!</div>
                        <div class="diary-entry">
                            <h3>📅 {{ search_result.date }}</h3>
                            {% if search_result.photo %}
                            <div class="diary-photo">
                                <img src="data:image/jpeg;base64,{{ search_result.photo }}" alt="일기 사진" onclick="showImage(this.src)">
                            </div>
                            {% endif %}
                            <p>{{ search_result.content }}</p>
                            <div class="diary-actions">
                                <button class="btn btn-edit" onclick="editDiary('{{ search_result.id }}', '{{ search_result.date }}', `{{ search_result.content|replace('\n', '\\n')|replace('`', '\\`') }}`, '{{ search_result.photo or '' }}')">✏️ 수정</button>
                                <button class="btn btn-delete" onclick="showDeleteModal('{{ search_result.id }}', '{{ search_result.date }}')">🗑️ 삭제</button>
                            </div>
                        </div>
                    </div>
                    {% else %}
                    <div style="margin-top: 30px;">
                        <div class="alert alert-info">❌ 해당 날짜의 일기를 찾을 수 없습니다.</div>
                    </div>
                    {% endif %}
                {% endif %}
            </div>
        </div>
    </div>
    
    <!-- 수정 모달 -->
    <div id="editModal" class="modal">
        <div class="modal-content">
            <h3>✏️ 일기 수정하기</h3>
            <form method="POST" action="/edit" enctype="multipart/form-data" id="editForm">
                <input type="hidden" name="diary_id" id="edit_id">
                <input type="hidden" name="existing_photo" id="existing_photo">
                <div class="form-group" style="text-align: left;">
                    <label>📅 날짜</label>
                    <input type="date" name="date" id="edit_date" required>
                </div>
                <div class="form-group" style="text-align: left;">
                    <label>📸 사진 변경 (선택)</label>
                    <input type="file" name="photo" accept="image/*" onchange="previewEditPhoto(event)">
                    <div id="editPhotoPreview" style="margin-top: 10px;"></div>
                </div>
                <div class="form-group" style="text-align: left;">
                    <label>✍️ 내용</label>
                    <textarea name="content" id="edit_content" required style="min-height: 200px;"></textarea>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-cancel" onclick="closeEditModal()" style="flex: 1;">취소</button>
                    <button type="submit" class="btn btn-success" style="flex: 1;">저장</button>
                </div>
            </form>
        </div>
    </div>
    
    <!-- 삭제 확인 모달 -->
    <div id="deleteModal" class="modal">
        <div class="modal-content">
            <h3>🗑️ 일기 삭제</h3>
            <p id="deleteMessage">정말 이 일기를 삭제하시겠어요?</p>
            <div class="alert alert-warning" style="margin-top: 15px;">
                ⚠️ 삭제하면 복구할 수 없습니다!
            </div>
            <form method="POST" action="/delete" id="deleteForm">
                <input type="hidden" name="diary_id" id="delete_id">
                <div class="modal-actions">
                    <button type="button" class="btn btn-cancel" onclick="closeDeleteModal()" style="flex: 1;">취소</button>
                    <button type="submit" class="btn btn-delete" style="flex: 1;">삭제</button>
                </div>
            </form>
        </div>
    </div>
    
    <!-- 이미지 확대 모달 -->
    <div id="imageModal" class="modal image-modal">
        <span class="close-image" onclick="closeImageModal()">&times;</span>
        <div class="modal-content">
            <img id="modalImage" src="" alt="확대 이미지">
        </div>
    </div>
    
    <script>
        function openTab(evt, tabName) {
            var i, tabContent, tabs;
            
            tabContent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabContent.length; i++) {
                tabContent[i].classList.remove("active");
            }
            
            tabs = document.getElementsByClassName("tab");
            for (i = 0; i < tabs.length; i++) {
                tabs[i].classList.remove("active");
            }
            
            document.getElementById(tabName).classList.add("active");
            evt.currentTarget.classList.add("active");
        }
        
        function previewPhoto(event) {
            const preview = document.getElementById('photoPreview');
            const previewImg = document.getElementById('previewImg');
            const file = event.target.files[0];
            
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImg.src = e.target.result;
                    preview.style.display = 'block';
                }
                reader.readAsDataURL(file);
            }
        }
        
        function previewEditPhoto(event) {
            const preview = document.getElementById('editPhotoPreview');
            const file = event.target.files[0];
            
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.innerHTML = '<img src="' + e.target.result + '" style="max-width: 100%; border-radius: 10px; margin-top: 10px;">';
                }
                reader.readAsDataURL(file);
            }
        }
        
        function editDiary(id, date, content, photo) {
            document.getElementById('edit_id').value = id;
            document.getElementById('edit_date').value = date;
            document.getElementById('edit_content').value = content;
            document.getElementById('existing_photo').value = photo;
            
            const preview = document.getElementById('editPhotoPreview');
            if (photo) {
                preview.innerHTML = '<img src="data:image/jpeg;base64,' + photo + '" style="max-width: 100%; border-radius: 10px;"><p style="color: #666; font-size: 14px; margin-top: 5px;">기존 사진 (새 사진을 선택하면 교체됩니다)</p>';
            } else {
                preview.innerHTML = '';
            }
            
            document.getElementById('editModal').classList.add('active');
        }
        
        function closeEditModal() {
            document.getElementById('editModal').classList.remove('active');
        }
        
        function showDeleteModal(id, date) {
            document.getElementById('delete_id').value = id;
            document.getElementById('deleteMessage').textContent = date + '의 일기를 삭제하시겠어요?';
            document.getElementById('deleteModal').classList.add('active');
        }
        
        function closeDeleteModal() {
            document.getElementById('deleteModal').classList.remove('active');
        }
        
        function showImage(src) {
            document.getElementById('modalImage').src = src;
            document.getElementById('imageModal').classList.add('active');
        }
        
        function closeImageModal() {
            document.getElementById('imageModal').classList.remove('active');
        }
        
        // 모달 바깥 클릭시 닫기
        window.onclick = function(event) {
            if (event.target.classList.contains('modal')) {
                event.target.classList.remove('active');
            }
        }
    </script>
</body>
</html>
"""

def read_diaries():
    """모든 일기 읽기"""
    if not os.path.exists(DIARY_FILE):
        return []
    
    try:
        with open(DIARY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return sorted(data, key=lambda x: x['date'], reverse=True)
    except:
        return []

def save_diaries(entries):
    """일기 저장"""
    with open(DIARY_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

def save_photo(photo_file):
    """사진을 base64로 변환"""
    if photo_file and photo_file.filename:
        return base64.b64encode(photo_file.read()).decode('utf-8')
    return None

@app.route('/')
def index():
    today = datetime.now().strftime('%Y-%m-%d')
    entries = read_diaries()
    return render_template_string(HTML_TEMPLATE, today=today, entries=entries)

@app.route('/save', methods=['POST'])
def save():
    date = request.form.get('date')
    content = request.form.get('content')
    photo = request.files.get('photo')
    
    entries = read_diaries()
    new_entry = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'date': date,
        'content': content,
        'photo': save_photo(photo)
    }
    entries.append(new_entry)
    save_diaries(entries)
    
    today = datetime.now().strftime('%Y-%m-%d')
    entries = read_diaries()
    return render_template_string(HTML_TEMPLATE, 
                                 today=today, 
                                 entries=entries,
                                 message=f'✅ {date}의 일기가 저장되었습니다!',
                                 message_type='success')

@app.route('/edit', methods=['POST'])
def edit():
    diary_id = request.form.get('diary_id')
    date = request.form.get('date')
    content = request.form.get('content')
    photo = request.files.get('photo')
    existing_photo = request.form.get('existing_photo')
    
    entries = read_diaries()
    for entry in entries:
        if entry['id'] == diary_id:
            entry['date'] = date
            entry['content'] = content
            # 새 사진이 있으면 교체, 없으면 기존 사진 유지
            new_photo = save_photo(photo)
            if new_photo:
                entry['photo'] = new_photo
            elif existing_photo:
                entry['photo'] = existing_photo
            break
    
    save_diaries(entries)
    
    today = datetime.now().strftime('%Y-%m-%d')
    entries = read_diaries()
    return render_template_string(HTML_TEMPLATE, 
                                 today=today, 
                                 entries=entries,
                                 message='✅ 일기가 수정되었습니다!',
                                 message_type='success')

@app.route('/delete', methods=['POST'])
def delete():
    diary_id = request.form.get('diary_id')
    
    entries = read_diaries()
    entries = [e for e in entries if e['id'] != diary_id]
    save_diaries(entries)
    
    today = datetime.now().strftime('%Y-%m-%d')
    entries = read_diaries()
    return render_template_string(HTML_TEMPLATE, 
                                 today=today, 
                                 entries=entries,
                                 message='✅ 일기가 삭제되었습니다!',
                                 message_type='success')

@app.route('/search', methods=['POST'])
def search():
    search_date = request.form.get('search_date')
    entries = read_diaries()
    
    result = {'found': False}
    for entry in entries:
        if entry['date'] == search_date:
            result = {
                'found': True,
                'id': entry['id'],
                'date': entry['date'],
                'content': entry['content'],
                'photo': entry.get('photo')
            }
            break
    
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template_string(HTML_TEMPLATE, 
                                 today=today, 
                                 entries=entries,
                                 search_result=result)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("📔 일기 앱이 실행되었습니다!")
    print("="*50)
    print("\n컴퓨터에서 접속: http://localhost:5000")
    print("\n📱 휴대폰에서 접속:")
    print("1. 컴퓨터와 같은 WiFi에 연결")
    print("2. 아래 주소 중 하나를 휴대폰 브라우저에 입력:")
    print("   http://192.168.0.XXX:5000")
    print("   (XXX는 실행 후 나오는 주소를 확인하세요)")
    print("\n✨ 새 기능:")
    print("   - 수정/삭제 가능!")
    print("   - 📸 사진 첨부 가능!")
    print("   - 사진 클릭하면 확대!")
    print("\n종료하려면 Ctrl+C를 누르세요")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
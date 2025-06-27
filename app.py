from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 用于会话加密

# 后端API配置
API_BASE_URL = "http://localhost:8000/api/v1"

@app.route('/')
def home():
    """首页 - 显示视频列表（带分页）"""
    try:
        # 获取分页参数，默认为第1页，每页6条
        page = request.args.get('page', 1, type=int)
        per_page = 6
        offset = (page - 1) * per_page
        
        # 调用API获取视频列表
        response = requests.get(
            f"{API_BASE_URL}/videos",
            params={'limit': per_page, 'offset': offset}
        )
        
        if response.status_code != 200:
            flash("无法获取视频列表，请稍后再试", "danger")
            return render_template('index.html', videos=[], pagination=None)
        
        data = response.json()
        videos = data.get('videos', [])
        total_videos = data.get('total', 0)
        
        # 计算分页信息
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total_videos,
            'pages': (total_videos + per_page - 1) // per_page
        }
        
        return render_template('index.html', videos=videos, pagination=pagination)
    except requests.exceptions.RequestException as e:
        flash("获取视频列表失败，请检查网络连接", "danger")
        return render_template('index.html', videos=[], pagination=None)

@app.route('/video/<int:video_id>')
def video_detail(video_id):
    """视频详情页 - 显示视频播放器和评论"""
    try:
        # 获取视频详情
        video_response = requests.get(f"{API_BASE_URL}/videos/{video_id}")
        if video_response.status_code != 200:
            flash("视频不存在或无法访问", "danger")
            return redirect(url_for('home'))
        
        video_data = video_response.json()
        
        # 确保sources是列表且不为空
        sources = video_data.get('sources', [])
        if not sources:
            flash("视频源不可用", "warning")
            return redirect(url_for('home'))
        
        # 获取评论
        try:
            comments_response = requests.get(f"{API_BASE_URL}/videos/{video_id}/comments")
            comments = comments_response.json() if comments_response.status_code == 200 else []
        except:
            comments = []
        
        return render_template('video_detail.html', 
                             video=video_data['video'], 
                             sources=sources,
                             comments=comments or [])
    except requests.exceptions.RequestException as e:
        flash("获取视频信息失败", "danger")
        return redirect(url_for('home'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_video():
    """视频上传页面"""
    if 'token' not in session:
        flash("请先登录", "warning")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # 处理文件上传
        if 'video_file' not in request.files:
            flash("未选择文件", "danger")
            return redirect(request.url)
        
        file = request.files['video_file']
        if file.filename == '':
            flash("未选择文件", "danger")
            return redirect(request.url)
        
        if file:
            # 1. 申请预签名URL
            headers = {
                "Authorization": f"Bearer {session['token']}",
                "Content-Type": "application/json"
            }
            data = {
                "file_name": file.filename,
                "title": request.form.get('title', file.filename),
                "description": request.form.get('description', '')
            }
            
            try:
                # 初始化上传
                initiate_response = requests.post(
                    f"{API_BASE_URL}/videos/upload/initiate",
                    headers=headers,
                    json=data
                )
                
                if initiate_response.status_code != 200:
                    flash("上传初始化失败", "danger")
                    return redirect(request.url)
                
                upload_data = initiate_response.json()
                upload_url = upload_data['upload_url']
                video_id = upload_data['video_id']
                
                # 2. 直接上传到MinIO
                with file.stream as file_stream:
                    upload_response = requests.put(
                        upload_url,
                        data=file_stream,
                        headers={"Content-Type": "application/octet-stream"}
                    )
                
                if upload_response.status_code != 200:
                    flash("文件上传失败", "danger")
                    return redirect(request.url)
                
                # 3. 通知上传完成
                complete_response = requests.post(
                    f"{API_BASE_URL}/videos/upload/complete",
                    headers=headers,
                    json={"video_id": video_id}
                )
                
                if complete_response.status_code == 200:
                    flash("视频上传成功，正在转码处理中", "success")
                    return redirect(url_for('video_detail', video_id=video_id))
                else:
                    flash("转码任务提交失败", "warning")
                    return redirect(url_for('video_detail', video_id=video_id))
                    
            except requests.exceptions.RequestException as e:
                flash(f"上传过程中出错: {str(e)}", "danger")
                return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/comment/<int:video_id>', methods=['POST'])
def add_comment(video_id):
    """添加评论或弹幕"""
    if 'token' not in session:
        flash("请先登录", "warning")
        return redirect(url_for('login'))
    
    content = request.form.get('content')
    timeline = request.form.get('timeline', type=int)
    
    if not content:
        flash("内容不能为空", "danger")
        return redirect(url_for('video_detail', video_id=video_id))
    
    try:
        headers = {
            "Authorization": f"Bearer {session['token']}",
            "Content-Type": "application/json"
        }
        
        # 构建请求体
        data = {"content": content}
        if timeline is not None and timeline >= 0:
            data["timeline"] = timeline
        
        response = requests.post(
            f"{API_BASE_URL}/videos/{video_id}/comments",
            headers=headers,
            json=data
        )
        
        if response.status_code == 201:
            flash("发表成功", "success")
        else:
            error_msg = response.json().get('message', '发表失败')
            flash(error_msg, "danger")
    except requests.exceptions.RequestException as e:
        flash(f"网络错误: {str(e)}", "danger")
    
    return redirect(url_for('video_detail', video_id=video_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/users/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                session['token'] = data['token']
                session['user_id'] = data['user_id']
                session['nickname'] = data['nickname']
                flash("登录成功", "success")
                return redirect(url_for('home'))
            else:
                flash("邮箱或密码错误", "danger")
        except requests.exceptions.RequestException:
            flash("登录服务暂时不可用", "danger")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/users/register",
                json={
                    "nickname": nickname,
                    "email": email,
                    "password": password
                }
            )
            
            if response.status_code == 201:
                flash("注册成功，请登录", "success")
                return redirect(url_for('login'))
            else:
                error_msg = response.json().get('message', '注册失败')
                flash(error_msg, "danger")
        except requests.exceptions.RequestException:
            flash("注册服务暂时不可用", "danger")
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """用户登出"""
    session.clear()
    flash("您已成功登出", "success")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash
from datetime import datetime
import hmac
import hashlib
import json
import os
from pathlib import Path
import math
import threading
import queue

# 导入配置
from config import config

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()  # 加载.env文件
except ImportError:
    # 如果没有安装python-dotenv，忽略
    pass

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# 从配置文件获取配置
ADMIN_USERNAME = config.ADMIN_USERNAME
ADMIN_PASSWORD_HASH = config.ADMIN_PASSWORD_HASH

# 文件存储配置
DATA_DIR = config.DATA_DIR
MESSAGES_FILE = config.MESSAGES_FILE
SETTINGS_FILE = config.SETTINGS_FILE
ARCHIVE_DIR = config.ARCHIVE_DIR

# 存储配置
MAX_MESSAGES_PER_FILE = config.MAX_MESSAGES_PER_FILE
MAX_ACTIVE_MESSAGES = config.MAX_ACTIVE_MESSAGES
PAGE_SIZE = config.PAGE_SIZE

# 确保数据目录存在
config.ensure_directories()

# 默认设置
DEFAULT_SETTINGS = config.DEFAULT_SETTINGS

def load_messages():
    """从文件加载消息"""
    try:
        if MESSAGES_FILE.exists():
            with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"加载消息失败: {e}")
    return []

def archive_old_messages():
    """归档旧消息到时间文件夹"""
    global webhook_messages
    
    try:
        if len(webhook_messages) <= MAX_ACTIVE_MESSAGES:
            return True
        
        # 计算需要归档的消息数量
        archive_count = len(webhook_messages) - MAX_ACTIVE_MESSAGES
        
        # 获取需要归档的消息（最旧的消息）
        messages_to_archive = webhook_messages[-archive_count:]
        
        # 按时间分组归档
        archive_groups = {}
        for msg in messages_to_archive:
            timestamp = datetime.strptime(msg['timestamp'], '%Y-%m-%d %H:%M:%S')
            date_key = timestamp.strftime('%Y-%m-%d')
            
            if date_key not in archive_groups:
                archive_groups[date_key] = []
            archive_groups[date_key].append(msg)
        
        # 保存归档文件
        for date_key, messages in archive_groups.items():
            archive_file = ARCHIVE_DIR / f'messages_{date_key}.json'
            
            # 如果文件已存在，合并消息
            existing_messages = []
            if archive_file.exists():
                with open(archive_file, 'r', encoding='utf-8') as f:
                    existing_messages = json.load(f)
            
            # 合并并按ID去重
            all_messages = existing_messages + messages
            unique_messages = {}
            for msg in all_messages:
                unique_messages[msg['id']] = msg
            
            # 按时间排序
            sorted_messages = sorted(unique_messages.values(), 
                                   key=lambda x: x['timestamp'], reverse=True)
            
            with open(archive_file, 'w', encoding='utf-8') as f:
                json.dump(sorted_messages, f, ensure_ascii=False, indent=2)
        
        # 从活跃消息中移除已归档的消息
        webhook_messages = webhook_messages[:-archive_count]
        
        print(f"已归档 {archive_count} 条消息")
        return True
        
    except Exception as e:
        print(f"归档消息失败: {e}")
        return False

def get_next_message_id():
    """获取下一个消息ID，考虑所有消息（包括归档的）"""
    max_id = 0
    
    # 1. 检查内存中的活跃消息
    if webhook_messages:
        max_id = max(max_id, max(msg.get('id', 0) for msg in webhook_messages))
    
    # 2. 检查所有归档文件中的消息
    try:
        archived_files = get_archived_files()
        for archive_info in archived_files:
            try:
                with open(archive_info['file'], 'r', encoding='utf-8') as f:
                    archived_messages = json.load(f)
                    if archived_messages:
                        max_id = max(max_id, max(msg.get('id', 0) for msg in archived_messages))
            except Exception as e:
                print(f"读取归档文件 {archive_info['file']} 失败: {e}")
    except Exception as e:
        print(f"检查归档文件失败: {e}")
    
    return max_id + 1
    """获取所有归档文件列表"""
    try:
        archive_files = []
        for file_path in ARCHIVE_DIR.glob('messages_*.json'):
            date_str = file_path.stem.replace('messages_', '')
            archive_files.append({
                'date': date_str,
                'file': str(file_path),
                'size': file_path.stat().st_size
            })
        return sorted(archive_files, key=lambda x: x['date'], reverse=True)
    except Exception as e:
        print(f"获取归档文件失败: {e}")
        return []

def get_paginated_messages(page=1, page_size=PAGE_SIZE, include_archived=False):
    """获取分页消息"""
    global webhook_messages
    
    try:
        all_messages = webhook_messages.copy()
        
        # 如果需要包含归档消息
        if include_archived:
            archived_files = get_archived_files()
            for archive_info in archived_files:
                try:
                    with open(archive_info['file'], 'r', encoding='utf-8') as f:
                        archived_messages = json.load(f)
                        all_messages.extend(archived_messages)
                except Exception as e:
                    print(f"读取归档文件失败: {e}")
        
        # 按时间排序（最新的在前）
        all_messages.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # 分页计算
        total_messages = len(all_messages)
        total_pages = math.ceil(total_messages / page_size)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        page_messages = all_messages[start_index:end_index]
        
        return {
            'messages': page_messages,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_messages': total_messages,
                'page_size': page_size,
                'has_prev': page > 1,
                'has_next': page < total_pages
            }
        }
        
    except Exception as e:
        print(f"获取分页消息失败: {e}")
        return {
            'messages': [],
            'pagination': {
                'current_page': 1,
                'total_pages': 1,
                'total_messages': 0,
                'page_size': page_size,
                'has_prev': False,
                'has_next': False
            }
        }

def save_messages(messages):
    """保存消息到文件，并自动归档"""
    try:
        # 先归档旧消息
        archive_old_messages()
        
        # 保存当前活跃消息
        with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存消息失败: {e}")
        return False

def load_settings():
    """从文件加载设置"""
    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # 确保所有必需的键都存在
                for key, value in DEFAULT_SETTINGS.items():
                    if key not in settings:
                        settings[key] = value
                return settings
    except Exception as e:
        print(f"加载设置失败: {e}")
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """保存设置到文件"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存设置失败: {e}")
        return False

# 加载数据
webhook_messages = load_messages()
webhook_settings = load_settings()

# 实时推送队列
message_queue = queue.Queue()
active_connections = set()  # 存储活跃的SSE连接

def broadcast_new_message(message):
    """广播新消息给所有连接的客户端"""
    try:
        # 将消息放入队列
        message_data = {
            'type': 'new_message',
            'data': message
        }
        message_queue.put(json.dumps(message_data))
        print(f"广播新消息: ID {message['id']}")
    except Exception as e:
        print(f"广播消息失败: {e}")

def verify_webhook_signature(payload, signature, secret):
    """验证Webhook签名"""
    if not signature:
        return False
    
    expected_signature = hmac.new(
        secret.encode('utf-8'), 
        payload, 
        hashlib.sha256
    ).hexdigest()
    
    # 支持GitHub风格的签名格式 sha256=xxxxx
    if signature.startswith('sha256='):
        signature = signature[7:]
    
    return hmac.compare_digest(expected_signature, signature)

@app.route('/')
def index():
    """首页重定向到登录页面"""
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['logged_in'] = True
            session['username'] = username
            flash('登录成功！', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('用户名或密码错误！', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """登出"""
    session.clear()
    flash('已成功登出！', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """消息dashboard"""
    global webhook_messages
    
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    include_archived = request.args.get('archived', 'false').lower() == 'true'
    
    # 获取分页数据
    result = get_paginated_messages(page=page, include_archived=include_archived)
    
    return render_template('dashboard.html', 
                         messages=result['messages'],
                         pagination=result['pagination'],
                         include_archived=include_archived,
                         message_count=len(webhook_messages),
                         archived_files=get_archived_files())

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """设置页面"""
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        webhook_settings['secret'] = request.form.get('secret', '')
        webhook_settings['enabled'] = 'enabled' in request.form
        webhook_settings['event_filter'] = request.form.get('event_filter', '')
        
        # 保存设置到文件
        if save_settings(webhook_settings):
            flash('设置已保存！', 'success')
        else:
            flash('保存设置失败！', 'error')
    
    return render_template('settings.html', settings=webhook_settings)

@app.route('/webhook', methods=['POST'])
def webhook_endpoint():
    """Webhook接收端点"""
    global webhook_messages
    
    if not webhook_settings['enabled']:
        return jsonify({'error': 'Webhook disabled'}), 403
    
    # 获取原始数据
    payload = request.get_data()
    signature = request.headers.get('X-Hub-Signature-256') or request.headers.get('X-Signature')
    
    # 验证签名（如果设置了secret）
    if webhook_settings['secret']:
        if not verify_webhook_signature(payload, signature, webhook_settings['secret']):
            return jsonify({'error': 'Invalid signature'}), 401
    
    try:
        # 解析JSON数据
        data = request.get_json() or {}
        
        # 事件过滤（如果设置了过滤器）
        if webhook_settings['event_filter']:
            event_type = data.get('event', '') or request.headers.get('X-Event-Type', '')
            if webhook_settings['event_filter'] not in event_type:
                return jsonify({'message': 'Event filtered'}), 200
        
        # 生成唯一ID（考虑所有消息包括归档的）
        message_id = get_next_message_id()
        
        # 保存消息（只保存data数据，不保存请求头）
        message = {
            'id': message_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data': data,
            'source_ip': request.remote_addr
        }
        
        webhook_messages.insert(0, message)  # 最新消息在前
        
        # 使用配置文件中的限制数量，而不是硬编码的1000
        if len(webhook_messages) > MAX_ACTIVE_MESSAGES:
            webhook_messages.pop()
        
        # 保存到文件
        save_messages(webhook_messages)
        
        # 实时推送新消息
        broadcast_new_message(message)
        
        return jsonify({'message': 'Webhook received successfully', 'id': message['id']}), 200
        
    except Exception as e:
        # 生成唯一ID（考虑所有消息包括归档的）
        error_id = get_next_message_id()
        
        error_message = {
            'id': error_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': str(e),
            'data': payload.decode('utf-8', errors='ignore'),
            'source_ip': request.remote_addr
        }
        webhook_messages.insert(0, error_message)
        
        # 保存到文件
        save_messages(webhook_messages)
        
        # 实时推送错误消息
        broadcast_new_message(error_message)
        
        return jsonify({'error': 'Failed to process webhook', 'details': str(e)}), 400

@app.route('/api/messages')
def api_messages():
    """API接口获取消息（AJAX用）"""
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    include_archived = request.args.get('archived', 'false').lower() == 'true'
    
    # 获取分页数据
    result = get_paginated_messages(page=page, include_archived=include_archived)
    
    return jsonify(result)

@app.route('/api/stats')
def api_stats():
    """API接口获取统计数据"""
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # 获取活跃消息数量
        active_count = len(webhook_messages)
        
        # 获取归档文件数量
        archived_files = get_archived_files()
        archived_count = len(archived_files)
        
        # 获取归档消息总数
        total_archived_messages = 0
        for archive_info in archived_files:
            try:
                with open(archive_info['file'], 'r', encoding='utf-8') as f:
                    archived_messages = json.load(f)
                    total_archived_messages += len(archived_messages)
            except Exception as e:
                print(f"读取归档文件失败: {e}")
        
        # 计算总消息数
        total_messages = active_count + total_archived_messages
        
        # 返回统计数据
        stats = {
            'total_messages': total_messages,
            'active_messages': active_count,
            'archived_messages': total_archived_messages,
            'archived_files': archived_count,
            'recent_messages': min(active_count, 24)  # 最近24条最近消息
        }
        
        return jsonify(stats)
        
    except Exception as e:
        print(f"获取统计数据失败: {e}")
        return jsonify({'error': 'Failed to get stats'}), 500

@app.route('/api/stream')
def message_stream():
    """
SSE消息流端点"""
    if 'logged_in' not in session:
        return "Unauthorized", 401
    
    def event_stream():
        """生成SSE事件流"""
        while True:
            try:
                # 阻塞等待新消息，超时30秒发送心跳
                try:
                    message_data = message_queue.get(timeout=30)
                    yield f"data: {message_data}\n\n"
                except queue.Empty:
                    # 发送心跳保持连接
                    yield "data: {\"type\": \"heartbeat\"}\n\n"
            except Exception as e:
                print(f"SSE流错误: {e}")
                break
    
    return app.response_class(
        event_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )

@app.route('/api/clear_messages', methods=['POST'])
def clear_messages():
    """清空消息"""
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    global webhook_messages
    webhook_messages = []
    
    # 保存到文件
    if save_messages(webhook_messages):
        return jsonify({'message': 'Messages cleared'})
    else:
        return jsonify({'error': 'Failed to clear messages'}), 500

if __name__ == '__main__':
    # 创建templates目录
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("Webhook服务启动中...")
    print(f"管理员账号: {config.ADMIN_USERNAME}")
    print(f"管理员密码: {config.ADMIN_PASSWORD}")
    print(f"Webhook端点: http://{config.HOST}:{config.PORT}/webhook")
    print(f"管理界面: http://{config.HOST}:{config.PORT}")
    print(f"配置文件: {config.__class__.__name__}")
    print(f"数据目录: {config.DATA_DIR}")
    
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
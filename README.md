# Webhook管理系统

一个功能完整的Webhook接收和管理系统，支持消息接收、验证、过滤和Web界面管理。

## ✨ 功能特性

- 🔐 **安全认证**: 用户名密码登录保护
- 📨 **消息接收**: 接收POST请求的Webhook消息  
- 🔒 **签名验证**: 支持HMAC-SHA256签名验证
- 🎯 **事件过滤**: 根据事件类型过滤消息
- 📊 **实时监控**: Dashboard实时显示接收的消息
- ⚙️ **配置管理**: Web界面配置Webhook参数
- 🔄 **自动刷新**: 支持自动刷新消息列表
- 💾 **文件存储**: 消息和设置自动保存到本地JSON文件
- 🎯 **精简显示**: 页面只显示data数据，不显示请求头信息
- 📄 **文件切割**: 消息过多时自动归档到日期文件夹
- 📜 **分页显示**: Dashboard支持分页浏览，可选择包含归档消息
- 🎨 **JSON美化**: 自动对JSON数据进行语法高亮和格式化显示

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动

### 3. 访问管理界面

- 打开浏览器访问: `http://localhost:5000`
- 默认账号: `admin`
- 默认密码: `admin123`

### 4. Webhook端点

- **URL**: `http://localhost:5000/webhook`
- **方法**: `POST`
- **Content-Type**: `application/json`

## 📝 使用说明

### Dashboard功能

- **消息列表**: 查看所有接收到的Webhook消息
- **实时刷新**: 点击"刷新"按钮或开启自动刷新
- **清空消息**: 清空所有历史消息
- **消息详情**: 显示请求头、数据内容、来源IP等

### 设置功能

- **Webhook密钥**: 设置用于签名验证的密钥
- **启用/禁用**: 控制是否接收Webhook请求
- **事件过滤**: 只接收包含特定关键词的事件

### 签名验证

如果设置了密钥，请求需要包含签名头部：

```bash
# 计算签名
signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

# 添加到请求头
X-Hub-Signature-256: sha256={signature}
# 或
X-Signature: {signature}
```

## 🧪 测试

运行测试脚本验证功能：

```bash
# 基础功能测试
python test_webhook.py

# 文件存储测试
python test_file_storage.py

# 分页和文件切割测试
python test_pagination.py
```

测试包括：
- ✅ 基础Webhook请求
- 🔐 签名验证
- 🐙 GitHub风格Webhook
- ❌ 无效签名处理
- 📦 大数据载荷
- 💾 文件存储功能
- 🇺🇳 中文数据处理

## 📖 API示例

### 基础请求

```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"event": "test", "message": "Hello Webhook"}'
```

### 带签名验证

```bash
# Python示例
import hmac
import hashlib
import requests
import json

payload = json.dumps({"event": "push", "data": "some data"})
secret = "your-webhook-secret"
signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

requests.post(
    "http://localhost:5000/webhook",
    data=payload,
    headers={
        "Content-Type": "application/json",
        "X-Hub-Signature-256": f"sha256={signature}"
    }
)
```

### GitHub风格Webhook

```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -H "X-Event-Type: push" \
  -H "X-Hub-Signature-256: sha256=签名值" \
  -d '{"action": "opened", "repository": {...}}'
```

## 📄 文件自动切割

系统会根据消息数量自动进行文件切割：

### 切割规则
- **活跃消息上限**: 1000条（可配置）
- **单文件上限**: 500条（可配置）
- **归档策略**: 超过上限时自动将旧消息归档到日期文件夹

### 文件结构
```
webhook_data/
├── messages.json          # 当前活跃消息
├── settings.json          # 系统设置
└── archive/               # 归档目录
    ├── messages_2024-01-15.json  # 按日期归档
    ├── messages_2024-01-16.json
    └── messages_2024-01-17.json
```

### 自动归档特性
- 自动按日期分组归档
- 去重处理，避免重复消息
- 按时间排序存储
- UTF-8编码，支持中文

## 📜 分页功能

Dashboard支持分页浏览，提供更好的用户体验：

### 分页设置
- **每页显示**: 20条消息（可配置）
- **智能分页**: 显示前3页、后3页和当前页周围的页码
- **快速导航**: 支持首页、末页、上一页、下一页

### 消息类型
- **活跃消息**: 当前未归档的消息
- **归档消息**: 已归档到日期文件的消息
- **全部消息**: 包含活跃+归档的所有消息

### 使用方法
```
# 查看第2页活跃消息
http://localhost:5000/dashboard?page=2

# 查看包含归档的第1页
http://localhost:5000/dashboard?page=1&archived=true
```

## 🎨 JSON美化显示

系统会自动对JSON数据进行美化处理：

### 语法高亮
- **键名**: 蓝色显示
- **字符串**: 绿色显示  
- **数字**: 橙色显示
- **布尔值**: 粉色显示
- **null值**: 灰色显示

### 格式化
- 自动缩进和换行
- 保持JSON结构清晰
- 支持复杂嵌套对象
- 中文内容正常显示

系统会自动在`webhook_data`目录下创建以下文件：

- **messages.json**: 存储所有Webhook消息数据
- **settings.json**: 存储Webhook配置设置

### 消息数据格式

```json
{
  "id": 1,
  "timestamp": "2024-01-15 14:30:25",
  "data": {
    "event": "test",
    "message": "Hello Webhook",
    "user_id": 12345
  },
  "source_ip": "127.0.0.1"
}
```

### 设置数据格式

```json
{
  "secret": "your-webhook-secret",
  "enabled": true,
  "event_filter": "push"
}
```

### 数据持久化

- 消息会实时保存到文件，重启服务后自动加载
- 设置变更后会立即保存到文件
- 支持中文数据，使用UTF-8编码存储
- 自动限制消息数量（最多1000条），防止文件过大

### 环境变量

可以通过环境变量配置：

```bash
export WEBHOOK_SECRET_KEY="your-secret-key"
export WEBHOOK_PORT=5000
export WEBHOOK_HOST="0.0.0.0"
```

### 默认配置

- **端口**: 5000
- **主机**: 0.0.0.0 (允许外部访问)
- **默认密钥**: default-webhook-secret
- **消息限制**: 1000条 (自动清理旧消息)

## 🛡️ 安全注意事项

1. **更改默认密码**: 生产环境请修改默认管理员密码
2. **设置强密钥**: 使用复杂的Webhook验证密钥
3. **HTTPS部署**: 生产环境建议使用HTTPS
4. **防火墙设置**: 限制访问来源IP
5. **定期清理**: 定期清理历史消息数据

## 📁 文件结构

```
webhook/
├── app.py                 # 主应用文件
├── requirements.txt       # Python依赖
├── test_webhook.py       # 基础测试脚本
├── test_file_storage.py  # 文件存储测试脚本
├── README.md             # 说明文档
├── webhook_data/         # 数据存储目录
│   ├── messages.json     # 消息数据
│   └── settings.json     # 配置数据
└── templates/            # HTML模板
    ├── login.html        # 登录页面
    ├── dashboard.html    # 控制面板
    └── settings.html     # 设置页面
```

## 🔄 扩展功能

### 数据库存储

可以将文件存储替换为数据库：

```python
# 替换文件存储
from pathlib import Path
import json

# 使用SQLite
import sqlite3

def init_database():
    conn = sqlite3.connect('webhook.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            data TEXT NOT NULL,
            source_ip TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
```

### 消息通知

添加邮件或其他通知方式：

```python
def send_notification(message):
    # 发送邮件通知
    # 发送Slack消息等
    pass
```

### 更多验证方式

支持更多签名算法：

```python
def verify_signature(payload, signature, secret, algorithm='sha256'):
    # 支持多种签名算法
    pass
```

## 🐛 故障排除

### 常见问题

1. **无法访问管理界面**
   - 检查服务是否启动
   - 确认端口5000未被占用

2. **Webhook请求失败**
   - 检查URL是否正确
   - 确认Content-Type为application/json

3. **签名验证失败**
   - 检查密钥是否正确
   - 确认签名计算方法
   - 验证请求头格式

### 日志调试

启用Flask调试模式：

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！
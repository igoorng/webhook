# Webhook管理系统配置说明

## 📋 概述

现在Webhook管理系统使用模块化的配置管理，所有配置参数都已提取到独立的配置文件中，便于管理和部署。

## 📁 配置文件结构

```
webhook/
├── config.py          # 核心配置类
├── .env.example       # 环境变量配置模板
├── .env              # 实际环境变量配置（需要手动创建）
├── manage_config.py   # 配置管理工具
└── app.py            # 主应用文件（现在从config.py读取配置）
```

## 🔧 配置方法

### 方法1：使用环境变量（推荐）

1. **复制配置模板**：
   ```bash
   cp .env.example .env
   ```

2. **编辑配置文件**：
   ```bash
   # 编辑.env文件
   notepad .env  # Windows
   nano .env     # Linux/Mac
   ```

3. **修改配置参数**：
   ```env
   # 修改管理员密码
   ADMIN_PASSWORD=your-secure-password
   
   # 修改服务端口
   PORT=8080
   
   # 设置运行环境
   FLASK_ENV=production
   ```

### 方法2：使用配置管理工具

```bash
# 显示当前配置
python manage_config.py show

# 验证配置
python manage_config.py validate

# 创建.env文件
python manage_config.py create

# 查看配置模板
python manage_config.py template
```

## ⚙️ 主要配置参数

### 应用配置
- `SECRET_KEY`: Flask应用密钥
- `DEBUG`: 调试模式开关
- `HOST`: 服务器绑定地址
- `PORT`: 服务器端口

### 管理员配置
- `ADMIN_USERNAME`: 管理员用户名
- `ADMIN_PASSWORD`: 管理员密码

### 存储配置
- `DATA_DIR`: 数据存储目录
- `MAX_ACTIVE_MESSAGES`: 活跃消息最大数量
- `MAX_MESSAGES_PER_FILE`: 每个文件最大消息数
- `PAGE_SIZE`: 每页显示消息数

### Webhook配置
- `DEFAULT_WEBHOOK_SECRET`: 默认签名密钥
- `DEFAULT_WEBHOOK_ENABLED`: 默认启用状态
- `DEFAULT_EVENT_FILTER`: 默认事件过滤器

### 安全配置
- `ENABLE_SIGNATURE_VERIFICATION`: 启用签名验证

## 🌍 运行环境

系统支持多种运行环境：

### 开发环境 (development)
```env
FLASK_ENV=development
DEBUG=True
LOG_LEVEL=DEBUG
```

### 生产环境 (production)
```env
FLASK_ENV=production
DEBUG=False
LOG_LEVEL=WARNING
SECRET_KEY=your-production-secret-key
```

### 测试环境 (testing)
```env
FLASK_ENV=testing
DEBUG=True
DATA_DIR=test_webhook_data
```

## 🚀 启动应用

### 使用默认配置
```bash
python app.py
```

### 指定运行环境
```bash
# 开发环境
FLASK_ENV=development python app.py

# 生产环境
FLASK_ENV=production python app.py

# 测试环境
FLASK_ENV=testing python app.py
```

## 📋 配置验证

启动前可以验证配置是否正确：

```bash
# 验证当前配置
python manage_config.py validate

# 查看当前配置
python manage_config.py show
```

## 🔐 安全建议

### 生产环境安全配置
1. **修改默认密码**：
   ```env
   ADMIN_USERNAME=your-admin-name
   ADMIN_PASSWORD=your-secure-password
   ```

2. **使用强密钥**：
   ```env
   SECRET_KEY=your-randomly-generated-secret-key
   ```

3. **启用签名验证**：
   ```env
   ENABLE_SIGNATURE_VERIFICATION=True
   DEFAULT_WEBHOOK_SECRET=your-webhook-secret
   ```

4. **设置合适的日志级别**：
   ```env
   LOG_LEVEL=WARNING
   ENABLE_ACCESS_LOG=False
   ```

## 📝 配置示例

### 完整的生产环境配置
```env
# 应用配置
SECRET_KEY=your-production-secret-key-here
FLASK_ENV=production
DEBUG=False
HOST=0.0.0.0
PORT=5000

# 管理员配置
ADMIN_USERNAME=admin
ADMIN_PASSWORD=SecurePassword123!

# 存储配置
DATA_DIR=/var/webhook_data
MAX_ACTIVE_MESSAGES=2000
MAX_MESSAGES_PER_FILE=1000
PAGE_SIZE=50

# Webhook配置
DEFAULT_WEBHOOK_SECRET=your-webhook-signing-secret
DEFAULT_WEBHOOK_ENABLED=True
DEFAULT_EVENT_FILTER=

# 安全配置
ENABLE_SIGNATURE_VERIFICATION=True

# 日志配置
LOG_LEVEL=INFO
ENABLE_ACCESS_LOG=True
```

## 🔧 故障排除

### 常见问题

1. **配置文件不生效**：
   - 确保.env文件在项目根目录
   - 检查环境变量格式是否正确
   - 重启应用程序

2. **目录权限问题**：
   - 确保应用有权限创建数据目录
   - 检查DATA_DIR路径是否正确

3. **端口冲突**：
   - 修改PORT配置
   - 检查端口是否被其他程序占用

### 配置重置

如果配置出现问题，可以重置到默认状态：
```bash
# 删除自定义配置
rm .env

# 重新创建配置文件
python manage_config.py create
```

## 📚 更多信息

- 查看config.py文件了解所有可用配置参数
- 使用manage_config.py工具管理配置
- 参考.env.example了解配置格式
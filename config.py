"""
Webhook管理系统配置文件
"""
import os
from pathlib import Path
from werkzeug.security import generate_password_hash

class Config:
    """基础配置类"""
    
    # ==================== 应用配置 ====================
    # Flask应用密钥
    SECRET_KEY = os.environ.get('SECRET_KEY', '65597')
    
    # 调试模式
    DEBUG = os.environ.get('DEBUG', 'True').lower() in ['true', '1', 'yes']
    
    # 服务器配置
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # ==================== 管理员账号配置 ====================
    # 默认管理员用户名
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    
    # 默认管理员密码
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    # 管理员密码哈希（自动生成）
    @property
    def ADMIN_PASSWORD_HASH(self):
        return generate_password_hash(self.ADMIN_PASSWORD)
    
    # ==================== 文件存储配置 ====================
    # 数据存储根目录
    DATA_DIR = Path(os.environ.get('DATA_DIR', 'webhook_data'))
    
    # 消息文件路径
    @property
    def MESSAGES_FILE(self):
        return self.DATA_DIR / 'messages.json'
    
    # 设置文件路径
    @property
    def SETTINGS_FILE(self):
        return self.DATA_DIR / 'settings.json'
    
    # 归档目录路径
    @property
    def ARCHIVE_DIR(self):
        return self.DATA_DIR / 'archive'
    
    # ==================== 存储限制配置 ====================
    # 每个文件最大消息数
    MAX_MESSAGES_PER_FILE = int(os.environ.get('MAX_MESSAGES_PER_FILE', 500))
    
    # 活跃消息最大数（超过后自动归档）
    MAX_ACTIVE_MESSAGES = int(os.environ.get('MAX_ACTIVE_MESSAGES', 1000))
    
    # 每页显示消息数
    PAGE_SIZE = int(os.environ.get('PAGE_SIZE', 20))
    
    # ==================== Webhook默认设置 ====================
    # 默认Webhook签名密钥
    DEFAULT_WEBHOOK_SECRET = os.environ.get('DEFAULT_WEBHOOK_SECRET', '0xca74f404e0c7bfa35b13b511097df966d5a65597')
    
    # 默认启用状态
    DEFAULT_WEBHOOK_ENABLED = os.environ.get('DEFAULT_WEBHOOK_ENABLED', 'True').lower() in ['true', '1', 'yes']
    
    # 默认事件过滤器
    DEFAULT_EVENT_FILTER = os.environ.get('DEFAULT_EVENT_FILTER', '')
    
    # 默认设置字典
    @property
    def DEFAULT_SETTINGS(self):
        return {
            'secret': self.DEFAULT_WEBHOOK_SECRET,
            'enabled': self.DEFAULT_WEBHOOK_ENABLED,
            'event_filter': self.DEFAULT_EVENT_FILTER
        }
    
    # ==================== 实时推送配置 ====================
    # SSE心跳间隔（秒）
    SSE_HEARTBEAT_INTERVAL = int(os.environ.get('SSE_HEARTBEAT_INTERVAL', 30))
    
    # 实时连接重连间隔（秒）
    REALTIME_RECONNECT_INTERVAL = int(os.environ.get('REALTIME_RECONNECT_INTERVAL', 5))
    
    # 自动刷新间隔（秒）
    AUTO_REFRESH_INTERVAL = int(os.environ.get('AUTO_REFRESH_INTERVAL', 5))
    
    # ==================== 安全配置 ====================
    # 是否启用签名验证
    ENABLE_SIGNATURE_VERIFICATION = os.environ.get('ENABLE_SIGNATURE_VERIFICATION', 'True').lower() in ['true', '1', 'yes']
    
    # 支持的签名头部
    SIGNATURE_HEADERS = [
        'X-Hub-Signature-256',
        'X-Signature',
        'X-GitHub-Signature-256'
    ]
    
    # ==================== 日志配置 ====================
    # 日志级别
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # 是否启用访问日志
    ENABLE_ACCESS_LOG = os.environ.get('ENABLE_ACCESS_LOG', 'True').lower() in ['true', '1', 'yes']
    
    # ==================== 初始化方法 ====================
    def __init__(self):
        """初始化配置，确保必要的目录存在"""
        self.ensure_directories()
    
    def ensure_directories(self):
        """确保必要的目录存在"""
        self.DATA_DIR.mkdir(exist_ok=True)
        self.ARCHIVE_DIR.mkdir(exist_ok=True)
    
    def to_dict(self):
        """将配置转换为字典格式"""
        return {
            'SECRET_KEY': self.SECRET_KEY,
            'DEBUG': self.DEBUG,
            'HOST': self.HOST,
            'PORT': self.PORT,
            'ADMIN_USERNAME': self.ADMIN_USERNAME,
            'DATA_DIR': str(self.DATA_DIR),
            'MAX_MESSAGES_PER_FILE': self.MAX_MESSAGES_PER_FILE,
            'MAX_ACTIVE_MESSAGES': self.MAX_ACTIVE_MESSAGES,
            'PAGE_SIZE': self.PAGE_SIZE,
            'DEFAULT_WEBHOOK_SECRET': self.DEFAULT_WEBHOOK_SECRET,
            'DEFAULT_WEBHOOK_ENABLED': self.DEFAULT_WEBHOOK_ENABLED,
            'DEFAULT_EVENT_FILTER': self.DEFAULT_EVENT_FILTER,
            'SSE_HEARTBEAT_INTERVAL': self.SSE_HEARTBEAT_INTERVAL,
            'REALTIME_RECONNECT_INTERVAL': self.REALTIME_RECONNECT_INTERVAL,
            'AUTO_REFRESH_INTERVAL': self.AUTO_REFRESH_INTERVAL,
            'ENABLE_SIGNATURE_VERIFICATION': self.ENABLE_SIGNATURE_VERIFICATION,
            'LOG_LEVEL': self.LOG_LEVEL,
            'ENABLE_ACCESS_LOG': self.ENABLE_ACCESS_LOG
        }


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    # 生产环境使用更强的密钥
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32).hex())


class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    DATA_DIR = Path('test_webhook_data')
    MAX_ACTIVE_MESSAGES = 100
    PAGE_SIZE = 10


# 配置映射
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """获取配置实例"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    config_class = config_map.get(config_name, DevelopmentConfig)
    return config_class()


# 默认配置实例
config = get_config()
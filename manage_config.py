#!/usr/bin/env python3
"""
配置管理工具
用于查看、验证和管理Webhook系统配置
"""

import json
import os
from pathlib import Path
from config import config, get_config, config_map

def show_current_config():
    """显示当前配置"""
    print("📋 当前配置信息")
    print("=" * 50)
    
    config_dict = config.to_dict()
    
    print(f"🔧 配置类型: {config.__class__.__name__}")
    print(f"🌍 运行环境: {os.environ.get('FLASK_ENV', 'default')}")
    print()
    
    # 按类别显示配置
    categories = {
        '应用配置': ['SECRET_KEY', 'DEBUG', 'HOST', 'PORT'],
        '管理员配置': ['ADMIN_USERNAME'],
        '存储配置': ['DATA_DIR', 'MAX_MESSAGES_PER_FILE', 'MAX_ACTIVE_MESSAGES', 'PAGE_SIZE'],
        'Webhook配置': ['DEFAULT_WEBHOOK_SECRET', 'DEFAULT_WEBHOOK_ENABLED', 'DEFAULT_EVENT_FILTER'],
        '实时推送配置': ['SSE_HEARTBEAT_INTERVAL', 'REALTIME_RECONNECT_INTERVAL', 'AUTO_REFRESH_INTERVAL'],
        '安全配置': ['ENABLE_SIGNATURE_VERIFICATION'],
        '日志配置': ['LOG_LEVEL', 'ENABLE_ACCESS_LOG']
    }
    
    for category, keys in categories.items():
        print(f"📂 {category}:")
        for key in keys:
            if key in config_dict:
                value = config_dict[key]
                # 隐藏敏感信息
                if 'SECRET' in key or 'PASSWORD' in key:
                    if isinstance(value, str) and len(value) > 8:
                        value = value[:4] + '*' * (len(value) - 8) + value[-4:]
                print(f"   {key}: {value}")
        print()

def validate_config():
    """验证配置"""
    print("✅ 配置验证")
    print("=" * 50)
    
    issues = []
    
    # 检查必要的目录
    if not config.DATA_DIR.exists():
        issues.append(f"数据目录不存在: {config.DATA_DIR}")
    
    if not config.ARCHIVE_DIR.exists():
        issues.append(f"归档目录不存在: {config.ARCHIVE_DIR}")
    
    # 检查端口
    if not (1, 65535).__contains__(config.PORT):
        issues.append(f"端口号无效: {config.PORT}")
    
    # 检查页面大小
    if config.PAGE_SIZE <= 0:
        issues.append(f"页面大小必须大于0: {config.PAGE_SIZE}")
    
    # 检查消息限制
    if config.MAX_ACTIVE_MESSAGES <= 0:
        issues.append(f"活跃消息数必须大于0: {config.MAX_ACTIVE_MESSAGES}")
    
    if config.MAX_MESSAGES_PER_FILE <= 0:
        issues.append(f"每文件消息数必须大于0: {config.MAX_MESSAGES_PER_FILE}")
    
    if issues:
        print("❌ 发现以下问题:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    else:
        print("✅ 配置验证通过，没有发现问题")
        return True

def show_env_template():
    """显示环境变量模板"""
    print("📄 环境变量配置模板")
    print("=" * 50)
    
    if Path('.env.example').exists():
        print("📁 .env.example 文件内容:")
        print()
        with open('.env.example', 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
    else:
        print("❌ .env.example 文件不存在")
        print("请运行程序生成示例配置文件")

def create_env_file():
    """创建.env文件"""
    print("📝 创建环境变量配置文件")
    print("=" * 50)
    
    if Path('.env').exists():
        response = input("⚠️  .env文件已存在，是否覆盖？(y/N): ")
        if response.lower() != 'y':
            print("❌ 操作已取消")
            return
    
    if not Path('.env.example').exists():
        print("❌ .env.example 文件不存在，无法创建配置文件")
        return
    
    # 复制示例文件
    with open('.env.example', 'r', encoding='utf-8') as src:
        content = src.read()
    
    with open('.env', 'w', encoding='utf-8') as dst:
        dst.write(content)
    
    print("✅ .env文件创建成功")
    print("📝 请编辑.env文件并根据需要修改配置")

def test_config_loading():
    """测试不同环境的配置加载"""
    print("🧪 测试配置加载")
    print("=" * 50)
    
    for env_name, config_class in config_map.items():
        print(f"🌍 {env_name} 环境:")
        try:
            test_config = config_class()
            print(f"   ✅ 配置类: {config_class.__name__}")
            print(f"   📁 数据目录: {test_config.DATA_DIR}")
            print(f"   🐛 调试模式: {test_config.DEBUG}")
            print(f"   📊 日志级别: {test_config.LOG_LEVEL}")
        except Exception as e:
            print(f"   ❌ 加载失败: {e}")
        print()

def show_help():
    """显示帮助信息"""
    print("🔧 Webhook配置管理工具")
    print("=" * 50)
    print("可用命令:")
    print("  show      - 显示当前配置")
    print("  validate  - 验证配置")
    print("  template  - 显示环境变量模板")
    print("  create    - 创建.env配置文件")
    print("  test      - 测试配置加载")
    print("  help      - 显示此帮助信息")
    print()
    print("示例:")
    print("  python manage_config.py show")
    print("  python manage_config.py validate")

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    commands = {
        'show': show_current_config,
        'validate': validate_config,
        'template': show_env_template,
        'create': create_env_file,
        'test': test_config_loading,
        'help': show_help
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"❌ 未知命令: {command}")
        print()
        show_help()

if __name__ == "__main__":
    main()
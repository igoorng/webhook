#!/usr/bin/env python3
"""
测试Webhook文件存储功能
"""

import requests
import json
import time

# 配置
WEBHOOK_URL = "http://localhost:5000/webhook"

def test_simple_data():
    """测试简单数据存储"""
    print("🧪 测试简单数据存储...")
    
    data = {
        "event": "test",
        "message": "测试消息",
        "user_id": 12345,
        "action": "create"
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"✅ 状态码: {response.status_code}")
        print(f"✅ 响应: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_complex_data():
    """测试复杂数据存储"""
    print("\n📦 测试复杂数据存储...")
    
    data = {
        "event": "order_created",
        "order": {
            "id": "ORDER_001",
            "customer": {
                "name": "张三",
                "email": "zhangsan@example.com",
                "phone": "13800138000"
            },
            "items": [
                {
                    "product_id": "PROD_001",
                    "name": "商品1",
                    "price": 99.99,
                    "quantity": 2
                },
                {
                    "product_id": "PROD_002", 
                    "name": "商品2",
                    "price": 149.99,
                    "quantity": 1
                }
            ],
            "total": 349.97,
            "currency": "CNY",
            "status": "pending"
        },
        "metadata": {
            "source": "web",
            "timestamp": int(time.time()),
            "version": "1.0"
        }
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"✅ 状态码: {response.status_code}")
        print(f"✅ 响应: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_chinese_data():
    """测试中文数据"""
    print("\n🇨🇳 测试中文数据...")
    
    data = {
        "事件": "用户注册",
        "用户信息": {
            "姓名": "李四",
            "城市": "北京",
            "描述": "这是一个包含中文的测试数据",
            "标签": ["新用户", "VIP", "推荐用户"]
        },
        "时间戳": int(time.time())
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"✅ 状态码: {response.status_code}")
        print(f"✅ 响应: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_array_data():
    """测试数组数据"""
    print("\n📋 测试数组数据...")
    
    data = {
        "event": "batch_update",
        "items": [
            {"id": i, "name": f"项目_{i}", "status": "active"}
            for i in range(1, 11)
        ],
        "summary": {
            "total": 10,
            "processed": 10,
            "errors": 0
        }
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"✅ 状态码: {response.status_code}")
        print(f"✅ 响应: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def run_tests():
    """运行所有测试"""
    print("🚀 开始文件存储测试...")
    print("=" * 50)
    
    tests = [
        ("简单数据", test_simple_data),
        ("复杂数据", test_complex_data),
        ("中文数据", test_chinese_data),
        ("数组数据", test_array_data)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
        
        time.sleep(1)  # 间隔1秒
    
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    # 检查文件是否生成
    print("\n📁 检查存储文件:")
    import os
    data_dir = "webhook_data"
    messages_file = os.path.join(data_dir, "messages.json")
    settings_file = os.path.join(data_dir, "settings.json")
    
    if os.path.exists(messages_file):
        size = os.path.getsize(messages_file)
        print(f"✅ 消息文件已生成: {messages_file} ({size} bytes)")
    else:
        print(f"❌ 消息文件未找到: {messages_file}")
    
    if os.path.exists(settings_file):
        size = os.path.getsize(settings_file)
        print(f"✅ 设置文件已生成: {settings_file} ({size} bytes)")
    else:
        print(f"❌ 设置文件未找到: {settings_file}")

if __name__ == "__main__":
    print("Webhook文件存储测试工具")
    print("确保Webhook服务已在 http://localhost:5000 启动")
    print()
    
    # 检查服务是否可用
    try:
        response = requests.get("http://localhost:5000")
        if response.status_code in [200, 302]:
            print("✅ Webhook服务已启动")
            run_tests()
        else:
            print("❌ Webhook服务未响应")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Webhook服务，请确保服务已启动")
    except Exception as e:
        print(f"❌ 检查服务时出错: {e}")
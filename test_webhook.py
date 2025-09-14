#!/usr/bin/env python3
"""
Webhook测试脚本
用于测试Webhook服务的各种功能
"""

import requests
import json
import hmac
import hashlib
import time

# 配置
WEBHOOK_URL = "http://localhost:5000/webhook"
SECRET = "0xca74f404e0c7bfa35b13b511097df966d5a65597"  # 与app.py中的默认值保持一致

def generate_signature(payload, secret):
    """生成HMAC-SHA256签名"""
    return hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def test_basic_webhook():
    """测试基础Webhook功能"""
    print("🧪 测试基础Webhook请求...")
    
    data = {
        "event": "test",
        "message": "Hello from test script",
        "timestamp": int(time.time()),
        "data": {
            "user": "test_user",
            "action": "test_action"
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

def test_signed_webhook():
    """测试带签名的Webhook请求"""
    print("\n🔐 测试带签名验证的Webhook请求...")
    
    data = {
        "event": "push",
        "repository": "test-repo",
        "action": "opened",
        "payload": "signed test data"
    }
    
    payload = json.dumps(data)
    signature = generate_signature(payload, SECRET)
    
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": f"sha256={signature}",
        "X-Event-Type": "push"
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            data=payload,
            headers=headers
        )
        
        print(f"✅ 状态码: {response.status_code}")
        print(f"✅ 响应: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_github_style_webhook():
    """测试GitHub风格的Webhook"""
    print("\n🐙 测试GitHub风格的Webhook...")
    
    data = {
        "zen": "Non-blocking is better than blocking.",
        "hook_id": 12345678,
        "hook": {
            "type": "Repository",
            "id": 12345678,
            "name": "web",
            "active": True,
            "events": ["push", "pull_request"],
            "config": {
                "content_type": "json",
                "insecure_ssl": "0",
                "url": WEBHOOK_URL
            }
        },
        "repository": {
            "id": 35129377,
            "name": "public-repo",
            "full_name": "baxterthehacker/public-repo",
            "owner": {
                "login": "baxterthehacker",
                "id": 6752317,
                "type": "User"
            },
            "private": False,
            "description": "This your first repo!"
        }
    }
    
    payload = json.dumps(data)
    signature = generate_signature(payload, SECRET)
    
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": f"sha256={signature}",
        "X-GitHub-Event": "ping",
        "X-GitHub-Delivery": f"12345678-1234-1234-1234-123456789012",
        "User-Agent": "GitHub-Hookshot/abc123"
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            data=payload,
            headers=headers
        )
        
        print(f"✅ 状态码: {response.status_code}")
        print(f"✅ 响应: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_invalid_signature():
    """测试无效签名"""
    print("\n❌ 测试无效签名...")
    
    data = {"event": "test", "message": "This should fail"}
    payload = json.dumps(data)
    
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": "sha256=invalid_signature"
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            data=payload,
            headers=headers
        )
        
        print(f"✅ 状态码: {response.status_code} (应该是401)")
        print(f"✅ 响应: {response.json()}")
        return response.status_code == 401
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_large_payload():
    """测试大数据载荷"""
    print("\n📦 测试大数据载荷...")
    
    # 生成一个较大的数据集
    large_data = {
        "event": "bulk_update",
        "items": [
            {
                "id": i,
                "name": f"item_{i}",
                "description": f"This is item number {i} with some additional data",
                "metadata": {
                    "created_at": f"2024-01-{i:02d}T10:00:00Z",
                    "tags": [f"tag_{j}" for j in range(5)],
                    "properties": {f"prop_{k}": f"value_{k}" for k in range(10)}
                }
            }
            for i in range(1, 101)  # 100个项目
        ]
    }
    
    payload = json.dumps(large_data)
    signature = generate_signature(payload, SECRET)
    
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": f"sha256={signature}",
        "X-Event-Type": "bulk_update"
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            data=payload,
            headers=headers
        )
        
        print(f"✅ 状态码: {response.status_code}")
        print(f"✅ 数据大小: {len(payload)} 字节")
        print(f"✅ 响应: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始Webhook测试...")
    print("=" * 50)
    
    tests = [
        ("基础功能", test_basic_webhook),
        ("签名验证", test_signed_webhook),
        ("GitHub风格", test_github_style_webhook),
        ("无效签名", test_invalid_signature),
        ("大数据载荷", test_large_payload)
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

if __name__ == "__main__":
    print("Webhook测试工具")
    print("确保Webhook服务已在 http://localhost:5000 启动")
    print()
    
    # 检查服务是否可用
    try:
        response = requests.get("http://localhost:5000")
        if response.status_code == 200 or response.status_code == 302:
            print("✅ Webhook服务已启动")
            run_all_tests()
        else:
            print("❌ Webhook服务未响应")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Webhook服务，请确保服务已启动")
    except Exception as e:
        print(f"❌ 检查服务时出错: {e}")
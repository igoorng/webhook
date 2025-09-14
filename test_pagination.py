#!/usr/bin/env python3
"""
测试Webhook分页和文件切割功能
"""

import requests
import json
import time
import random

# 配置
WEBHOOK_URL = "http://localhost:5000/webhook"

def generate_test_data(count=100):
    """生成测试数据"""
    test_data = []
    
    event_types = ["user_created", "order_placed", "payment_completed", "product_updated", "inventory_changed"]
    statuses = ["pending", "processing", "completed", "failed", "cancelled"]
    
    for i in range(count):
        data = {
            "event": random.choice(event_types),
            "id": f"TEST_{i+1:03d}",
            "timestamp": int(time.time()) + i,
            "data": {
                "user_id": random.randint(1000, 9999),
                "amount": round(random.uniform(10.0, 1000.0), 2),
                "status": random.choice(statuses),
                "metadata": {
                    "source": "test_script",
                    "batch_id": f"BATCH_{(i//10)+1}",
                    "tags": [f"tag_{j}" for j in range(random.randint(1, 4))],
                    "complex_data": {
                        "nested_object": {
                            "value": random.randint(1, 100),
                            "description": f"这是第{i+1}条测试数据",
                            "items": [
                                {
                                    "id": f"item_{k}",
                                    "name": f"商品{k}",
                                    "price": round(random.uniform(5.0, 100.0), 2)
                                }
                                for k in range(random.randint(1, 5))
                            ]
                        }
                    }
                }
            }
        }
        test_data.append(data)
    
    return test_data

def send_test_messages(data_list):
    """发送测试消息"""
    print(f"🚀 开始发送 {len(data_list)} 条测试消息...")
    
    success_count = 0
    error_count = 0
    
    for i, data in enumerate(data_list):
        try:
            response = requests.post(
                WEBHOOK_URL,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code == 200:
                success_count += 1
                if (i + 1) % 10 == 0:
                    print(f"✅ 已发送 {i + 1}/{len(data_list)} 条消息")
            else:
                error_count += 1
                print(f"❌ 消息 {i + 1} 发送失败: {response.status_code}")
                
        except Exception as e:
            error_count += 1
            print(f"❌ 消息 {i + 1} 发送异常: {e}")
        
        # 短暂延迟，避免过快发送
        time.sleep(0.1)
    
    print(f"\n📊 发送完成:")
    print(f"   成功: {success_count} 条")
    print(f"   失败: {error_count} 条")
    print(f"   总计: {len(data_list)} 条")

def test_pagination():
    """测试分页功能"""
    print("\n📄 测试分页功能...")
    
    base_url = "http://localhost:5000/dashboard"
    
    # 测试不同页面
    pages_to_test = [1, 2, 3]
    
    for page in pages_to_test:
        try:
            url = f"{base_url}?page={page}"
            response = requests.get(url)
            
            if response.status_code == 200:
                print(f"✅ 第 {page} 页访问成功")
            else:
                print(f"❌ 第 {page} 页访问失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 访问第 {page} 页异常: {e}")
    
    # 测试包含归档的页面
    try:
        url = f"{base_url}?page=1&archived=true"
        response = requests.get(url)
        
        if response.status_code == 200:
            print("✅ 归档页面访问成功")
        else:
            print(f"❌ 归档页面访问失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 访问归档页面异常: {e}")

def test_api_pagination():
    """测试API分页"""
    print("\n🔌 测试API分页功能...")
    
    # 需要先登录获取session
    login_url = "http://localhost:5000/login"
    api_url = "http://localhost:5000/api/messages"
    
    session = requests.Session()
    
    # 尝试登录
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        login_response = session.post(login_url, data=login_data)
        
        if login_response.status_code == 200 or "dashboard" in login_response.url:
            print("✅ 登录成功")
            
            # 测试API分页
            for page in [1, 2, 3]:
                params = {"page": page}
                api_response = session.get(api_url, params=params)
                
                if api_response.status_code == 200:
                    data = api_response.json()
                    pagination = data.get('pagination', {})
                    messages = data.get('messages', [])
                    
                    print(f"✅ API第 {page} 页: {len(messages)} 条消息, 总页数: {pagination.get('total_pages', 0)}")
                else:
                    print(f"❌ API第 {page} 页失败: {api_response.status_code}")
            
            # 测试包含归档
            params = {"page": 1, "archived": "true"}
            api_response = session.get(api_url, params=params)
            
            if api_response.status_code == 200:
                data = api_response.json()
                pagination = data.get('pagination', {})
                messages = data.get('messages', [])
                
                print(f"✅ API归档页面: {len(messages)} 条消息, 总消息数: {pagination.get('total_messages', 0)}")
            else:
                print(f"❌ API归档页面失败: {api_response.status_code}")
                
        else:
            print("❌ 登录失败")
            
    except Exception as e:
        print(f"❌ API测试异常: {e}")

def check_files():
    """检查生成的文件"""
    print("\n📁 检查存储文件...")
    
    import os
    from pathlib import Path
    
    data_dir = Path("webhook_data")
    
    if data_dir.exists():
        print(f"✅ 数据目录存在: {data_dir}")
        
        # 检查消息文件
        messages_file = data_dir / "messages.json"
        if messages_file.exists():
            size = messages_file.stat().st_size
            print(f"✅ 消息文件: {messages_file} ({size:,} bytes)")
            
            # 检查消息数量
            try:
                with open(messages_file, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
                    print(f"   活跃消息数量: {len(messages)}")
            except Exception as e:
                print(f"   读取消息文件失败: {e}")
        else:
            print("❌ 消息文件不存在")
        
        # 检查归档文件
        archive_dir = data_dir / "archive"
        if archive_dir.exists():
            archive_files = list(archive_dir.glob("messages_*.json"))
            print(f"✅ 归档目录: {archive_dir} ({len(archive_files)} 个文件)")
            
            total_archived = 0
            for archive_file in archive_files:
                try:
                    with open(archive_file, 'r', encoding='utf-8') as f:
                        archived_messages = json.load(f)
                        file_size = archive_file.stat().st_size
                        print(f"   {archive_file.name}: {len(archived_messages)} 条消息 ({file_size:,} bytes)")
                        total_archived += len(archived_messages)
                except Exception as e:
                    print(f"   读取归档文件 {archive_file.name} 失败: {e}")
                    
            print(f"   总归档消息数: {total_archived}")
        else:
            print("📂 归档目录不存在（正常，如果消息数量不多）")
        
        # 检查设置文件
        settings_file = data_dir / "settings.json"
        if settings_file.exists():
            size = settings_file.stat().st_size
            print(f"✅ 设置文件: {settings_file} ({size} bytes)")
        else:
            print("❌ 设置文件不存在")
            
    else:
        print("❌ 数据目录不存在")

def main():
    """主函数"""
    print("Webhook分页和文件切割测试工具")
    print("=" * 50)
    
    # 检查服务是否可用
    try:
        response = requests.get("http://localhost:5000")
        if response.status_code in [200, 302]:
            print("✅ Webhook服务已启动")
        else:
            print("❌ Webhook服务未响应")
            return
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Webhook服务，请确保服务已启动")
        return
    
    # 询问用户要发送多少条消息
    try:
        count = int(input("\n请输入要发送的测试消息数量 (建议100-500): ") or "100")
        if count <= 0:
            print("❌ 数量必须大于0")
            return
    except ValueError:
        print("❌ 请输入有效数字")
        return
    
    print(f"\n将发送 {count} 条测试消息来测试分页和文件切割功能...")
    confirm = input("确认继续? (y/N): ").lower()
    
    if confirm != 'y':
        print("取消测试")
        return
    
    # 生成并发送测试数据
    test_data = generate_test_data(count)
    send_test_messages(test_data)
    
    # 等待处理完成
    print("\n⏳ 等待3秒让服务处理消息...")
    time.sleep(3)
    
    # 测试功能
    test_pagination()
    test_api_pagination()
    check_files()
    
    print("\n🎉 测试完成!")
    print("请访问 http://localhost:5000 查看分页效果和JSON美化显示")

if __name__ == "__main__":
    main()
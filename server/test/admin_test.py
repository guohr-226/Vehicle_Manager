import requests
import json
import time

# 服务器配置
ADMIN_SERVER_URL = "http://localhost:12345"
LOGIC_SERVER_URL = "http://localhost:12344"
ADMIN_NAME = "root"
ADMIN_PWD = "123456"
TEST_USER = "temp_test_user"
TEST_USER_UPDATED = "temp_test_user_updated"
TEST_SENSOR = "temp_sensor_001"
TEST_VEHICLE = "TEMP123"

def check_server_connection(url, name):
    """检查服务器是否可以连接（使用GET替代HEAD请求）"""
    try:
        response = requests.get(url, timeout=3)
        return True
    except requests.exceptions.ConnectionError:
        print(f"无法连接到{name}服务器，请确保{name}服务器已启动")
        return False
    except requests.exceptions.Timeout:
        print(f"连接{name}服务器超时")
        return False
    except Exception as e:
        if hasattr(e, 'response') and e.response.status_code == 404:
            return True
        print(f"检查{name}服务器连接时出错: {str(e)}")
        return False

def wait_for_server(url, name, max_retries=5, delay=2):
    """等待服务器启动"""
    for i in range(max_retries):
        if check_server_connection(url, name):
            return True
        if i < max_retries - 1:
            print(f"等待{delay}秒后重试连接{name}服务器...")
            time.sleep(delay)
    return False

def get_admin_token():
    """获取管理员令牌"""
    try:
        if not check_server_connection(LOGIC_SERVER_URL, "逻辑"):
            return None
            
        resp = requests.post(
            f"{LOGIC_SERVER_URL}/verify_user_and_get_role",
            json={"name": ADMIN_NAME, "password": ADMIN_PWD},
            timeout=10
        )
        
        try:
            result = resp.json()
            return result if result in ["admin", "user"] else None
        except json.JSONDecodeError:
            print("登录接口返回的不是有效的JSON格式")
            print(f"原始响应: {resp.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("连接逻辑服务器失败，请检查服务器是否启动")
        return None
    except Exception as e:
        print(f"获取管理员令牌时出错: {str(e)}")
        return None

def test_admin_apis():
    if not wait_for_server(ADMIN_SERVER_URL, "管理员"):
        print("管理员服务器连接失败，无法进行测试")
        return
        
    if not wait_for_server(LOGIC_SERVER_URL, "逻辑"):
        print("逻辑服务器连接失败，无法进行测试")
        return
    
    token = get_admin_token()
    if not token:
        print("获取管理员令牌失败，无法进行测试")
        return
        
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    print(f"成功获取管理员令牌: {token}")
    
    user_id = None
    try:
        # 1. 测试添加用户
        print("\n1. 测试添加用户...")
        add_user_data = {
            "name": TEST_USER, 
            "password": "123456",
            "is_admin": False
        }
        resp = requests.post(
            f"{ADMIN_SERVER_URL}/add_user", 
            json=add_user_data,
            headers=headers,
            timeout=10
        )
        print(f"  响应状态码: {resp.status_code}")
        print(f"  响应内容: {resp.json()}")
        
        if not resp.json().get("success", False):
            print(f"添加用户失败: {resp.json().get('message', '未知错误')}")
            return
        
        # 2. 测试查询单个用户信息
        print("\n2. 测试查询单个用户信息...")
        resp = requests.get(
            f"{ADMIN_SERVER_URL}/get_user_info?name={TEST_USER}", 
            headers=headers,
            timeout=10
        )
        print(f"  响应状态码: {resp.status_code}")
        user_data = resp.json()
        print(f"  响应内容: {user_data}")
        
        if not user_data.get("success", False) or not user_data.get("data"):
            print(f"查询用户信息失败")
            return
            
        user_id = user_data["data"]["id"]
        print(f"  获取到测试用户ID: {user_id}")
        
        # 3. 测试批量查询用户
        print("\n3. 测试批量查询用户...")
        resp = requests.get(
            f"{ADMIN_SERVER_URL}/get_users?limit=10", 
            headers=headers,
            timeout=10
        )
        print(f"  响应状态码: {resp.status_code}")
        users_data = resp.json()
        print(f"  响应内容: {users_data}")
        
        if not users_data.get("success", False):
            print(f"批量查询用户失败")
            return
        
        # 4. 测试修改用户密码
        print("\n4. 测试修改用户密码...")
        change_pwd_data = {
            "name": TEST_USER,
            "password": "654321"
        }
        resp = requests.post(
            f"{ADMIN_SERVER_URL}/change_password",
            json=change_pwd_data,
            headers=headers,
            timeout=10
        )
        print(f"  响应状态码: {resp.status_code}")
        print(f"  响应内容: {resp.json()}")
        
        if not resp.json().get("success", False):
            print(f"修改密码失败")
        
        # 5. 测试添加传感器
        print("\n5. 测试添加传感器...")
        add_sensor_data = {
            "sensor_id": TEST_SENSOR, 
            "location": "测试位置",
            "description": "测试用传感器",
            "is_active": True,
            "is_gate": False
        }
        resp = requests.post(
            f"{ADMIN_SERVER_URL}/add_or_update_sensor",
            json=add_sensor_data,
            headers=headers,
            timeout=10
        )
        print(f"  响应状态码: {resp.status_code}")
        print(f"  响应内容: {resp.json()}")
        
        if not resp.json().get("success", False):
            print(f"添加传感器失败")
        
        # 6. 测试更新传感器
        print("\n6. 测试更新传感器...")
        update_sensor_data = {
            "sensor_id": TEST_SENSOR, 
            "location": "更新后的位置",
            "description": "更新后的描述",
            "is_active": False,
            "is_gate": True
        }
        resp = requests.post(
            f"{ADMIN_SERVER_URL}/add_or_update_sensor",
            json=update_sensor_data,
            headers=headers,
            timeout=10
        )
        print(f"  响应状态码: {resp.status_code}")
        print(f"  响应内容: {resp.json()}")
        
        if not resp.json().get("success", False):
            print(f"更新传感器失败")
        
        # 7. 测试查询单个传感器
        print("\n7. 测试查询单个传感器...")
        resp = requests.get(
            f"{ADMIN_SERVER_URL}/get_sensor_info?sensor_id={TEST_SENSOR}", 
            headers=headers,
            timeout=10
        )
        print(f"  响应状态码: {resp.status_code}")
        sensor_data = resp.json()
        print(f"  响应内容: {sensor_data}")
        
        if not sensor_data.get("success", False):
            print(f"查询传感器信息失败")
        
        # 8. 测试批量查询传感器
        print("\n8. 测试批量查询传感器...")
        resp = requests.get(
            f"{ADMIN_SERVER_URL}/get_sensors?limit=10", 
            headers=headers,
            timeout=10
        )
        print(f"  响应状态码: {resp.status_code}")
        sensors_data = resp.json()
        print(f"  响应内容: {sensors_data}")
        
        if not sensors_data.get("success", False):
            print(f"批量查询传感器失败")
        
        # 9. 测试添加车辆
        print("\n9. 测试添加车辆...")
        add_vehicle_data = {
            "vehicle_id": TEST_VEHICLE, 
            "registered_by": user_id
        }
        resp = requests.post(
            f"{ADMIN_SERVER_URL}/add_vehicle",
            json=add_vehicle_data,
            headers=headers,
            timeout=10
        )
        print(f"  响应状态码: {resp.status_code}")
        print(f"  响应内容: {resp.json()}")
        
        if not resp.json().get("success", False):
            print(f"添加车辆失败")
        
        # 10. 测试查询单个车辆
        print("\n10. 测试查询单个车辆...")
        resp = requests.get(
            f"{ADMIN_SERVER_URL}/get_vehicle_info?vehicle_id={TEST_VEHICLE}", 
            headers=headers,
            timeout=10
        )
        print(f"  响应状态码: {resp.status_code}")
        vehicle_data = resp.json()
        print(f"  响应内容: {vehicle_data}")
        
        if not vehicle_data.get("success", False):
            print(f"查询车辆信息失败")
        
        # 11. 测试批量查询车辆
        print("\n11. 测试批量查询车辆...")
        resp = requests.get(
            f"{ADMIN_SERVER_URL}/get_vehicles?limit=10", 
            headers=headers,
            timeout=10
        )
        print(f"  响应状态码: {resp.status_code}")
        vehicles_data = resp.json()
        print(f"  响应内容: {vehicles_data}")
        
        if not vehicles_data.get("success", False):
            print(f"批量查询车辆失败")
        
    finally:
        print("\n12. 清理测试数据...")
        
        # 删除测试车辆
        try:
            requests.post(
                f"{ADMIN_SERVER_URL}/delete_vehicle", 
                json={"vehicle_id": TEST_VEHICLE}, 
                headers=headers,
                timeout=10
            )
            print("  测试车辆已删除")
        except Exception as e:
            print(f"  删除测试车辆时出错: {str(e)}")
            
        # 删除测试传感器
        try:
            requests.post(
                f"{ADMIN_SERVER_URL}/delete_sensor", 
                json={"sensor_id": TEST_SENSOR}, 
                headers=headers,
                timeout=10
            )
            print("  测试传感器已删除")
        except Exception as e:
            print(f"  删除测试传感器时出错: {str(e)}")
            
        # 删除测试用户
        try:
            requests.post(
                f"{ADMIN_SERVER_URL}/delete_user", 
                json={"name": TEST_USER}, 
                headers=headers,
                timeout=10
            )
            print("  测试用户已删除")
        except Exception as e:
            print(f"  删除测试用户时出错: {str(e)}")

if __name__ == "__main__":
    print("=== 管理员接口测试程序 ===")
    test_admin_apis()
    print("\n=== 测试程序执行完毕 ===")
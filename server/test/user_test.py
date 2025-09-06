import requests
import json

BASE_URL = "http://localhost:12346"
TEST_USER = "test_user"
TEST_PWD = "test123"
TEST_VEHICLE = "ABC123"

def test_user_apis():
    print("测试查询当前用户信息...")
    resp = requests.get(f"{BASE_URL}/get_current_user_info?name={TEST_USER}")
    print(f"  响应: {resp.json()}")
    assert resp.json()["success"] == True
    
    print("\n测试修改密码...")
    change_data = {
        "name": TEST_USER,
        "old_password": TEST_PWD,
        "password": "new_test123"
    }
    resp = requests.post(f"{BASE_URL}/change_own_password", json=change_data)
    print(f"  响应: {resp.json()}")
    assert resp.json()["success"] == True
    
    # 改回原密码
    requests.post(f"{BASE_URL}/change_own_password", json={
        "name": TEST_USER,
        "old_password": "new_test123",
        "password": TEST_PWD
    })
    
    print("\n测试查询用户车辆列表...")
    resp = requests.get(f"{BASE_URL}/get_user_vehicles?name={TEST_USER}&limit=10")
    print(f"  响应: {resp.json()}")
    assert resp.json()["success"] == True
    
    print("\n测试查询车辆信息...")
    resp = requests.get(f"{BASE_URL}/get_user_vehicle_info?name={TEST_USER}&vehicle_id={TEST_VEHICLE}")
    print(f"  响应: {resp.json()}")
    assert resp.json()["success"] == True

if __name__ == "__main__":
    test_user_apis()

import requests
import json

BASE_URL = "http://localhost:12344"

def test_verify_user_and_get_role():
    # 测试数据 - 包含各种场景
    test_cases = [
        {
            "name": "root", 
            "password": "123456", 
            "expected_success": True,
            "expected_role": "admin",
            "description": "管理员账号登录"
        },
        {
            "name": "test_user", 
            "password": "test123", 
            "expected_success": True,
            "expected_role": "user",
            "description": "普通用户账号登录"
        },
        {
            "name": "invalid_user", 
            "password": "any_password", 
            "expected_success": False,
            "expected_role": None,
            "description": "不存在的用户登录"
        },
        {
            "name": "root", 
            "password": "wrong_password", 
            "expected_success": False,
            "expected_role": None,
            "description": "密码错误的登录"
        },
        {
            "name": "", 
            "password": "123456", 
            "expected_success": False,
            "expected_role": None,
            "description": "空用户名登录"
        },
        {
            "name": "test_user", 
            "password": "", 
            "expected_success": False,
            "expected_role": None,
            "description": "空密码登录"
        }
    ]
    
    print(f"开始测试登录接口，共 {len(test_cases)} 个测试用例\n")
    
    for i, case in enumerate(test_cases, 1):
        print(f"测试用例 {i}: {case['description']}")
        print(f"  用户名: {case['name']}, 密码: {'*' * len(case['password'])}")
        
        try:
            # 测试POST请求
            post_url = f"{BASE_URL}/verify_user_and_get_role"
            post_data = {
                "name": case["name"],
                "password": case["password"]
            }
            
            post_response = requests.post(
                post_url,
                json=post_data,
                headers={"Content-Type": "application/json"}
            )
            
            # 确保响应是JSON格式
            try:
                post_result = post_response.json()
            except json.JSONDecodeError:
                print(f"错误：响应不是有效的JSON格式")
                print(f"  原始响应: {post_response.text}\n")
                continue
            
            # 验证状态码和结果结构
            print(f"  POST状态码: {post_response.status_code}")
            print(f"  实际结果: {post_result}")
            print(f"  预期success: {case['expected_success']}")
            if case['expected_success']:
                print(f"  预期role: {case['expected_role']}")
            
            # 验证必要的返回字段
            if not all(key in post_result for key in ['success', 'message' if not case['expected_success'] else 'role']):
                print(f"错误：返回数据缺少必要字段")
                print(f"测试失败\n")
                continue
            
            # 验证结果是否符合预期
            if (post_result['success'] == case['expected_success'] and 
                (not case['expected_success'] or post_result['role'] == case['expected_role'])):
                print(f"测试通过\n")
            else:
                print(f"测试失败\n")
                
        except Exception as e:
            print(f"测试出错: {str(e)}\n")

if __name__ == "__main__":
    test_verify_user_and_get_role()
    print("所有测试用例执行完毕")
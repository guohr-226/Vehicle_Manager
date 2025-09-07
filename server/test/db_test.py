import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from vehicle_db import VehicleDB

def print_separator(title):
    """打印分隔线，用于区分不同测试模块"""
    print("\n" + "="*60)
    print(f"=== {title} ===")
    print("="*60)

def test_user_management(db):
    """测试用户管理功能"""
    print_separator("测试用户管理功能")
    
    # 测试添加用户
    print("\n1. 测试添加用户")
    success, msg = db.add_user("test_user", "test_pass")
    print(f"添加普通用户: {'成功' if success else '失败'}, 消息: {msg}")
    
    success, msg = db.add_user("admin_user", "admin_pass", is_admin=True)
    print(f"添加管理员用户: {'成功' if success else '失败'}, 消息: {msg}")
    
    # 测试添加重复用户
    success, msg = db.add_user("test_user", "another_pass")
    print(f"添加重复用户: {'成功' if success else '失败'}, 消息: {msg}")
    
    # 测试用户验证
    print("\n2. 测试用户验证")
    success, user_id, is_admin = db.verify_user("root", "123456")
    print(f"验证默认管理员: {'成功' if success else '失败'}, ID: {user_id}, 是否管理员: {is_admin}")
    
    success, user_id, is_admin = db.verify_user("test_user", "test_pass")
    print(f"验证普通用户: {'成功' if success else '失败'}, ID: {user_id}, 是否管理员: {is_admin}")
    
    success, user_id, is_admin = db.verify_user("test_user", "wrong_pass")
    print(f"验证错误密码: {'成功' if success else '失败'}, ID: {user_id}, 是否管理员: {is_admin}")
    
    # 测试修改密码
    print("\n3. 测试修改密码")
    success, msg = db.change_password("test_user", "test_pass", "new_pass")
    print(f"普通用户修改密码: {'成功' if success else '失败'}, 消息: {msg}")
    
    # 使用新密码验证
    success, user_id, is_admin = db.verify_user("test_user", "new_pass")
    print(f"使用新密码验证: {'成功' if success else '失败'}")
    
    # 管理员修改其他用户密码（无需旧密码）
    success, root_id, _ = db.verify_user("root", "123456")
    if success:
        success, msg = db.change_password("test_user", None, "admin_changed_pass")
        print(f"管理员修改用户密码: {'成功' if success else '失败'}, 消息: {msg}")
    
    # 测试查询用户列表
    print("\n4. 测试查询用户列表")
    success, users, total = db.get_users(limit=10, offset=0)
    if success:
        print(f"查询到 {total} 个用户:")
        for user in users:
            print(f"ID: {user['id']}, 用户名: {user['name']}, 管理员: {user['is_admin']}, 创建时间: {user['created_at']}")
    else:
        print(f"查询失败: {users}")

def test_sensor_management(db):
    """测试传感器管理功能"""
    print_separator("测试传感器管理功能")
    
    # 添加传感器
    print("\n1. 测试添加传感器")
    success, msg = db.add_sensor(
        sensor_id="sensor_entrance",
        location="学校正门",
        description="学校主入口门禁传感器",
        is_active=True,
        is_gate=True
    )
    print(f"添加校门传感器: {'成功' if success else '失败'}, 消息: {msg}")
    
    success, msg = db.add_sensor(
        sensor_id="sensor_library",
        location="图书馆门口",
        description="图书馆入口传感器",
        is_active=True,
        is_gate=False
    )
    print(f"添加图书馆传感器: {'成功' if success else '失败'}, 消息: {msg}")
    
    # 添加重复位置的传感器
    success, msg = db.add_sensor(
        sensor_id="sensor_dup",
        location="学校正门",
        description="重复位置测试"
    )
    print(f"添加重复位置传感器: {'成功' if success else '失败'}, 消息: {msg}")
    
    # 查询传感器状态
    print("\n2. 测试查询传感器状态")
    success, sensors, total = db.get_sensors()
    if success:
        print(f"查询到 {total} 个传感器:")
        for s in sensors:
            print(f"ID: {s['sensor_id']}, 位置: {s['location']}, 激活: {s['is_active']}, 校门: {s['is_gate']}")
    else:
        print(f"查询失败: {sensors}")
    
    # 测试更新传感器状态
    print("\n3. 测试更新传感器状态")
    success, msg = db.update_sensor_status("sensor_library", False)
    print(f"禁用图书馆传感器: {'成功' if success else '失败'}, 消息: {msg}")
    
    # 验证状态更新
    success, status = db.get_sensor_status("sensor_library")
    if success:
        print(f"图书馆传感器当前状态: 激活={status['is_active']}")

def test_vehicle_management(db):
    """测试车辆管理功能"""
    print_separator("测试车辆管理功能")
    
    # 获取测试用户ID
    success, test_user_id, _ = db.verify_user("test_user", "admin_changed_pass")
    if not success:
        print("获取测试用户ID失败，无法进行车辆管理测试")
        return
    
    # 添加车辆
    print("\n1. 测试添加车辆")
    success, msg = db.add_vehicle(
        vehicle_id="ABC123",
        registered_by="test_user",
        is_on_campus=False
    )
    print(f"添加车辆ABC123: {'成功' if success else '失败'}, 消息: {msg}")
    
    success, msg = db.add_vehicle(
        vehicle_id="XYZ789",
        registered_by="test_user",
        is_on_campus=True
    )
    print(f"添加车辆XYZ789: {'成功' if success else '失败'}, 消息: {msg}")
    
    # 添加重复车辆
    success, msg = db.add_vehicle(
        vehicle_id="ABC123",
        registered_by="test_user"
    )
    print(f"添加重复车辆: {'成功' if success else '失败'}, 消息: {msg}")
    
    # 查询车辆列表
    print("\n2. 测试查询车辆列表")
    success, vehicles, total = db.get_vehicles()
    if success:
        print(f"查询到 {total} 辆车:")
        for v in vehicles:
            print(f"车牌: {v['vehicle_id']}, 登记人: {v['registered_by_name']}, 在校: {v['is_on_campus']}, 登记时间: {v['created_at']}")
    else:
        print(f"查询失败: {vehicles}")
    
    # 查询单个车辆状态
    print("\n3. 测试查询单个车辆状态")
    success, status = db.get_vehicle_status("ABC123")
    if success:
        print(f"车辆ABC123状态: 在校={status['is_on_campus']}, 登记人={status['registered_by_name']}")
    else:
        print(f"查询失败: {status}")

def test_passage_records(db):
    """测试通行记录管理功能"""
    print_separator("测试通行记录管理功能")
    
    # 获取传感器ID
    success, sensors, _ = db.get_sensors()
    if not success or len(sensors) == 0:
        print("未找到传感器，无法测试通行记录")
        return
    entrance_sensor_id = sensors[0]['id']  # 使用第一个传感器（校门）
    
    # 添加通行记录（修复原测试中的参数错误，移除direction参数）
    print("\n1. 测试添加通行记录")
    success, msg = db.add_passage_record("ABC123", entrance_sensor_id)
    print(f"车辆ABC123通过校门传感器: {'成功' if success else '失败'}, 消息: {msg}")
    
    # 等待一会，确保时间戳不同
    time.sleep(1)
    
    success, msg = db.add_passage_record("XYZ789", entrance_sensor_id)
    print(f"车辆XYZ789通过校门传感器: {'成功' if success else '失败'}, 消息: {msg}")
    
    time.sleep(1)
    success, msg = db.add_passage_record("ABC123", entrance_sensor_id)
    print(f"车辆ABC123再次通过校门传感器: {'成功' if success else '失败'}, 消息: {msg}")
    
    # 检查车辆状态是否更新（校门传感器会自动反转状态）
    success, status = db.get_vehicle_status("ABC123")
    if success:
        print(f"车辆ABC123当前状态: 在校={status['is_on_campus']} (预期: False)")
    
    # 按车辆查询通行记录
    print("\n2. 测试按车辆查询通行记录")
    success, records, total = db.get_passage_by_vehicle("ABC123")
    if success:
        print(f"车辆ABC123的{total}条通行记录:")
        for r in records:
            print(f"时间: {r['passage_time']}, 位置: {r['location']}, 传感器: {r['sensor_id']}")
    else:
        print(f"查询失败: {records}")
    
    # 按传感器查询通行记录
    print("\n3. 测试按传感器查询通行记录")
    success, records, total = db.get_passage_by_sensor(entrance_sensor_id)
    if success:
        print(f"传感器{entrance_sensor_id}的{total}条通行记录:")
        for r in records:
            print(f"时间: {r['passage_time']}, 车辆: {r['vehicle_id']}, 位置: {r['location']}")
    else:
        print(f"查询失败: {records}")
    
    # 测试删除通行记录（按时间）
    print("\n4. 测试删除通行记录")
    # 先获取第一条记录的时间作为起始时间
    if success and len(records) > 0:
        start_time = records[-1]['passage_time']
        end_time = records[0]['passage_time']
        success, msg = db.delete_passage_records_by_time(start_time, end_time)
        print(f"删除时间范围内的记录: {'成功' if success else '失败'}, 消息: {msg}")
        
        # 验证删除结果
        success, records, total = db.get_passage_by_sensor(entrance_sensor_id)
        print(f"删除后剩余记录数: {total}")

def test_cleanup(db):
    """测试清理功能"""
    print_separator("测试清理功能")
    
    # 删除测试用户（管理员权限）
    success, root_id, _ = db.verify_user("root", "123456")
    if success:
        print("\n1. 删除测试用户")
        success, msg = db.delete_user("test_user", None)  # 管理员删除无需密码
        print(f"删除test_user: {'成功' if success else '失败'}, 消息: {msg}")
        
        print("\n2. 删除测试传感器")
        success, msg = db.delete_sensor("sensor_entrance")
        print(f"删除校门传感器: {'成功' if success else '失败'}, 消息: {msg}")
        
        success, msg = db.delete_sensor("sensor_library")
        print(f"删除图书馆传感器: {'成功' if success else '失败'}, 消息: {msg}")

def main():
    """主测试函数"""
    print("=== 开始数据库功能测试 ===")
    
    # 初始化数据库
    db = VehicleDB()
    # 可修改为实际测试路径
    success = db.initialize("test_vehicle_db.db")
    if not success:
        print("数据库初始化失败，无法进行测试")
        return
    
    try:
        # 运行各项测试
        test_user_management(db)
        test_sensor_management(db)
        test_vehicle_management(db)
        test_passage_records(db)
        test_cleanup(db)
        
        # 测试测试数据初始化功能
        print_separator("测试测试数据初始化")
        db.initialize_test_data()
        print("测试数据已初始化，可手动验证数据库内容")
        
    finally:
        # 关闭线程资源和数据库连接
        db.close_thread_resources()
        db.close()
        print("\n=== 所有测试完成 ===")

if __name__ == "__main__":
    main()
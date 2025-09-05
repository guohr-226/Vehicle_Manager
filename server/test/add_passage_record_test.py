import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from vehicle_db import VehicleDB
import os
import sqlite3

class TestAddPassageRecord(unittest.TestCase):
    def setUp(self):
        """测试前的初始化工作"""
        # 使用临时数据库文件
        self.test_db_path = "vehicle_db_add_passage_record_test.db"
        # 确保之前的测试数据库已删除
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
        # 初始化数据库
        self.db = VehicleDB()
        self.assertTrue(self.db.initialize(self.test_db_path), "数据库初始化失败")
        
        # 添加测试数据
        # 1. 添加测试用户
        self.assertTrue(self.db.add_user("test_admin", "admin123", True)[0], "添加管理员失败")
        _, self.admin_id, _ = self.db.verify_user("test_admin", "admin123")
        self.assertNotEqual(self.admin_id, -1, "验证管理员失败")
        
        # 2. 添加测试车辆
        self.assertTrue(self.db.add_vehicle("TEST001", self.admin_id)[0], "添加车辆TEST001失败")
        self.assertTrue(self.db.add_vehicle("TEST002", self.admin_id)[0], "添加车辆TEST002失败")
        
        # 3. 添加测试传感器（校门和普通传感器）
        self.assertTrue(self.db.add_sensor("GATE001", "东门", "入口大门", True, True)[0], "添加东门传感器失败")
        self.assertTrue(self.db.add_sensor("GATE002", "西门", "出口大门", True, True)[0], "添加西门传感器失败")
        self.assertTrue(self.db.add_sensor("SENSOR001", "停车场A区", "普通传感器", True, False)[0], "添加停车场传感器失败")
        
        # 获取传感器ID - 修正：get_sensor_status返回的是二元组
        success, gate1_data = self.db.get_sensor_status("GATE001")
        self.assertTrue(success, "获取东门传感器失败")
        success, gate2_data = self.db.get_sensor_status("GATE002")
        self.assertTrue(success, "获取西门传感器失败")
        success, sensor1_data = self.db.get_sensor_status("SENSOR001")
        self.assertTrue(success, "获取停车场传感器失败")
        
        self.gate1_id = gate1_data["id"]
        self.gate2_id = gate2_data["id"]
        self.sensor1_id = sensor1_data["id"]

    def tearDown(self):
        """测试后的清理工作"""
        self.db.close()
        self.db.close_thread_resources()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_add_passage_with_gate_sensor(self):
        """测试通过校门传感器时的车辆状态变化"""
        # 初始状态应该是不在校内
        _, vehicle_status = self.db.get_vehicle_status("TEST001")
        self.assertFalse(vehicle_status["is_on_campus"], "车辆初始状态应为不在校内")
        
        # 第一次通过东门（校门传感器）- 应该进入校内
        result, msg = self.db.add_passage_record("TEST001", self.gate1_id)
        self.assertTrue(result, f"添加东门通行记录失败: {msg}")
        
        # 检查状态是否变为在校内
        _, vehicle_status = self.db.get_vehicle_status("TEST001")
        self.assertTrue(vehicle_status["is_on_campus"], "车辆通过东门后应在校内")
        
        # 第二次通过西门（校门传感器）- 应该离开校内
        result, msg = self.db.add_passage_record("TEST001", self.gate2_id)
        self.assertTrue(result, f"添加西门通行记录失败: {msg}")
        
        # 检查状态是否变为不在校内
        _, vehicle_status = self.db.get_vehicle_status("TEST001")
        self.assertFalse(vehicle_status["is_on_campus"], "车辆通过西门后应不在校内")

    def test_add_passage_with_normal_sensor(self):
        """测试通过普通传感器时的车辆状态不变"""
        # 先让车辆进入校内
        self.db.add_passage_record("TEST002", self.gate1_id)
        _, vehicle_status = self.db.get_vehicle_status("TEST002")
        self.assertTrue(vehicle_status["is_on_campus"], "车辆应在校内")
        
        # 通过停车场传感器（非校门）
        result, msg = self.db.add_passage_record("TEST002", self.sensor1_id)
        self.assertTrue(result, f"添加停车场通行记录失败: {msg}")
        
        # 检查状态是否保持不变
        _, vehicle_status = self.db.get_vehicle_status("TEST002")
        self.assertTrue(vehicle_status["is_on_campus"], "通过普通传感器后状态应不变")

    def test_add_passage_with_invalid_vehicle(self):
        """测试添加不存在车辆的通行记录"""
        result, msg = self.db.add_passage_record("INVALID001", self.gate1_id)
        self.assertFalse(result, "添加不存在车辆的记录应失败")
        self.assertEqual(msg, "车辆不存在", "错误信息不正确")

    def test_add_passage_with_invalid_sensor(self):
        """测试添加不存在传感器的通行记录"""
        result, msg = self.db.add_passage_record("TEST001", 9999)  # 9999是不存在的传感器ID
        self.assertFalse(result, "添加不存在传感器的记录应失败")
        self.assertEqual(msg, "传感器不存在", "错误信息不正确")

    def test_passage_record_count(self):
        """测试通行记录是否正确计数"""
        # 添加多条记录
        self.db.add_passage_record("TEST001", self.gate1_id)
        self.db.add_passage_record("TEST001", self.sensor1_id)
        self.db.add_passage_record("TEST001", self.gate2_id)
        
        # 检查记录总数
        success, records, total = self.db.get_passage_by_vehicle("TEST001")
        self.assertTrue(success, "查询通行记录失败")
        self.assertEqual(total, 3, "通行记录数量不正确")
        self.assertEqual(len(records), 3, "返回的记录数量不正确")

if __name__ == "__main__":
    unittest.main()
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from vehicle_db import VehicleDB  # 假设数据库类在vehicle_db.py中
import json

def main():
    # 初始化数据库连接
    db = VehicleDB()
    if not db.initialize("/home/ghr226/iot/server/vehicle_db.db"):
        print("数据库初始化失败，无法继续操作")
        return

    try:
        # 获取所有用户信息
        print("===== 开始获取用户信息 =====")
        users = []
        offset = 0
        limit = 20  # 分页查询每页数量
        
        while True:
            success, data, total = db.get_users(limit=limit, offset=offset)
            if not success:
                print(f"获取用户信息失败: {data}")
                break
            
            users.extend(data)
            offset += limit
            
            # 当已获取数量达到总数时停止查询
            if len(users) >= total:
                break
        
        print(f"共获取到 {len(users)} 个用户信息")

        # 获取所有车辆信息
        print("\n===== 开始获取车辆信息 =====")
        vehicles = []
        offset = 0
        
        while True:
            success, data, total = db.get_vehicles(limit=limit, offset=offset)
            if not success:
                print(f"获取车辆信息失败: {data}")
                break
            
            vehicles.extend(data)
            offset += limit
            
            if len(vehicles) >= total:
                break
        
        print(f"共获取到 {len(vehicles)} 条车辆信息")

        # 获取所有传感器信息
        print("\n===== 开始获取传感器信息 =====")
        sensors = []
        offset = 0
        
        while True:
            success, data, total = db.get_sensors(limit=limit, offset=offset)
            if not success:
                print(f"获取传感器信息失败: {data}")
                break
            
            sensors.extend(data)
            offset += limit
            
            if len(sensors) >= total:
                break
        
        print(f"共获取到 {len(sensors)} 个传感器信息")

        # 将结果保存为JSON文件
        result = {
            "users": users,
            "vehicles": vehicles,
            "sensors": sensors,
            "timestamp": str(db._retry_operation(lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        }

        with open("db_export.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print("\n数据已成功导出到 db_export.json 文件")

    except Exception as e:
        print(f"操作过程中发生错误: {str(e)}")
    finally:
        # 清理资源
        db.close_thread_resources()
        db.close()
        print("\n数据库连接已关闭")

if __name__ == "__main__":
    from datetime import datetime  # 延迟导入，仅在主程序运行时需要
    main()

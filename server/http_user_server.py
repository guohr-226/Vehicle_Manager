import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from vehicle_db import VehicleDB

class UserHTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.db = VehicleDB()
        if not self.db.initialize():
            raise RuntimeError("数据库初始化失败")
        super().__init__(*args, **kwargs)

    def _set_response(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()

    def _parse_post_data(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            return json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            return None

    def _get_params(self):
        """获取请求参数（GET从查询字符串，POST从JSON数据）"""
        if self.command == 'GET':
            params = {}
            if '?' in self.path:
                path, query = self.path.split('?', 1)
                for param in query.split('&'):
                    if '=' in param:
                        k, v = param.split('=', 1)
                        params[k] = v
            return params
        else:  # POST
            return self._parse_post_data() or {}

    def _verify_user_exists(self, name):
        """验证用户是否存在"""
        success, users, _ = self.db.get_users(limit=1000)
        if not success:
            return False
        return any(u['name'] == name for u in users)

    def _get_user_id(self, name):
        """获取用户ID"""
        success, users, _ = self.db.get_users(limit=1000)
        if not success:
            return None
        for user in users:
            if user['name'] == name:
                return user['id']
        return None

    def _is_vehicle_owned_by_user(self, vehicle_id, name):
        """验证车辆是否属于用户"""
        success, vehicle_info = self.db.get_vehicle_status(vehicle_id)
        if not success or not vehicle_info:
            return False
        return vehicle_info.get('registered_by_name') == name

    def do_GET(self):
        self._handle_request()

    def do_POST(self):
        self._handle_request()

    def _handle_request(self):
        path = self.path.split('?')[0]
        params = self._get_params()
        name = params.get('name')
        
        # 验证用户是否存在
        if not name or not self._verify_user_exists(name):
            response = {"success": False, "message": "用户不存在"}
            self._set_response(401)
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
            
        if path == '/get_current_user_info':
            # 获取用户信息
            success, users, _ = self.db.get_users(limit=1000)
            if not success:
                response = {"success": False, "message": "查询失败"}
                self._set_response(500)
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            user_info = next((u for u in users if u['name'] == name), None)
            if user_info:
                # 移除敏感信息
                user_info.pop('id', None)
                response = {"success": True, "data": user_info}
            else:
                response = {"success": False, "message": "用户不存在"}
                
            self._set_response()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif path == '/change_own_password':
            old_password = params.get('old_password')
            new_password = params.get('password')
            
            if not old_password or not new_password:
                response = {"success": False, "message": "旧密码和新密码为必填项"}
                self._set_response(400)
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            success, message = self.db.change_password(name, old_password, new_password)
            response = {"success": success, "message": message}
            self._set_response()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif path == '/get_user_vehicles':
            cursor = int(params.get('cursor', 0))
            limit = min(int(params.get('limit', 10)), 100)
            user_id = self._get_user_id(name)
            
            if not user_id:
                response = {"success": False, "message": "用户不存在"}
                self._set_response(401)
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            # 获取用户名下的车辆
            success, vehicles, total = self.db.get_vehicles(limit, cursor)
            if not success:
                response = {"success": False, "message": vehicles}
                self._set_response(500)
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            # 过滤出当前用户的车辆
            user_vehicles = [v for v in vehicles if v['registered_by_name'] == name]
            
            next_cursor = cursor + limit if cursor + limit < total else None
            response = {
                "success": True,
                "data": user_vehicles,
                "total": len(user_vehicles),
                "next_cursor": next_cursor,
                "limit": limit
            }
            
            self._set_response()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif path == '/get_user_vehicle_info':
            vehicle_id = params.get('vehicle_id')
            user_id = self._get_user_id(name)
            
            if not vehicle_id:
                response = {"success": False, "message": "车辆ID为必填项"}
                self._set_response(400)
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
            
            # 验证车辆是否属于用户
            if not self._is_vehicle_owned_by_user(vehicle_id, name):
                response = {"success": False, "message": "无权访问该车辆信息"}
                self._set_response(403)
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            # 获取车辆基本信息
            success, vehicle_info = self.db.get_vehicle_status(vehicle_id)
            if not success or not vehicle_info:
                response = {"success": False, "message": "车辆不存在"}
                self._set_response(404)
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            # 获取最后一次通行记录
            success, records, _ = self.db.get_passage_by_vehicle(vehicle_id, limit=1)
            if success and records:
                last_record = records[0]
                vehicle_info['last_location'] = last_record['location']
                vehicle_info['last_time'] = last_record['passage_time']
                
            response = {"success": True, "data": vehicle_info}
            self._set_response()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({"success": False, "message": "接口不存在"}).encode('utf-8'))

def run_user_server():
    server_address = ('', 12346)
    httpd = HTTPServer(server_address, UserHTTPHandler)
    print('用户服务器启动，监听端口 12346...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('用户服务器已关闭')

if __name__ == '__main__':
    run_user_server()
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from vehicle_db import VehicleDB

class LogicHTTPHandler(BaseHTTPRequestHandler):
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

    def do_GET(self):
        self._handle_request()

    def do_POST(self):
        self._handle_request()

    def _handle_request(self):
        path = self.path.split('?')[0]
        params = self._get_params()
        
        if path == '/verify_user_and_get_role':
            name = params.get('name')
            password = params.get('password')
            
            if not name or not password:
                response = "error"
                self._set_response(400)
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            # 验证用户
            success, user_id, is_admin = self.db.verify_user(name, password)

            # print("verify_user done", "success:", success,"user_id:", user_id, "is_admin:", is_admin)

            if success and user_id != -1:
                role = "admin" if is_admin else "user"
                response = role
            else:
                response = "error"
                
            self._set_response()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        else:
            self._set_response(404)
            self.wfile.write(json.dumps("error").encode('utf-8'))

def run_logic_server():
    server_address = ('', 12344)
    httpd = HTTPServer(server_address, LogicHTTPHandler)
    print('逻辑服务器启动，监听端口 12344...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('逻辑服务器已关闭')

if __name__ == '__main__':
    run_logic_server()
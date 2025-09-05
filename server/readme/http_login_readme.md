| 接口路径 | 请求方法 | 必要参数 | 可选参数 | 功能描述 | 返回数据 |
|---------|---------|---------|---------|---------|---------|
| `/verify_user_and_get_role` | GET/POST | `name`、`password` | - | 登录接口 | 成功: `{"success": true, "role": "user/admin"}`；失败: `{"success": false, "message": "错误信息"}` |

1. **数据格式**：所有请求和响应均使用 JSON 格式，编码为 UTF-8
2. **通信协议**：基于 HTTP 协议，服务器监听本地 12344 端口
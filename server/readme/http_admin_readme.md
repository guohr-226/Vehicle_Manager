| 功能分类       | 接口路径                  | 请求方法 | 必要参数                                  | 可选参数                                      | 功能描述                                  | 响应内容格式                                  | 状态码说明 |
|----------------|---------------------------|----------|-------------------------------------------|-----------------------------------------------|-------------------------------------------|-----------------------------------------------|------------|
| **用户管理**   | `/add_user`               | POST     | `name`（用户名）、`password`（密码）      | `is_admin`（是否为管理员，默认false）         | 添加新用户                                | `{"success": 布尔值, "message": 字符串}`       | 200：成功；400：参数缺失                     |
|                | `/change_password`        | POST     | `name`（用户名）、`password`（新密码）    | -                                             | 修改用户密码（无需旧密码）                | `{"success": 布尔值, "message": 字符串}`       | 200：成功；400：参数缺失                     |
|                | `/delete_user`            | POST     | `name`（用户名）                          | -                                             | 删除指定用户                              | `{"success": 布尔值, "message": 字符串}`       | 200：成功；400：参数缺失                     |
|                | `/get_user_info`          | GET      | `name`（用户名，通过URL参数传递）         | -                                             | 查询指定用户的详细信息                    | `{"success": 布尔值, "data": 用户信息对象 \| null, "message": 字符串}` | 200：成功；400：参数缺失                     |
|                | `/get_users`              | GET      | -                                         | `cursor`（分页游标，默认0）、`limit`（每页数量，默认20，最大100） | 分页拉取用户列表                          | `{"success": 布尔值, "data": 用户列表数组, "total": 总数, "next_cursor": 下一页游标 \| null, "limit": 每页数量, "message": 字符串}` | 200：成功                                    |
| **传感器管理** | `/add_or_update_sensor`   | POST     | `sensor_id`（传感器ID）、`location`（位置）| `description`（描述）、`is_active`（是否激活，默认true）、`is_gate`（是否为校门，默认false） | 添加新传感器或更新已有传感器信息          | `{"success": 布尔值, "message": 字符串}`       | 200：成功；400：参数缺失                     |
|                | `/delete_sensor`          | POST     | `sensor_id`（传感器ID）                   | -                                             | 删除指定传感器                            | `{"success": 布尔值, "message": 字符串}`       | 200：成功；400：参数缺失                     |
|                | `/get_sensor_info`        | GET      | `sensor_id`（传感器ID，通过URL参数传递）  | -                                             | 查询指定传感器的详细信息                  | `{"success": 布尔值, "data": 传感器信息对象 \| null, "message": 字符串}` | 200：成功；400：参数缺失                     |
|                | `/get_sensors`            | GET      | -                                         | `cursor`（分页游标，默认0）、`limit`（每页数量，默认20，最大100） | 分页拉取传感器列表                        | `{"success": 布尔值, "data": 传感器列表数组, "total": 总数, "next_cursor": 下一页游标 \| null, "limit": 每页数量, "message": 字符串}` | 200：成功                                    |
| **车辆管理**   | `/add_vehicle`            | POST     | `vehicle_id`（车辆ID）、`registered_by`（登记人ID） | -                                             | 添加新车辆并关联登记人                    | `{"success": 布尔值, "message": 字符串}`       | 200：成功；400：参数缺失                     |
|                | `/delete_vehicle`         | POST     | `vehicle_id`（车辆ID）                    | -                                             | 删除指定车辆                              | `{"success": 布尔值, "message": 字符串}`       | 200：成功；400：参数缺失                     |
|                | `/get_vehicle_info`       | GET      | `vehicle_id`（车辆ID，通过URL参数传递）   | -                                             | 查询指定车辆的详细信息                    | `{"success": 布尔值, "data": 车辆信息对象 \| null, "message": 字符串}` | 200：成功；400：参数缺失                     |
|                | `/get_vehicles`           | GET      | -                                         | `cursor`（分页游标，默认0）、`limit`（每页数量，默认20，最大100） | 分页拉取车辆列表                          | `{"success": 布尔值, "data": 车辆列表数组, "total": 总数, "next_cursor": 下一页游标 \| null, "limit": 每页数量, "message": 字符串}` | 200：成功                                    |

### 补充说明
1. 所有接口请求/响应数据格式均为JSON，编码为UTF-8
2. 分页逻辑中，`next_cursor` 为 `null` 时表示没有更多数据
3. 未列出的路径请求将返回 `404` 状态码，响应格式为 `{"success": false, "message": "接口不存在"}`
4. 查询类接口（`get_*`）成功时返回 `data` 字段，失败时返回 `message` 字段说明原因
5. 操作类接口（`add_*`/`delete_*`/`change_*`）始终返回 `message` 字段说明操作结果
6. 分页逻辑：
   - `cursor`：分页起始位置（偏移量），默认为 0
   - `limit`：每页最大数量，默认 20，最大 100
   - 响应包含 `next_cursor`，为 `null` 时表示没有更多数据

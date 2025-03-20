# 后端主入口文件
from flask import Flask
from app.routes.temperature_routes import temperature_bp
# 导入其他路由...

# 创建Flask应用
app = Flask(__name__)

# 注册蓝图(路由)
app.register_blueprint(temperature_bp, url_prefix='/api')
# 注册其他蓝图...

# 配置跨域请求(CORS)
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

# 主路由
@app.route('/')
def index():
    return {"status": "API服务运行正常"}

# 启动服务器
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



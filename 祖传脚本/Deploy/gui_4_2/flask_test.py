from flask import Flask, request, jsonify

app = Flask("franka_task_finished")

def execute_specific_function(obj_value):

    print("obj_value",obj_value)
    return f"{obj_value} recieved"


def handle_obj():
    # 获取客户端发送的JSON数据
    data = request.get_json()
    
    # 检查是否包含prompt字段
    if not data or 'obj' not in data:
        return jsonify({'error': 'Missing obj field'}), 400
    
    obj_value = data['obj']
    result = execute_specific_function(obj_value)
    return jsonify({'status': 'success', 'message': result}), 200

app.add_url_rule('/api/obj', view_func=handle_obj, methods=['POST'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009)
    
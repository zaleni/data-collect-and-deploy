import socket
import pickle
import numpy as np


class ModelClient:
    """模型推理客户端"""
    
    def __init__(self, host='127.0.0.1', port=9999, timeout=30):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None
        self.connect()
    
    def connect(self):
        """连接到服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            print(f"已连接到模型服务器: {self.host}:{self.port}")
        except Exception as e:
            print(f"连接服务器失败: {e}")
            raise
    
    def send_request(self, request):
        """发送请求并接收响应"""
        try:
            # 序列化请求
            request_bytes = pickle.dumps(request)
            request_size = len(request_bytes).to_bytes(4, byteorder='big')
            
            # 发送请求
            self.socket.sendall(request_size + request_bytes)
            
            # 接收响应大小
            response_size_bytes = self.recv_all(4)
            if not response_size_bytes:
                raise ConnectionError("服务器断开连接")
            
            response_size = int.from_bytes(response_size_bytes, byteorder='big')
            
            # 接收响应数据
            response_bytes = self.recv_all(response_size)
            if not response_bytes:
                raise ConnectionError("服务器断开连接")
            
            # 反序列化响应
            response = pickle.loads(response_bytes)
            return response
            
        except Exception as e:
            print(f"请求失败: {e}")
            raise
    
    def recv_all(self, n):
        """接收指定字节数的数据"""
        data = bytearray()
        while len(data) < n:
            packet = self.socket.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return bytes(data)
    
    def update_obs(self, observation):
        """更新观测数据"""
        request = {
            'command': 'update_obs',
            'observation': observation
        }
        response = self.send_request(request)
        return response['status'] == 'success'
    
    def predict_action(self, observation):
        """预测动作"""
        request = {
            'command': 'predict_action',
            'observation': observation
        }
        response = self.send_request(request)
        
        if response['status'] == 'success' and response['action'] is not None:
            return np.array(response['action'])
        return None
    
    def ping(self):
        """检查服务器是否在线"""
        try:
            request = {'command': 'ping'}
            response = self.send_request(request)
            return response['status'] == 'alive'
        except:
            return False
    
    def close(self):
        """关闭连接"""
        if self.socket:
            self.socket.close()
            print("已断开与服务器的连接")
    
    def __del__(self):
        self.close()
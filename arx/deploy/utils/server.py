import argparse
import torch
import numpy as np
import sys
import yaml
import json
import socket
import pickle
import threading

project_root = "/home/go2/ARX_X5/H_RDT"
sys.path.append(project_root)

# 直接导入 HRDTInference
sys.path.append("/home/go2/ARX_X5/inference/utils")
from model_inference import HRDTInference


class ModelServer:
    """模型推理服务器"""
    
    def __init__(self, args, host='127.0.0.1', port=9999):
        self.host = host
        self.port = port
        self.args = args
        
        # 初始化模型 - 使用 HRDTInference
        print("=" * 60)
        print("正在加载模型...")
        self.model = HRDTInference(args)
        print("模型加载完成!")
        print("=" * 60)
        
        # 服务器socket
        self.server_socket = None
        self.running = False
        
    def start(self):
        """启动服务器"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        
        print(f"模型服务器已启动: {self.host}:{self.port}")
        print("等待客户端连接...")
        
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"客户端已连接: {address}")
                
                # 为每个客户端创建新线程
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"接受连接错误: {e}")
    
    def handle_client(self, client_socket, address):
        """处理客户端请求"""
        try:
            while self.running:
                # 接收数据长度
                data_size_bytes = self.recv_all(client_socket, 4)
                if not data_size_bytes:
                    break
                
                data_size = int.from_bytes(data_size_bytes, byteorder='big')
                
                # 接收实际数据
                data_bytes = self.recv_all(client_socket, data_size)
                if not data_bytes:
                    break
                
                # 解析请求
                request = pickle.loads(data_bytes)
                command = request.get('command')
                
                # 处理不同命令
                if command == 'update_obs':
                    observation = request['observation']
                    self.model.update_obs(observation)
                    response = {'status': 'success'}
                    
                elif command == 'predict_action':
                    observation = request['observation']
                    action = self.model.predict_action(observation)
                    response = {
                        'status': 'success',
                        'action': action.tolist() if action is not None else None
                    }
                    
                elif command == 'ping':
                    response = {'status': 'alive'}
                    
                else:
                    response = {'status': 'error', 'message': 'Unknown command'}
                
                # 发送响应
                response_bytes = pickle.dumps(response)
                response_size = len(response_bytes).to_bytes(4, byteorder='big')
                client_socket.sendall(response_size + response_bytes)
                
        except Exception as e:
            print(f"处理客户端 {address} 错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            client_socket.close()
            print(f"客户端 {address} 已断开")
    
    def recv_all(self, sock, n):
        """接收指定字节数的数据"""
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return bytes(data)
    
    def stop(self):
        """停止服务器"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("服务器已停止")


def get_arguments():
    parser = argparse.ArgumentParser()
    
    # 模型配置 - 参考 hrdt_infer.py
    parser.add_argument('--config_path', type=str, 
                        default='/home/go2/ARX_X5/checkpoint/hrdt_finetune_real_robot_14d.yaml',
                        help='Path to model config file')
    parser.add_argument('--pretrained_model_path', type=str,
                        default='/home/go2/ARX_X5/checkpoint/arrange_umbrella/hrdt_14d_norm/checkpoint-15000',
                        help='Path to pretrained model')
    parser.add_argument('--lang_embeddings_path', type=str,
                        default='/home/go2/ARX_X5/checkpoint/arrange_umbrella/umb_hrdt_14d_finetune_norm/lang_embeddings/arrange_the_umbrellas.pt',
                        help='Path to language embeddings')
    parser.add_argument('--stat_file_path', type=str,
                        default='/home/go2/ARX_X5/checkpoint/arrange_the_umbrellas.json',
                        help='Path to statistics file')
    
    parser.add_argument('--runner_type', type=str, default='default',
                        choices=['default', '7d_selective', '14d_selective'])
    parser.add_argument('--training_mode', type=str, default='lang')
    parser.add_argument('--chunk_size', type=int, default=16)
    parser.add_argument('--model_dimension', type=int, default=14, choices=[7, 14, 62])
    parser.add_argument('--noise_strategy', type=str, default='gaussian',
                        choices=['zero', 'gaussian', 'uniform'])
    parser.add_argument('--noise_scale', type=float, default=1.0)
    parser.add_argument('--normalize_actions', action='store_true')
    parser.add_argument('--use_depth_image', action='store_true')
    parser.add_argument('--camera_names', type=str, default=['left_wrist', 'head'])
    
    # 服务器配置
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Server host address')
    parser.add_argument('--port', type=int, default=9999,
                        help='Server port')
    
    return parser.parse_args()


if __name__ == "__main__":
    args = get_arguments()
    
    server = ModelServer(args, host=args.host, port=args.port)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n正在关闭服务器...")
        server.stop()
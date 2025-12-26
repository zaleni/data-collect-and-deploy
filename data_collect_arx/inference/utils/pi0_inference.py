#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import yaml
import time
import json

import numpy as np
import torch
import cv2
from PIL import Image as PImage
project_root = "/home/pc3/deploy/openpi/packages/openpi-client/src"
sys.path.append(project_root)

from openpi_client import websocket_client_policy as _websocket_client_policy
# Import model components - use relative path


class PI0Inference:
    """H-RDT model inference class"""
    
    def __init__(self, args):
        self.args = args
        self.normalize_actions=args.normalize_actions
        # self.use_62d_model=args.use_62d_model
        self.noise_strategy = args.noise_strategy
        self.noise_scale=args.noise_scale
        self.prompt = args.prompt
        print("norm",args.normalize_actions)

        # Load action normalization statistics
        if os.path.exists(args.stat_file_path):
            with open(args.stat_file_path, 'r') as file:
                stat = json.load(file)
            self.action_min = np.array(stat['real_robot']['min'])
            self.action_max = np.array(stat['real_robot']['max'])
        else:
            print(f"Warning: Statistics file not found at {args.stat_file_path}")
            self.action_min = None
            self.action_max = None
        
        self.model=self.make_policy(args)
        print(f"PI0 inference initialized successfully")

    def make_policy(self, args):
        model = _websocket_client_policy.WebsocketClientPolicy(
            host="0.0.0.0",
            port="8000",
        )
        return model
    
    def generate_human_noise(self, batch_size=1):
        """生成48D人类动作噪声"""
        if self.noise_strategy == "gaussian":
            return torch.randn(batch_size, 48) * self.noise_scale
        elif self.noise_strategy == "uniform":
            return torch.rand(batch_size, 48) * 2 - 1
        else:  # zero
            return torch.zeros(batch_size, 48)
    
    def normalize_action(self, action):
        """
        Normalize action values from original range to [-1, 1]

        Args:
            action: Action array to normalize

        Returns:
            Normalized action array
        """
        if not self.normalize_actions:
            return action

        # Ensure action_min and action_max are numpy arrays
        if not isinstance(self.action_min, np.ndarray):
            self.action_min = np.array(self.action_min)
        if not isinstance(self.action_max, np.ndarray):
            self.action_max = np.array(self.action_max)

        # Avoid division by zero
        action_range = self.action_max - self.action_min
        action_range = np.where(action_range == 0, 1.0, action_range)

        # Normalize to [-1, 1]
        normalized_action = 2.0 * (action - self.action_min) / action_range - 1.0

        return normalized_action

    def denormalize_action(self, normalized_action):
        """
        Denormalize action values from [-1, 1] back to original range

        Args:
            normalized_action: Normalized action array

        Returns:
            Denormalized action array
        """
        if not self.normalize_actions:
            return normalized_action

        # Ensure action_min and action_max are numpy arrays
        if not isinstance(self.action_min, np.ndarray):
            self.action_min = np.array(self.action_min)
        if not isinstance(self.action_max, np.ndarray):
            self.action_max = np.array(self.action_max)

        # Avoid division by zero
        action_range = self.action_max - self.action_min
        action_range = np.where(action_range == 0, 1.0, action_range)

        # Denormalize from [-1, 1]
        action = (normalized_action + 1.0) * 0.5 * action_range + self.action_min

        return action

    
    def predict_action(self, observation):

        # example_observation = {
        #     "state":observation['qpos'],
        #     "image": observation['images']["cam_thirdPerson"],
        #     "wrist_image":observation['images']["cam_wrist"],
        #     "prompt": self.prompt,
        # }
        result = self.model.infer(observation)
        action = result["actions"]
        return np.array(action)
    

        # if self.model_dimension == 62:
        #       normalized_actions = normalized_actions[:, 48:]  # 只取后14D真实数据
   
        # joint_actions = self.denormalize_action(normalized_actions)

        # # Apply gripper adjustment: subtract 0.3 from 7th dimension (index 6) and 14th dimension (index 13)
        # # joint_actions[:, 6] -= 0.3   # Left arm gripper (7th dimension)
        # # joint_actions[:, 13] -= 0.3  # Right arm gripper (14th dimension)
        # # print(f"Applied gripper adjustment: -0.3 to dimensions 7 and 14")
        
        # return joint_actions 
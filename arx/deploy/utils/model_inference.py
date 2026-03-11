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

# Import model components - use relative path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../H_RDT'))
sys.path.append(project_root)
from models.hrdt_runner import HRDTRunner
from models.hrdt_runner_7d_selective import HRDTRunner62Dselective7D
from models.hrdt_runner_62d_selective_14d import HRDTRunner62Dselective14D
from models.encoder.dinosiglip_vit import DinoSigLIPViTBackbone


class HRDTInference:
    """H-RDT model inference class"""
    
    def __init__(self, args):
        self.args = args
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.dtype = torch.bfloat16
        self.training_mode = args.training_mode
        self.normalize_actions=args.normalize_actions
        # self.use_62d_model=args.use_62d_model
        self.runner_type = args.runner_type
        self.model_dimension = args.model_dimension
        self.noise_strategy = args.noise_strategy
        self.noise_scale=args.noise_scale
        print("pretrained_model_path",args.pretrained_model_path)
        print("model_dimension",args.model_dimension)
        print("norm",args.normalize_actions)
        # Load model config
        with open(args.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
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
            
        # Load vision encoder
        self.load_vision_encoder()
        
        # Load H-RDT model
        self.load_hrdt_model()
        
        # Load language embeddings
        self.load_embeddings()
        
        # Initialize observation cache
        self.obs_cache = []
        self.max_obs_cache_size = self.config['common']['img_history_size']
        
        print(f"H-RDT inference initialized successfully in {self.training_mode} mode")
    
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
    def load_vision_encoder(self):
        """Load vision encoder"""
        # Use relative path for vision backbone
        vision_backbone_path = os.path.join(project_root, 'bak/dino-siglip')
        print(f"Loading vision encoder from: {vision_backbone_path}")
        
        self.vision_encoder = DinoSigLIPViTBackbone(
            vision_backbone_id="dino-siglip",
            image_resize_strategy="letterbox" 
                if self.config["dataset"]["image_aspect_ratio"] == "pad" 
                else "resize-naive",
            default_image_size=384
        )
        self.vision_encoder.to(self.device, dtype=self.dtype)
        self.vision_encoder.eval()
        self.image_transform = self.vision_encoder.get_image_transform()
        
    def load_hrdt_model(self):
        """Load H-RDT model"""
        state_dim = self.config["common"]["state_dim"]
        action_dim = self.config["common"]["action_dim"]
        pred_horizon = self.config["common"]["action_chunk_size"]
        
        # Create H-RDT model
        if self.runner_type == '7d_selective':
            RunnerClass = HRDTRunner62Dselective7D
            print("Using HRDTRunner62Dselective7D")
        elif self.runner_type == '14d_selective':
            RunnerClass = HRDTRunner62Dselective14D
            print("Using HRDTRunner62Dselective14D")
        else:
            RunnerClass = HRDTRunner
            print("Using default HRDTRunner")


        self.policy = RunnerClass.from_pretrained(
            pretrained_model_name_or_path=self.args.pretrained_model_path,
            state_dim=state_dim,
            action_dim=action_dim,
            pred_horizon=pred_horizon,
            config=self.config["model"],
            act_pos_emb_config=[
                ("state", 1),
                ("action", pred_horizon),
            ],
            img_pos_emb_config=[
                ("image", (self.config["common"]["img_history_size"], 
                          2,  # 3 separate camera views
                          -self.vision_encoder.num_patches)),
            ],
            lang_pos_emb_config=[
                ("lang", -self.config["dataset"]["tokenizer_max_length"]),
            ],
            max_img_len=self.config["common"]["img_history_size"] * self.vision_encoder.num_patches*2,
            max_lang_len=self.config["dataset"]["tokenizer_max_length"],
            training_mode=self.training_mode,
            dtype=self.dtype,
        )
        
        self.policy.to(self.device, dtype=self.dtype).eval()
        print("H-RDT model loaded successfully")
    
    def load_embeddings(self):
        """Load languageembeddings"""
        self.lang_tokens = None
        self.lang_attn_mask = None
        
        if self.training_mode == 'lang':
            # Load pre-encoded language embeddings
            if hasattr(self.args, 'lang_embeddings_path') and self.args.lang_embeddings_path:
                lang_embed_path = self.args.lang_embeddings_path
            else:
                # Use relative path for default embeddings location
                lang_embed_path = os.path.join(project_root, f'utils/lang_embeddings/{self.args.task_name}.pt')
            
            if os.path.exists(lang_embed_path):
                embedding_data = torch.load(lang_embed_path, map_location=self.device)
                embeddings = embedding_data.get('embeddings', None)
                if embeddings is not None:
                    if embeddings.dim() == 3:
                        embeddings = embeddings.squeeze(0)
                    self.lang_tokens = embeddings.to(dtype=self.dtype)
                    self.lang_attn_mask = torch.ones(self.lang_tokens.shape[:1], dtype=torch.bool, device=self.device)
                    print(f"Loaded language embeddings from: {lang_embed_path}")
                    print(f"Language token shape: {self.lang_tokens.shape}")
                else:
                    print(f"No 'embeddings' key found in {lang_embed_path}")
            else:
                print(f"Language embedding not found: {lang_embed_path}")
    
    def update_obs(self, observation):
        """Update observation cache"""
        # Process observation
        processed_obs = {
            'agent_pos': None,
            'images': {'head_cam': None, 'left_cam': None, 'right_cam': None}
        }
        
        # Process state information
        if observation['puppet_left'] is not None and observation['puppet_right'] is not None:
            left_pos = np.array(observation['puppet_left'])
            right_pos = np.array(observation['puppet_right'])
            if self.model_dimension == 7:
                agent_pos = left_pos
            else:
                agent_pos = np.concatenate([left_pos, right_pos])
            # Normalize if statistics available
            # if self.action_min is not None and self.action_max is not None:
            #     agent_pos[:6] = (agent_pos[:6]  - self.action_min[:6] ) / (self.action_max[:6]  - self.action_min[:6] )
            # processed_obs['agent_pos'] = agent_pos
            print("agent_pos before normalization:",agent_pos)
            
            # print("agent_pos after normalization:",agent_pos)
            agent_pos = self.normalize_action(agent_pos)


            if self.model_dimension == 14:
                # 14D model, use both arms
                agent_pos[7:] = 0.0
                # pass
            elif self.model_dimension == 62 :  
                # 62D model, add 48D noise to both arms
                agent_pos[7:] = 0.0
                human_noise = self.generate_human_noise(batch_size=1).numpy().squeeze(0)
                agent_pos = np.concatenate([human_noise,agent_pos])  # 48D噪声  + 14D真实数据

            processed_obs['agent_pos'] = agent_pos
            print("agent_pos after normalization:",agent_pos)

        # Process images separately (no combining)
        if observation['images']['head_cam'] is not None:
            processed_obs['images']['head_cam'] = observation['images']['head_cam']
        if observation['images']['left_cam'] is not None:
            processed_obs['images']['left_cam'] = observation['images']['left_cam']
        if observation['images']['right_cam'] is not None:
            processed_obs['images']['right_cam'] = observation['images']['right_cam']
        
        self.obs_cache.append(processed_obs)
        if len(self.obs_cache) > self.max_obs_cache_size:
            self.obs_cache.pop(0)
    
    def create_three_view_image(self, head_cam, left_cam, right_cam):
        """Create three-view combined image for video saving"""
        # Resize images
        head_resized = cv2.resize(head_cam, (640, 480))  # Main view keeps original size
        left_resized = cv2.resize(left_cam, (320, 240))  # Left view
        right_resized = cv2.resize(right_cam, (320, 240))  # Right view
        
        # Create combined image: main view on top, left and right views on bottom
        # Total size: 640x720 (width x height)
        combined_image = np.zeros((720, 640, 3), dtype=np.uint8)
        
        # Place main view (top)
        combined_image[0:480, 0:640] = head_resized
        
        # Place left and right views (bottom)
        combined_image[480:720, 0:320] = left_resized
        combined_image[480:720, 320:640] = right_resized
        
        return combined_image

    @torch.no_grad()
    def predict_action(self, observation):
        """Predict action using H-RDT model"""
        if len(self.obs_cache) == 0:
            return None
        
        current_obs = self.obs_cache[-1]
        print("current_obs",current_obs)
        # Process state tokens
        state_tokens = None
        if current_obs['agent_pos'] is not None:
            state_tokens = torch.tensor(
                current_obs['agent_pos']
            ).unsqueeze(0).unsqueeze(0).to(self.device, dtype=self.dtype)
        
        # Process image tokens (separate camera views)
        image_tokens = None
        valid_images = []
        
        for cam_name in ['head_cam', 'left_cam', 'right_cam']:
            if current_obs['images'][cam_name] is not None:
                # Convert to PIL image
                img_pil = PImage.fromarray(current_obs['images'][cam_name])
                
                # Apply image transform
                transformed = self.image_transform(img_pil)
                valid_images.append(transformed)
        
        if len(valid_images) > 0:
            # Stack images for batch processing
            image_inputs = {}
            for k in valid_images[0].keys():
                image_inputs[k] = torch.stack([img[k] for img in valid_images])
                image_inputs[k] = image_inputs[k].unsqueeze(0).to(self.device, dtype=self.dtype)
            
            # Use vision encoder
            with torch.no_grad():
                k = next(iter(image_inputs))
                batch_size, seq_len, C, H, W = image_inputs[k].shape
                # Reshape to (batch_size * seq_len, C, H, W)
                for k in image_inputs:
                    image_inputs[k] = image_inputs[k].view(-1, C, H, W)
                # Get features using vision encoder
                image_features = self.vision_encoder(image_inputs)
                # Reshape features to correct dimensions
                image_tokens = image_features.view((batch_size, -1, self.vision_encoder.embed_dim))
        
        if image_tokens is None:
            return None
        
        # Prepare language tokens
        lang_tokens = None
        lang_attn_mask = None
        
        if self.training_mode == 'lang' and self.lang_tokens is not None:
            lang_tokens = self.lang_tokens.unsqueeze(0)  # Add batch dimension
            lang_attn_mask = self.lang_attn_mask.unsqueeze(0) if self.lang_attn_mask is not None else None

        # Model inference
        start_time = time.time()
        
        action_pred = self.policy.predict_action(
            state_tokens=state_tokens,
            image_tokens=image_tokens,
            lang_tokens=lang_tokens,
            lang_attn_mask=lang_attn_mask,
        )
        
        inference_time = time.time() - start_time
        print(f"Model inference time: {inference_time:.3f}s")
        
        # Convert to numpy array
        normalized_actions = action_pred.float().cpu().numpy()[0]
        
        # Denormalize actions if statistics available
        # if self.action_min is not None and self.action_max is not None:
        #     joint_actions = normalized_actions * (self.action_max - self.action_min) + self.action_min
        # else:
        #     joint_actions = normalized_actions
        if self.model_dimension == 62:
            normalized_actions = normalized_actions[:, 48:]  # 只取后14D真实数据
   
        joint_actions = self.denormalize_action(normalized_actions)
        # Apply gripper adjustment: subtract 0.3 from 7th dimension (index 6) and 14th dimension (index 13)
        # joint_actions[:, 6] -= 0.3   # Left arm gripper (7th dimension)
        # joint_actions[:, 13] -= 0.3  # Right arm gripper (14th dimension)
        # print(f"Applied gripper adjustment: -0.3 to dimensions 7 and 14")
        
        return joint_actions 
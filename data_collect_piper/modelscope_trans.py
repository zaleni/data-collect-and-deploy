from modelscope.hub.api import HubApi
YOUR_ACCESS_TOKEN = '8d7b1539-22ea-4a3d-b6b1-73a7b6311d9d'
api = HubApi()
api.login(YOUR_ACCESS_TOKEN)

from modelscope.hub.constants import Licenses, ModelVisibility

################### 模型
owner_name = 'zaleni'
model_name = 'magicbot_520_basedata'
model_id = f"{owner_name}/{model_name}"

# api.create_model(
#     model_id,
#     visibility=ModelVisibility.PUBLIC,
#     license=Licenses.APACHE_V2,
#     chinese_name="我的测试模型"
# )

# 上传
api.upload_folder(
    repo_id=f"{owner_name}/{model_name}",
    folder_path='work_dirs/lup1m_path-l_to_vit_tiny_from_cls_patch_atten_moe_v2/checkpoint0100.pth', # 本地的数据集文件
    path_in_repo='0517_v1', # 传到modelscope上的文件夹名称，没有就不传这个参数
    commit_message='v1 0517', # 提交的信息
    repo_type='dataset' # 如果是数据集就是'dataset''model'
)
# 下载
# from modelscope import snapshot_download
# model_path =snapshot_download(
#     repo_id=f"{owner_name}/{model_name}",
#     repo_type='model',
#     local_dir='./work_dirs',
#     allow_patterns=['lup1m_solider-b_to_swin_tiny_from_cls_patch_moe/checkpoint.pth']
#     )

# ################### 数据集
# owner_name = 'hmdeng'
# dataset_name = 'LUP'
# dataset_id = f"{owner_name}/{dataset_name}"

# api.upload_folder(
#     repo_id=f"{owner_name}/{dataset_name}",
#     folder_path='/mnt/hdd1/wangxuanhan/datasets/LUP1M.tar.gz',
#     commit_message='LUP1M',
#     repo_type = 'dataset'
# )
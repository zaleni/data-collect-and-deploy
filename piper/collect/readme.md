#### data_collect

松灵piper采用主从臂连线方式进行遥操，连线通电后不用启动额外程序

1. 新开一个终端，启动摄像头ros程序

   ```
   source ~/deploy/tmp/OrbbecSDK_develop/orbbec_ws/devel/setup.bash
   roslaunch orbbec_camera_multi_camera.launch
   ```

2. 启动采集数据程序 from[ zchoi/MagicBot/DataCollection at main](https://github.com/zchoi/MagicBot/tree/main/DataCollection)（不能vscode，直接终端）

   ```
   cd /home/pc3/data_collect/songlings
   conda activate piper_clt
   python data_collect.py
   ```

3. 数据集格式转换，将采集的数据转化为所需hdf5文件

   ```
   conda activate piper_clt
   python /home/pc3/data_collect/openpi/convert_data_hdf5_noop.py
   python /home/pc3/data_collect/openpi/convert_data_hdf5.pyw
   ```

   


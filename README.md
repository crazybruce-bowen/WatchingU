# WatchingU  

简体中文 | [English](README_EN.md) 

--------  
自动获取lianjia和ziru在上海的房源信息，并提供低价预警  
  
技术点：  
1. 使用MongoDB以拓展存储图像数据  
2. 使用图像检测和分割技术，对Ziru网的房源价格加密图片进行解密，获取数值型的房源价格  
3. 自动计算小区均价以供对比。房源低价预警正在开发中  
  
代码结构:

>- core (核心功能)
>  - core_catching （核心爬虫）
>- logs （日志区）
>- utils （工具区）
>  - orc （图像文本识别相关）
>  - common_utils （通用工具）
>  - html_service （html服务）
>  - io_service （读取写出服务）
>  - log_service （日志服务）
>  - orc_service （图像文本识别服务）
>- main （主程序）

关联项目：
- [链家独立项目](https://github.com/crazybruce-bowen/crawler_LJ)
- [自如独立项目](https://github.com/crazybruce-bowen/crawler_ZR)

--------  

非商业用途，仅供个人学习交流  
    
<p align="right"> 作者： 李博文  
<p align="right"> 20220919  

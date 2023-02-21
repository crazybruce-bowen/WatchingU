#%% 测试区域

import os

path = r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\整合'
os.chdir(path)

from core.usage import get_room_info_standard, add_drive_time


#%%
t1, t2, t3 = get_room_info_standard('hz', '西湖', tag_xiaoqu=False, rent_type='整租',
                                    get_price=True, price_min=3000, price_max=6000)
t1 = add_drive_time(t1, '杭州东站', '杭州', '西湖')
t2 = add_drive_time(t2, '杭州东站', '杭州', '西湖')
df1 = pd.DataFrame(t1)
df2 = pd.DataFrame(t2)
df3 = pd.DataFrame(t3)
df4 = pd.DataFrame(t1 + t2)
writer = pd.ExcelWriter(r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\整合\result\test_0217.xlsx')
df1.to_excel(writer, index=None, sheet_name='链家')
df2.to_excel(writer, index=None, sheet_name='自如')
df3.to_excel(writer, index=None, sheet_name='小区')
df4.to_excel(writer, index=None, sheet_name='全部')



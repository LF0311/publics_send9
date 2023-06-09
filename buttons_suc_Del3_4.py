import streamlit as st
import time
import requests
import datetime
import pandas as pd
import struct
import socket


def read_files_split(df):
    # 重命名列名
    time_list = []
    n_list = []
    e_list = []
    id_sent_list = []
    n_e_dic = {
        '17': [118.94487719912863, 32.04973320987654], '33': [118.944653665479, 32.04930415779645],
        '49': [118.94371091538719, 32.04952245813544], '65': [118.9440911184693, 32.04922271168032],
        '81': [118.94476257015458, 32.04909416478442], '97': [118.94522941814569, 32.04918556478112],
        '113': [118.9450939453889, 32.04882166706268], '129': [118.94439573831303, 32.0489326089609],
        '145': [118.9437780293552, 32.0486649622104], '161': [118.94440360807663, 32.04854417425235],
        '18': [118.94376971312143, 32.04749544339897], '34': [118.94408233261578, 32.04798360123858],
        '50': [118.94449395983249, 32.047371193787015], '66': [118.94388113557162, 32.04696915703969],
        '82': [118.94339509710773, 32.04795072592209], '98': [118.9429047495926, 32.04817937491075],
        '114': [118.94282941944903, 32.04769909289085], '130': [118.94414871429017, 32.0483391058218],
        '146': [118.94343921535817, 32.04702676274397], '162': [118.94425473794394, 32.047609564263816],
        '19': [118.94422551817604, 32.04984433138635], '35': [118.9436352561242, 32.04910948855981],
        '51': [118.94463680062799, 32.04798154165046],
        '15': [118.94425473794394, 32.047609564263816],
    }

    id_sent_dic = {
        '17': 1, '33': 2, '49': 3,
        '65': 4,
        '81': 5, '97': 6, '113': 7,
        '129': 8,
        '145': 9, '161': 10, '18': 11,
        '34': 12, '50': 13, '66': 14,
        '82': 15, '98': 16, '114': 17,
        '130': 18, '146': 19, '162': 20,
        '19': 21, '35': 22, '51': 23,
        '15': 55,
    }

    #  df = df[df.loc[:, 1].isin(list(map(int, list(n_e_dic.keys()))))]
    mask = df.loc[:, 1].isin(list(map(int, list(n_e_dic.keys()))))
    # 获取不符合条件的行索引
    indexes_to_drop = df[~mask].index
    # 删除不符合条件的行
    df.drop(indexes_to_drop, inplace=True)
    df.reset_index(drop=True, inplace=True)
    # df.drop(['index'], axis=1)

    for tme in range(len(df[0])):
        time_list.append(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        n_list.append(n_e_dic[str(df[1][tme])][0])
        e_list.append(n_e_dic[str(df[1][tme])][1])
        id_sent_list.append(id_sent_dic[str(df[1][tme])])

    df['T'] = time_list
    df['N'] = n_list
    df['E'] = e_list
    df['Id'] = id_sent_list

    df.columns = ['Frame', 'Id_Real', 'X_Mag', 'Y_Mag', 'Z_Mag', 'X_Gyro', 'Y_Gyro', 'Z_Gyro', 'X_Accel', 'Y_Accel',
                  'Z_Accel',
                  'Audio', 'Audio_VAD', 'Location', 'T', 'N', 'E', 'Id']
    # 删除Location列
    df['Audio'] = df['Audio'].apply(lambda x: x / 100)
    # df['N'] = df['N'].apply(lambda x: float(x) / 100)
    # df['E'] = df['E'].apply(lambda x: float(x) / 100)
    df1 = df.drop(['Location'], axis=1)
    return df1


def process_udp_to_df(data):
    k = 0
    final_var_list = []
    while True:
        if data[0 + k * 60:k * 60 + 1] == b'':
            # obj.close()
            break
        if data[0 + k * 60:k * 60 + 1] == b'\xbb' and data[k * 60 + 1:k * 60 + 2] == b'\xbb':
            if data[2 + k * 60:k * 60 + 3] == b'\x3c':
                data_id = ord(data[k * 60 + 3:k * 60 + 4])  # int(data[k * 60 + 3:k * 60 + 4], 16)              # 修改代码
                data_sensor = data[k * 60 + 4:k * 60 + 26]  # fp.read(22)
                count = len(data_sensor) / 2
                var = struct.unpack('h' * int(count), data_sensor)
                print(k, data_id, var)
                data_sensor_next = data[k * 60 + 26:k * 60 + 58]  # fp.read(32)
                # var0 = "T:"
                var1 = data_sensor_next     # 修改
                var_list = list(var)
                var_list.insert(0, data_id)     # 修改
                var_list.insert(0, k)       # 修改
                var_list.append(var1)    # 修改
                # print(var_list)
                final_var_list.append(var_list)     # 修改
            elif data[2 + k * 60:k * 60 + 3] == b'\xaa' or data[2 + k * 60:k * 60 + 3] == b'\xAA':
                if data[3 + k * 60:k * 60 + 4] == b'\x01':
                    var_list = [k, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    final_var_list.append(var_list)
                elif data[3 + k * 60:k * 60 + 4] == b'\x02':
                    var_list = [k, 15, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    final_var_list.append(var_list)
                elif data[3 + k * 60:k * 60 + 4] == b'\x03':
                    var_list = [k, 15, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    final_var_list.append(var_list)
                elif data[3 + k * 60:k * 60 + 4] == b'\x04':
                    var_list = [k, 15, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    final_var_list.append(var_list)
        k += 1
    final_var_df = pd.DataFrame(final_var_list)
    print("已生成txt数据文件！")
    return final_var_df

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """

st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.markdown(
    f'''
        <style>
            .reportview-container .sidebar-content {{
                padding-top: {0}rem;
            }}
            .appview-container .main .block-container {{
                {f'max-width: 100%;'}
                padding-top: {0}rem;
                padding-right: {1}rem;
                padding-left: {1}rem;
                padding-bottom: {0}rem;
                overflow: auto;
            }}
        </style>
        ''',
    unsafe_allow_html=True,
)

st.subheader("  ")

colmns0 = st.columns([1, 8, 1], gap="medium")

with colmns0[1]:
    st.markdown(
        '<nobr><p style="text-align: center;font-family:sans serif; color:Black; font-size: 32px; font-weight: bold">环境传感器目标识别平台</p></nobr>',
        unsafe_allow_html=True)

with colmns0[1]:
    # st.markdown('###')

    timestr = time.strftime('%Y-%m-%d %H:%M:%S')
    st.markdown(
        '<nobr><p style="text-align: center;font-family:sans serif; color:Black; font-size: 20px;">{}</p></nobr>'.format(
            timestr),
        unsafe_allow_html=True)

colmns = colmns0[1].columns([1, 1, 1, 1, 1], gap="small")
button1 = colmns[1].button(' 开始执行 ')
button2 = colmns[2].button(' 结束指令 ')
button3 = colmns[3].button(' 刷新页面 ')
button4 = colmns[1].button(' 重置页面 ')
button5 = colmns[2].button(' 初始设备 ')
button6 = colmns[3].button(' 初始网关 ')

# 本地IP地址和端口号
LOCAL_IP = ""
# LOCAL_PORT = 0  # 选择一个空闲端口，系统会自动分配

# 服务器IP地址和端口号
UDP_IP = "10.10.20.150"  # 51.51.51.50
UDP_PORT = 1438

# 指令数据
command_real_time = bytearray([0x55, 0xAA, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA, 0x55])
command_history = bytearray([0x55, 0xAA, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA, 0x55])
sj_mode_control = bytearray([0x55, 0xAA, 0x10, 0x02, 0x01, 0x01, 0x00])
zz_mode_control = bytearray([0x55, 0xAA, 0x20, 0x02, 0x02, 0x02, 0x00])

empty_elem = colmns0[1].columns([1, 3, 1], gap="small")[1].empty()  # 创建空元素

if button1:
    print('执行Button1')
    empty_elem.empty()
    empty_elem.error('请勿点击')
    start_time = time.time()
    fir_cyc_num = 1
    while True:
        print(f'第{fir_cyc_num}次执行Button1第一层循环')
        fir_cyc_num += 1
        if button2 or button3 or button4 or button5 or button6:
            # st.markdown('终止发送')
            print('终止发送')
            break
        else:
            first_elapsed_time = time.time() - start_time
            # print(elapsed_time)
            if first_elapsed_time >= 30:
                print("已等待30秒，重新接收数据")
                start_time = time.time()  # 重新设置时间 重新开始判断30s
                continue
            else:
                # 创建UDP套接字
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind((LOCAL_IP, UDP_PORT))
                # obj_txt = open("./sensors_data.txt", 'w')

                sock.setblocking(False)
                # 设置接收超时时间为 1 秒
                sock.settimeout(1)

                # 发送获取实时数据指令
                sock.sendto(command_real_time, (UDP_IP, UDP_PORT))
                # sock.sendto(command_real_time, (UDP_IP, UDP_PORT))
                start_time2 = time.time()
                received_data = b''
                cyc_num = 1
                while True:
                    print(f'第{cyc_num}次执行Button1第二层循环')
                    cyc_num += 1
                    # print(cyc_num)
                    elapsed_time = time.time() - start_time2
                    # print(elapsed_time)
                    if elapsed_time >= 5:
                        print("已完成5秒数据接收，退出循环")
                        break
                    else:
                        try:
                            data, addr = sock.recvfrom(6000)
                            if len(data) == 8 and data[0] == 0xAA and data[1] == 0x55 and data[4] == 0x01 and data[
                                5] == 0x01:
                                # 重新发送指令
                                print("服务器无数据")
                            else:
                                received_data += data

                                # print(data_udp)
                            if len(received_data) != 0:
                                print(received_data)
                            # break  # 接收到数据后跳出循环
                        except socket.timeout:
                            # 处理未接收到数据的情况
                            print("未接收到数据，重新发送...")
                            sock.sendto(command_real_time, (UDP_IP, UDP_PORT))
                            continue  # 继续下一次循环
                        except BlockingIOError:
                            # 处理非阻塞模式下未接收到数据的情况
                            print("未接收到数据，退出循环...")
                            break  # 打破当前循环
                        except OSError as e:
                            if e.errno == 10048:
                                # 处理端口已被占用的情况
                                sock.close()
                                print("端口已被占用，退出循环...")
                                break  # 打破当前循环


                print('处理数据')
                read_file_df = process_udp_to_df(received_data)

                # 关闭套接字
                sock.close()
                print('关闭套接字')
                if len(read_file_df) > 0:
                    # 读取文件，解析数据
                    # read_file_df = pd.read_csv('./sensors_data.txt', sep=',', header=None)
                    final_read_file_df = read_files_split(read_file_df)

                    sensor_dfs = {}

                    # 获取id列中的唯一值
                    unique_ids = final_read_file_df['Id'].unique()
                    unique_ids = sorted(unique_ids)
                    for id_value in unique_ids:
                        # 根据id值筛选数据
                        subset = final_read_file_df[final_read_file_df['Id'] == id_value]
                        subset.reset_index(drop=False, inplace=True)
                        # 将分割后的数据框存储到字典中
                        sensor_dfs[id_value] = subset

                    # 通过50振动传感器信号阈值识别目标
                    if 55 not in unique_ids:
                        # 通过传感器信号阈值识别目标
                        target_mblb_tmp = {}
                        for tmp_id in unique_ids:  # 检测所有传感器
                            # if (sensor_dfs[tmp_id]['Audio'] >= 100).any() or (
                            #         (sensor_dfs[tmp_id]['X_Accel'] >= 5000).any() and sensor_dfs[tmp_id]['X_Accel'] <= 10000).any()  \
                            #         or (sensor_dfs[tmp_id]['X_Mag'] >= 20000).any():
                            #     target_mblb_tmp.update(
                            #         {
                            #             tmp_id: '无' # 车辆
                            #         }
                            #     )
                            if (sensor_dfs[tmp_id]['Audio'] >= 60).any() or \
                                    (sensor_dfs[tmp_id]['X_Accel'] >= 2500).any():
                                target_mblb_tmp.update(
                                    {
                                        tmp_id: '人员'
                                    }
                                )
                            else:
                                target_mblb_tmp.update(
                                    {
                                        tmp_id: '无'
                                    }
                                )

                        # 判断是否全为 '无'
                        if all(value == '无' for value in target_mblb_tmp.values()):
                            print("未识别到目标")
                        else:
                            # 统计人员和车辆的数量
                            person_count = sum(value == '人员' for value in target_mblb_tmp.values())
                            vehicle_count = sum(value == '人员' for value in target_mblb_tmp.values())

                            # 根据数量判断目标类型
                            if person_count > vehicle_count:
                                target_mblb = '人员'
                                id_list = [str(key) for key, value in target_mblb_tmp.items() if value == '人员']
                            else:
                                target_mblb = '人员'
                                id_list = [str(key) for key, value in target_mblb_tmp.items() if value == '人员']

                            trans_data_1 = {}
                            trans_data_1.update(
                                {
                                    'JDMIN': final_read_file_df['N'].min(),
                                    'JDMAX': final_read_file_df['N'].max(),
                                    'WDMIN': final_read_file_df['E'].min(),
                                    'WDMAX': final_read_file_df['E'].max(),
                                    'MBLB': target_mblb,
                                    'MBGS': str(1),
                                    'SBXH': '振动',
                                    'FXSJ': final_read_file_df['T'][0],
                                    'IDLIST': id_list
                                }
                            )
                            url = 'http://51.51.51.15:9011/api/WLW_MLFW/sendTargetInfo'
                            response = requests.post(url, json=trans_data_1)
                            print(trans_data_1)
                            # st.markdown(trans_data_1)
                    else:  # 通过50振动传感器信号
                        if (sensor_dfs[55]['X_Mag'] == 1).any():
                            target_mblb = '人员'
                            id_list = ['1']
                        elif (sensor_dfs[55]['X_Mag'] == 2).any():
                            target_mblb = '人员'
                            id_list = ['2']
                        elif (sensor_dfs[55]['X_Mag'] == 3).any():
                            target_mblb = '人员'
                            id_list = ['3']
                        elif (sensor_dfs[55]['X_Mag'] == 4).any():
                            target_mblb = '人员'
                            id_list = ['4']
                        else:
                            target_mblb = '无'
                            id_list = []

                        if target_mblb != '无':
                            trans_data_1 = {}
                            trans_data_1.update(
                                {
                                    'JDMIN': final_read_file_df['N'].min(),
                                    'JDMAX': final_read_file_df['N'].max(),
                                    'WDMIN': final_read_file_df['E'].min(),
                                    'WDMAX': final_read_file_df['E'].max(),
                                    'MBLB': target_mblb,
                                    'MBGS': str(1),
                                    'SBXH': '振动',
                                    'FXSJ': final_read_file_df['T'][0],
                                    'IDLIST': id_list
                                }
                            )
                            url = 'http://51.51.51.15:9011/api/WLW_MLFW/sendTargetInfo'
                            response = requests.post(url, json=trans_data_1)
                            print(trans_data_1)
                            # st.markdown(trans_data_1)

                    for sensID in unique_ids:
                        if sensID != 55:
                            trans_data_tmp = {}
                            trans_data_tmp.update(
                                {
                                    'CGQID': str(sensID),
                                    'JD': sensor_dfs[sensID]['N'].iloc[0],
                                    'WD': sensor_dfs[sensID]['E'].iloc[0],
                                    'SBSJ': sensor_dfs[sensID]['T'].iloc[0],
                                    'SZJSD': list(abs(sensor_dfs[sensID]['X_Accel'])),
                                    'CTL': list(abs(sensor_dfs[sensID]['X_Mag'])),
                                    'ZS': list(abs(sensor_dfs[sensID]['Audio'])),
                                }
                            )
                            url = 'http://51.51.51.15:9011/api/WLW_MLFW/sendSensorInfo'
                            response_tmp = requests.post(url, json=trans_data_tmp)
                            print(trans_data_tmp)
                            # st.markdown(trans_data_tmp)
                    empty_elem.success('可点击其他按钮')
                    print('**** 可点击其他按钮 ****')
                    time.sleep(2)
                    empty_elem.empty()  # 清空元素
                    empty_elem.error('请勿点击')
                else:
                    print("未接收到传感器数据")
                    # empty_elem = st.empty()  # 创建空元素
                    empty_elem.success('可点击其他按钮')
                    print('**** 可点击其他按钮 ****')
                    time.sleep(2)
                    empty_elem.empty()  # 清空元素
                    empty_elem.error('请勿点击')

if button3:
    print('执行Button3')
    empty_elem.empty()
    empty_elem.error('请勿点击')
    start_time = time.time()
    fir_cyc_num = 1
    while True:
        print(f'第{fir_cyc_num}次执行Button3第一层循环')
        fir_cyc_num += 1
        # st.markdown(button2)
        if button1 or button2 or button4 or button5 or button6:
            # st.markdown('终止发送')
            print('终止发送Button3')
            break
        else:
            first_elapsed_time = time.time() - start_time
            # print(elapsed_time)
            if first_elapsed_time >= 30:
                print("已等待30秒，重新接收数据")
                start_time = time.time()  # 重新设置时间 重新开始判断30s
                continue
            else:
                # 创建UDP套接字
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind((LOCAL_IP, UDP_PORT))
                # obj_txt = open("./sensors_data.txt", 'w')

                sock.setblocking(False)
                # 设置接收超时时间为 1 秒
                sock.settimeout(1)

                # 发送获取实时数据指令
                sock.sendto(command_real_time, (UDP_IP, UDP_PORT))
                # sock.sendto(command_real_time, (UDP_IP, UDP_PORT))
                start_time2 = time.time()
                received_data = b''
                cyc_num = 1
                while True:
                    print(f'第{cyc_num}次执行Button3第二层循环')
                    cyc_num += 1
                    elapsed_time = time.time() - start_time2
                    # print(elapsed_time)
                    if elapsed_time >= 5:
                        print("已完成5秒数据接收，退出循环")
                        break
                    else:
                        try:
                            data, addr = sock.recvfrom(6000)
                            if len(data) == 8 and data[0] == 0xAA and data[1] == 0x55 and data[4] == 0x01 and \
                                    data[5] == 0x01:
                                # 重新发送指令
                                print("服务器无数据")
                            else:
                                received_data += data

                                # print(data_udp)
                            if len(received_data) != 0:
                                print(received_data)
                            # break  # 接收到数据后跳出循环
                        except socket.timeout:
                            # 处理未接收到数据的情况
                            print("未接收到数据，重新发送...")
                            sock.sendto(command_real_time, (UDP_IP, UDP_PORT))
                            continue  # 继续下一次循环
                        except BlockingIOError:
                            # 处理非阻塞模式下未接收到数据的情况
                            print("未接收到数据，退出循环...")
                            break  # 打破当前循环

                print('处理数据')
                read_file_df = process_udp_to_df(received_data)

                # 关闭套接字
                sock.close()

                if len(read_file_df) > 0:
                    # 读取文件，解析数据
                    # read_file_df = pd.read_csv('./sensors_data.txt', sep=',', header=None)
                    final_read_file_df = read_files_split(read_file_df)

                    sensor_dfs = {}

                    # 获取id列中的唯一值
                    unique_ids = final_read_file_df['Id'].unique()
                    unique_ids = sorted(unique_ids)
                    for id_value in unique_ids:
                        # 根据id值筛选数据
                        subset = final_read_file_df[final_read_file_df['Id'] == id_value]
                        subset.reset_index(drop=False, inplace=True)
                        # 将分割后的数据框存储到字典中
                        sensor_dfs[id_value] = subset

                    trans_data_1 = {}
                    trans_data_1.update(
                        {
                            'JDMIN': final_read_file_df['N'].min(),
                            'JDMAX': final_read_file_df['N'].max(),
                            'WDMIN': final_read_file_df['E'].min(),
                            'WDMAX': final_read_file_df['E'].max(),
                            'MBLB': '人员',
                            'MBGS': str(1),
                            'SBXH': '振动',
                            'FXSJ': str(final_read_file_df['T'][0]),
                            'IDLIST': ['1']
                        }
                    )
                    url = 'http://51.51.51.15:9011/api/WLW_MLFW/sendTargetInfo'
                    response = requests.post(url, json=trans_data_1)
                    print(trans_data_1)
                    # st.markdown(trans_data_1)

                    for sensID in unique_ids:
                        if sensID != 55:
                            trans_data_tmp = {}
                            trans_data_tmp.update(
                                {
                                    'CGQID': str(sensID),
                                    'JD': sensor_dfs[sensID]['N'].iloc[0],
                                    'WD': sensor_dfs[sensID]['E'].iloc[0],
                                    'SBSJ': sensor_dfs[sensID]['T'].iloc[0],
                                    'SZJSD': list(abs(sensor_dfs[sensID]['X_Accel'])),
                                    'CTL': list(abs(sensor_dfs[sensID]['X_Mag'])),
                                    'ZS': list(abs(sensor_dfs[sensID]['Audio'])),
                                }
                            )
                            url = 'http://51.51.51.15:9011/api/WLW_MLFW/sendSensorInfo'
                            response_tmp = requests.post(url, json=trans_data_tmp)
                            print(trans_data_tmp)
                            # st.markdown(trans_data_tmp)
                    # empty_elem = st.empty()  # 创建空元素
                    empty_elem.success('可点击其他按钮')
                    print('**** 可点击其他按钮 ****')
                    time.sleep(2)
                    empty_elem.empty()  # 清空元素
                    empty_elem.error('请勿点击')
                else:
                    print("未接收到传感器数据")
                    # empty_elem = st.empty()  # 创建空元素
                    empty_elem.success('可点击其他按钮')
                    print('**** 可点击其他按钮 ****')
                    time.sleep(2)
                    empty_elem.empty()  # 清空元素
                    empty_elem.error('请勿点击')


if button4:
    print('执行Button4')
    empty_elem.empty()  # 创建空元素
    empty_elem.error('请勿点击')
    start_time = time.time()
    fir_cyc_num = 1
    while True:
        print(f'第{fir_cyc_num}次执行Button4第一层循环')
        fir_cyc_num += 1
        # st.markdown(button2)
        if button1 or button2 or button3 or button5 or button6:
            # st.markdown('终止发送')
            print('终止发送Button4')
            break
        else:
            first_elapsed_time = time.time() - start_time
            # print(elapsed_time)
            if first_elapsed_time >= 30:
                print("已等待30秒，重新接收数据")
                start_time = time.time()  # 重新设置时间 重新开始判断30s
                continue
            else:
                # 创建UDP套接字
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind((LOCAL_IP, UDP_PORT))
                # obj_txt = open("./sensors_data.txt", 'w')

                sock.setblocking(False)
                # 设置接收超时时间为 4 秒
                sock.settimeout(1)

                # 发送获取实时数据指令
                sock.sendto(command_real_time, (UDP_IP, UDP_PORT))
                # sock.sendto(command_real_time, (UDP_IP, UDP_PORT))
                start_time2 = time.time()
                received_data = b''
                cyc_num = 1
                while True:
                    print(f'第{cyc_num}次执行Button4第二层循环')
                    cyc_num += 1
                    elapsed_time = time.time() - start_time2
                    # print(elapsed_time)
                    if elapsed_time >= 5:
                        print("已完成5秒数据接收，退出循环")
                        break
                    else:
                        try:
                            data, addr = sock.recvfrom(6000)
                            if len(data) == 8 and data[0] == 0xAA and data[1] == 0x55 and data[4] == 0x01 and data[
                                5] == 0x01:
                                # 重新发送指令
                                print("服务器无数据")
                            else:
                                received_data += data

                                # print(data_udp)
                            if len(received_data) != 0:
                                print(received_data)
                            # break  # 接收到数据后跳出循环
                        except socket.timeout:
                            # 处理未接收到数据的情况
                            print("未接收到数据，重新发送...")
                            sock.sendto(command_real_time, (UDP_IP, UDP_PORT))
                            continue  # 继续下一次循环
                        except BlockingIOError:
                            # 处理非阻塞模式下未接收到数据的情况
                            print("未接收到数据，退出循环...")
                            break  # 打破当前循环

                print('处理数据')
                read_file_df = process_udp_to_df(received_data)

                # 关闭套接字
                sock.close()

                if len(read_file_df) > 0:
                    # 读取文件，解析数据
                    # read_file_df = pd.read_csv('./sensors_data.txt', sep=',', header=None)
                    final_read_file_df = read_files_split(read_file_df)

                    sensor_dfs = {}

                    # 获取id列中的唯一值
                    unique_ids = final_read_file_df['Id'].unique()
                    unique_ids = sorted(unique_ids)
                    for id_value in unique_ids:
                        # 根据id值筛选数据
                        subset = final_read_file_df[final_read_file_df['Id'] == id_value]
                        subset.reset_index(drop=False, inplace=True)
                        # 将分割后的数据框存储到字典中
                        sensor_dfs[id_value] = subset

                    trans_data_1 = {}
                    trans_data_1.update(
                        {
                            'JDMIN': final_read_file_df['N'].min(),
                            'JDMAX': final_read_file_df['N'].max(),
                            'WDMIN': final_read_file_df['E'].min(),
                            'WDMAX': final_read_file_df['E'].max(),
                            'MBLB': '人员',
                            'MBGS': str(1),
                            'SBXH': '振动',
                            'FXSJ': final_read_file_df['T'][0],
                            'IDLIST': ['2']
                        }
                    )
                    url = 'http://51.51.51.15:9011/api/WLW_MLFW/sendTargetInfo'
                    response = requests.post(url, json=trans_data_1)
                    print(trans_data_1)
                    # st.markdown(trans_data_1)

                    for sensID in unique_ids:
                        if sensID != 55:
                            trans_data_tmp = {}
                            trans_data_tmp.update(
                                {
                                    'CGQID': str(sensID),
                                    'JD': sensor_dfs[sensID]['N'].iloc[0],
                                    'WD': sensor_dfs[sensID]['E'].iloc[0],
                                    'SBSJ': sensor_dfs[sensID]['T'].iloc[0],
                                    'SZJSD': list(abs(sensor_dfs[sensID]['X_Accel'])),
                                    'CTL': list(abs(sensor_dfs[sensID]['X_Mag'])),
                                    'ZS': list(abs(sensor_dfs[sensID]['Audio'])),
                                }
                            )
                            url = 'http://51.51.51.15:9011/api/WLW_MLFW/sendSensorInfo'
                            response_tmp = requests.post(url, json=trans_data_tmp)
                            print(trans_data_tmp)
                            # st.markdown(trans_data_tmp)
                    empty_elem.success('可点击其他按钮')
                    print('**** 可点击其他按钮 ****')
                    time.sleep(2)
                    empty_elem.empty()  # 清空元素
                    empty_elem.error('请勿点击')
                else:
                    print("未接收到传感器数据")
                    # empty_elem = st.empty()  # 创建空元素
                    empty_elem.success('可点击其他按钮')
                    print('**** 可点击其他按钮 ****')
                    time.sleep(2)
                    empty_elem.empty()  # 清空元素
                    empty_elem.error('请勿点击')


# 按钮字体
st.markdown("""<style>p, ol, ul, dl
{
margin: 0px 0px 1rem;
padding: 0px;
font-size: 1.0rem;
font-weight: 1000;
}
</style>""", unsafe_allow_html=True)

st.markdown("""<style> div.stButton > button:first-child {
background-color: white;
color: black;
height:3em; 
width:8em; 
border-radius:10px 10px 10px 10px;
border: 3px solid #008CBA;
}
</style>""", unsafe_allow_html=True)

st.markdown("""<style> 
#root > div:nth-child(1) > div.withScreencast > div > div > div > section.main.css-uf99v8.egzxvld5 > div.block-container.css-z5fcl4.egzxvld4 > div:nth-child(1) > div > div.css-ocqkz7.e1tzin5v3 > div:nth-child(1) > div:nth-child(1) > div > div.css-ocqkz7.e1tzin5v3 > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(5) > div > div.css-c6gdys.edb2rvg0 > div > p {
font-size: 4px;
}
</style>""", unsafe_allow_html=True)
st.markdown("""<style> 
#root > div:nth-child(1) > div.withScreencast > div > div > div > section.main.css-uf99v8.egzxvld5 > div.block-container.css-z5fcl4.egzxvld4 > div:nth-child(1) > div > div.css-ocqkz7.e1tzin5v3 > div:nth-child(1) > div:nth-child(1) > div > div.css-ocqkz7.e1tzin5v3 > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(4) > div > div.css-c6gdys.edb2rvg0 > div > p {
font-size: 4px;
}
</style>""", unsafe_allow_html=True)

st.markdown("""<style> 
#root > div:nth-child(1) > div.withScreencast > div > div > div > section.main.css-uf99v8.egzxvld5 > div.block-container.css-z5fcl4.egzxvld4 > div:nth-child(1) > div > div.css-ocqkz7.e1tzin5v3 > div:nth-child(1) > div:nth-child(1) > div > div.css-ocqkz7.e1tzin5v3 > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(6) > div > div > div > div > div > div > p {
font-size: 4px;
}
</style>""", unsafe_allow_html=True)
st.markdown("""<style> div.stButton > button:first-child {
background-color: white;
color: black;
height:3em; 
width:8em; 
border-radius:10px 10px 10px 10px;
border: 3px solid #008CBA;
}
</style>""", unsafe_allow_html=True)

st.markdown("""<style> div.stButton > button:hover {
background-color: #008CBA;
color: white;
}
</style>""", unsafe_allow_html=True)

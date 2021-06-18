import numpy as np
import pandas as pd
import urllib.request
from io import StringIO

#必要に応じて変更するパラメータ。
test_data_url = 'https://raw.githubusercontent.com/ToshikiMoritani/fixpoint_test/main/test_data.csv'#テストデータが保存されているGitHub上のURL
N = 5#故障とみなす連続したタイムアウトの回数。また、あるサブネット内全て同時にN回以上タイムアウトしていると、サブネットの故障とみなす。
m = 3#平均応答時間計算に使う直近のデータ数。
t = 50#過負荷状態であると判断するping時間の閾値。

#テストデータをデータフレーム型で読み込む。
res = urllib.request.urlopen(test_data_url)
res = res.read().decode("utf-8")
test_data = pd.read_csv(StringIO(res) , header=None, names=['date_time', 'server_address','response_time'])

#テストデータを、行名を日時、列名をサーバアドレス、値を応答時間の形に加工した表を作成。
server_address_list = list(test_data['server_address'].unique())
test_data_mat = np.zeros([len(test_data.index),len(server_address_list)])
test_data_mat[:,:] = np.nan
test_data_mat = pd.DataFrame(test_data_mat, columns=server_address_list) 
for server_address in server_address_list:
    test_data_mat[server_address] = test_data[test_data['server_address']==server_address]['response_time']
test_data_mat = test_data_mat.set_index(test_data['date_time'])

#連続で応答がない回数を数える表を作成。
counter_mat = np.zeros([len(test_data.index),len(server_address_list)])
counter_mat[:,:] = np.nan
counter_mat = pd.DataFrame(counter_mat, columns=server_address_list) 
for server_address in server_address_list:
    counter = 0#連続で応答がない回数を数えるcounterを作成。
    for i in range(len(counter_mat.index)):
        if (test_data_mat[server_address][i:i+1].isnull()).all():#nanの時は何もしない。
            pass
        elif (test_data_mat[server_address][i:i+1] == '-').all():#タイムアウトしたときはcounterに1を足す。
            counter += 1
            counter_mat[server_address][i:i+1] = counter
        elif (test_data_mat[server_address][i:i+1] != '-').all():#正常に応答があればcounterを0にリセット。
            counter = 0
            counter_mat[server_address][i:i+1] = counter
counter_mat = counter_mat.set_index(test_data['date_time'])

#設問1。故障状態のサーバアドレスとそのサーバの故障期間を出力する。
print('設問1：故障状態のサーバアドレスとそのサーバの故障期間を出力する。')
for server_address in server_address_list:
    breakdowned_time = (counter_mat[server_address] == 1).index[(counter_mat[server_address] == 1)==True]#応答がなくなった（counter=1になった）時のインデックス配列
    normal_time = (counter_mat[server_address] == 0).index[(counter_mat[server_address] == 0)==True]#応答がある（counter=0の）時のインデックス配列
    for time in breakdowned_time:
        if np.count_nonzero(normal_time > time) >= 1:#サーバが復活した場合。
            revivaled_time = normal_time[normal_time > time][0]
            print('サーバアドレス' + server_address + 'が' \
                  + str(time)[-14:-10] + '年' + str(time)[-10:-8] + '月' + str(time)[-8:-6] + '日' + str(time)[-6:-4] + '時' + str(time)[-4:-2] + '分' + str(time)[-2:] + '秒から' \
                  + str(revivaled_time)[-14:-10] + '年' + str(revivaled_time)[-10:-8] + '月' + str(revivaled_time)[-8:-6] + '日' + str(revivaled_time)[-6:-4] + '時' + str(revivaled_time)[-4:-2] + '分' + str(revivaled_time)[-2:] + '秒まで故障。')
        elif np.count_nonzero(normal_time > time) ==0:#サーバが故障したまま記録が終了した場合。
            print('サーバアドレス' + server_address + 'が' \
                  + str(time)[-14:-10] + '年' + str(time)[-10:-8] + '月' + str(time)[-8:-6] + '日' + str(time)[-6:-4] + '時' + str(time)[-4:-2] + '分' + str(time)[-2:] + '秒から' \
                  +'記録終了まで故障。')

print('')#一行空ける

#設問2。N回以上連続してタイムアウトした場合にのみ故障とみなす。
print('設問2：N回以上連続してタイムアウトした場合にのみ故障とみなす。今回はN=' + str(N) + '。')
for server_address in server_address_list:
    breakdowned_time = (counter_mat[server_address] == 1).index[(counter_mat[server_address] == 1)==True]#応答がなくなった（counter=1になった）時のインデックス配列
    breakdowned_long_time = (counter_mat[server_address] == N).index[(counter_mat[server_address] == N)==True]#応答がN回連続でなくなった（counter=Nになった）時のインデックス配列
    normal_time = (counter_mat[server_address] == 0).index[(counter_mat[server_address] == 0)==True]#応答がある（counter=0の）時のインデックス配列
    for time in breakdowned_long_time:
        breakdowned_long_start_time = breakdowned_time[breakdowned_time < time][-1]
        if np.count_nonzero(normal_time > time) >= 1:#サーバが復活した場合。
            revivaled_time = normal_time[normal_time > time][0]
            print('サーバアドレス' + server_address + 'が' \
                  + str(breakdowned_long_start_time)[-14:-10] + '年' + str(breakdowned_long_start_time)[-10:-8] + '月' + str(breakdowned_long_start_time)[-8:-6] + '日' + str(breakdowned_long_start_time)[-6:-4] + '時' + str(breakdowned_long_start_time)[-4:-2] + '分' + str(breakdowned_long_start_time)[-2:] + '秒から' \
                  + str(revivaled_time)[-14:-10] + '年' + str(revivaled_time)[-10:-8] + '月' + str(revivaled_time)[-8:-6] + '日' + str(revivaled_time)[-6:-4] + '時' + str(revivaled_time)[-4:-2] + '分' + str(revivaled_time)[-2:] + '秒まで故障。')
        elif np.count_nonzero(normal_time > time) ==0:#サーバが故障したまま記録が終了した場合。
            print('サーバアドレス' + server_address + 'が' \
                  + str(breakdowned_long_start_time)[-14:-10] + '年' + str(breakdowned_long_start_time)[-10:-8] + '月' + str(breakdowned_long_start_time)[-8:-6] + '日' + str(breakdowned_long_start_time)[-6:-4] + '時' + str(breakdowned_long_start_time)[-4:-2] + '分' + str(breakdowned_long_start_time)[-2:] + '秒から' \
                  + '記録終了まで故障。')

print('')#一行空ける

#設問3。直近m回の平均応答時間がtミリ秒を超えた場合を、サーバが過負荷状態とする。
print('設問3：直近m回の平均応答時間がtミリ秒を超えた場合を、サーバが過負荷状態とする。今回はｍ=' + str(m) + '、t=' + str(t) + '。')
print('また、今回は「直近は直前」として解釈し、直近m回の中に1度でもタイムアウトを含む場合はサーバ負荷状態とみなす。')
for server_address in server_address_list:
    response_time_seriese = test_data_mat[server_address].dropna(how = 'all')
    response_time_seriese = response_time_seriese.replace({'-' : m * t})#直近にタイムアウトを含めば強制的にサーバー負荷状態とみなす。
    moving_average_response_time_seriese = response_time_seriese.rolling(m).mean().round(1)#自身を含めた直近m回の応答時間の移動平均。
    num = m - 1#loop の為の変数
    overload_checker = False#過負荷の有無を記録する変数。
    overload_start_time_list =[]#過負荷開始時刻リスト。
    overload_end_time_list = []#過負荷終了時刻リスト。
    while num <= len(moving_average_response_time_seriese) - 1:
        if (moving_average_response_time_seriese[moving_average_response_time_seriese.index[num]] >= t) & (overload_checker == False):
            overload_checker = True
            overload_start_time_list.append(moving_average_response_time_seriese.index[num])
            
        if (moving_average_response_time_seriese[moving_average_response_time_seriese.index[num]] < t) & (overload_checker == True):
            overload_checker = False
            overload_end_time_list.append(moving_average_response_time_seriese.index[num - 1])
        num += 1
    
    if (len(overload_start_time_list) != 0) & (len(overload_start_time_list) == (len(overload_end_time_list))):
        for i in range(len(overload_start_time_list)):
            print('サーバアドレス' + server_address + 'が' \
                  + str(overload_start_time_list[i])[-14:-10] + '年' + str(overload_start_time_list[i])[-10:-8] + '月' + str(overload_start_time_list[i])[-8:-6] + '日' + str(overload_start_time_list[i])[-6:-4] + '時' + str(overload_start_time_list[i])[-4:-2] + '分' + str(overload_start_time_list[i])[-2:] + '秒から' \
                  + str(overload_end_time_list[i])[-14:-10] + '年' + str(overload_end_time_list[i])[-10:-8] + '月' + str(overload_end_time_list[i])[-8:-6] + '日' + str(overload_end_time_list[i])[-6:-4] + '時' + str(overload_end_time_list[i])[-4:-2] + '分' + str(overload_end_time_list[i])[-2:] + '秒まで過負荷状態。')
    
    if (len(overload_start_time_list) != 0) & (len(overload_start_time_list) != (len(overload_end_time_list))):
        if len(overload_start_time_list) != 1:
            for i in range(len(overload_start_time_list) - 1):
                print('サーバアドレス' + server_address + 'が' \
                      + str(overload_start_time_list[i])[-14:-10] + '年' + str(overload_start_time_list[i])[-10:-8] + '月' + str(overload_start_time_list[i])[-8:-6] + '日' + str(overload_start_time_list[i])[-6:-4] + '時' + str(overload_start_time_list[i])[-4:-2] + '分' + str(overload_start_time_list[i])[-2:] + '秒から' \
                      + str(overload_end_time_list[i])[-14:-10] + '年' + str(overload_end_time_list[i])[-10:-8] + '月' + str(overload_end_time_list[i])[-8:-6] + '日' + str(overload_end_time_list[i])[-6:-4] + '時' + str(overload_end_time_list[i])[-4:-2] + '分' + str(overload_end_time_list[i])[-2:] + '秒まで過負荷状態。')          
        print('サーバアドレス' + server_address + 'が' \
              + str(overload_start_time_list[-1])[-14:-10] + '年' + str(overload_start_time_list[-1])[-10:-8] + '月' + str(overload_start_time_list[-1])[-8:-6] + '日' + str(overload_start_time_list[-1])[-6:-4] + '時' + str(overload_start_time_list[-1])[-4:-2] + '分' + str(overload_start_time_list[-1])[-2:] + '秒から' \
              + '記録終了時刻まで過負荷状態。')
print('')#一行空ける

#設問4。あるサブネット内のサーバが全て故障（ping応答がすべてN回以上連続でタイムアウト）している場合は、そのサブネット（のスイッチ）の故障とみなす。
print('設問4：あるサブネット内のサーバが全て故障（ping応答がすべてN回以上連続でタイムアウト）している場合は、そのサブネット（のスイッチ）の故障とみなす。今回はN=' + str(N) + '。')
subnet_list=[]#使われているサブネットのリストを作成。
for server_address in server_address_list:
    if not server_address.split('/')[1] in subnet_list:
        subnet_list.append(server_address.split('/')[1])


for subnet in subnet_list:
    subnet_downstream_server_address_list = []#subnetの下流にあるサーバアドレスのリスト。
    for server_address in server_address_list:
        if server_address.split('/')[1] == subnet:
            subnet_downstream_server_address_list.append(server_address)
    subnet_downstream_server_counter_mat = counter_mat[subnet_downstream_server_address_list].fillna(method='ffill')#subnet下流のサーバの、連続タイムアウト回数の表作成。NaNは直前の数字で埋める。
    
    num = 0#loop の為の変数
    breakdowned_subnet_checker = False#サブネットの故障の有無を記録する変数。
    breakdowned_subnet_start_time_list =[]#サブネット故障開始時間。
    breakdowned_subnet_end_time_list = []#サブネット故障終了時間。
    while num <= len(subnet_downstream_server_counter_mat) - 1: 
        if ((subnet_downstream_server_counter_mat.loc[subnet_downstream_server_counter_mat.index[num]] >= N).all()) & (breakdowned_subnet_checker == False):
            breakdowned_subnet_checker = True
            breakdowned_subnet_start_time_list.append(subnet_downstream_server_counter_mat.index[num])
         
        if ((subnet_downstream_server_counter_mat.loc[subnet_downstream_server_counter_mat.index[num]] < N).any()) & (breakdowned_subnet_checker == True):
            breakdowned_subnet_checker = False
            breakdowned_subnet_end_time_list.append(subnet_downstream_server_counter_mat.index[num - 1])
        
        num += 1
        
    if (len(breakdowned_subnet_start_time_list) != 0) & (len(breakdowned_subnet_start_time_list) == (len(breakdowned_subnet_end_time_list))):
        for i in range(len(breakdowned_subnet_start_time_list)):
            print('サブネット/' + str(subnet) + 'が' \
                  + str(breakdowned_subnet_start_time_list[i])[-14:-10] + '年' + str(breakdowned_subnet_start_time_list[i])[-10:-8] + '月' + str(breakdowned_subnet_start_time_list[i])[-8:-6] + '日' + str(breakdowned_subnet_start_time_list[i])[-6:-4] + '時' + str(breakdowned_subnet_start_time_list[i])[-4:-2] + '分' + str(breakdowned_subnet_start_time_list[i])[-2:] + '秒から' \
                  + str(breakdowned_subnet_end_time_list[i])[-14:-10] + '年' + str(breakdowned_subnet_end_time_list[i])[-10:-8] + '月' + str(breakdowned_subnet_end_time_list[i])[-8:-6] + '日' + str(breakdowned_subnet_end_time_list[i])[-6:-4] + '時' + str(breakdowned_subnet_end_time_list[i])[-4:-2] + '分' + str(breakdowned_subnet_end_time_list[i])[-2:] + '秒まで故障。')
    
    if (len(breakdowned_subnet_start_time_list) != 0) & (len(breakdowned_subnet_start_time_list) != (len(breakdowned_subnet_end_time_list))):
        if len(breakdowned_subnet_start_time_list) != 1:
            for i in range(len(breakdowned_subnet_start_time_list) - 1):
                print('サブネット/' + str(subnet) + 'が' \
                      + str(breakdowned_subnet_start_time_list[i])[-14:-10] + '年' + str(breakdowned_subnet_start_time_list[i])[-10:-8] + '月' + str(breakdowned_subnet_start_time_list[i])[-8:-6] + '日' + str(breakdowned_subnet_start_time_list[i])[-6:-4] + '時' + str(breakdowned_subnet_start_time_list[i])[-4:-2] + '分' + str(breakdowned_subnet_start_time_list[i])[-2:] + '秒から' \
                  + str(breakdowned_subnet_end_time_list[i])[-14:-10] + '年' + str(breakdowned_subnet_end_time_list[i])[-10:-8] + '月' + str(breakdowned_subnet_end_time_list[i])[-8:-6] + '日' + str(breakdowned_subnet_end_time_list[i])[-6:-4] + '時' + str(breakdowned_subnet_end_time_list[i])[-4:-2] + '分' + str(breakdowned_subnet_end_time_list[i])[-2:] + '秒まで故障。')
        print('サブネット/' + str(subnet) + 'が' \
              + str(breakdowned_subnet_start_time_list[-1])[-14:-10] + '年' + str(breakdowned_subnet_start_time_list[-1])[-10:-8] + '月' + str(breakdowned_subnet_start_time_list[-1])[-8:-6] + '日' + str(breakdowned_subnet_start_time_list[-1])[-6:-4] + '時' + str(breakdowned_subnet_start_time_list[-1])[-4:-2] + '分' + str(breakdowned_subnet_start_time_list[-1])[-2:] + '秒から' \
              + '記録終了時刻まで故障。')
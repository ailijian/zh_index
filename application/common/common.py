from extend.mysql.sql import Sql
from application.config import setting
import os
import pickle

set_sql = {
    'user': setting.user,
    'password': setting.password,
    'host': setting.host,
    'database': setting.database,
}


class Common:

    def __init__(self):
        pass

    # 获取num统计 并且 +1
    def get_num(self, user_id, count_type, chat):
        customer_id = str(user_id)
        count_type = str(count_type)
        chat = str(chat)
        where = {"user_id": customer_id, 'type': str(count_type)}
        user_cout = Sql(set_sql).sql_user_select('work_chat_user_cout', where, '1')
        if len(user_cout) < 1:
            filed = ('user_id', 'num', 'type', 'value', 'addtime')
            jsons = (customer_id, '1', str(count_type), chat, Sql.time())
            Sql(set_sql).sql_add('work_chat_user_cout', filed, jsons)
        else:
            if user_cout[0]['value']:
                chat = user_cout[0]['value'] + ',' + chat
            else:
                chat = chat
            chat = chat.replace('"', '').replace("'", '')
            Sql(set_sql).sql_save_count('work_chat_user_cout', customer_id, count_type, chat)
        info = Sql(set_sql).sql_user_select('work_chat_user_cout', where, '1')
        return info[0]['num'], info[0]['value']

    # 获取num统计
    def get_select(self, user_id, count_type):
        customer_id = str(user_id)
        where = {"user_id": customer_id, 'type': str(count_type)}
        info = Sql(set_sql).sql_user_select('work_chat_user_cout', where, '1')
        return info[0]['num'], info[0]['id']

    def save_work_chat_message(self, ids):
        where = 'id = ' + str(ids)
        value = "value ='',num=0"
        Sql(set_sql).sql_save('work_chat_user_cout', value, where)
        return 'ok'

    # 获取历史多轮聊天缓存
    def get_chat_list(self, user_id):
        user_id = str(user_id)
        data = self.load_data(user_id)
        if data is None:
            self.save_data(user_id, '')
        return self.load_data(user_id)

    def load_data(self, name):
        # 从文件中读取数据并进行反序列化
        # ./file/wx_token.pkl
        if os.path.exists('./file_storage/user/' + name + '.pkl'):
            with open('./file_storage/user/' + name + '.pkl', 'rb') as f:
                data = pickle.load(f)
            return data
        else:
            return None

    def save_data(self, name, data):
        file_url = './file_storage/user/'
        if not os.path.exists(file_url):
            os.makedirs(file_url)
            os.chmod(file_url, 0o777)
        # 将数据序列化为二进制格式并写入文件
        key = './file_storage/user/' + name + '.pkl'
        if os.path.exists(key):
            with open(key, 'wb') as f:
                pickle.dump(data, f)
        else:
            with open(key, 'wb') as f:
                os.chmod(key, 0o777)
                pickle.dump(data, f)
        return 'ok'

    # 日志记录
    def log_ini_add(self, title, number, log):
        filed = ('title', 'user_id', 'log', 'addtime')
        jsons = (title, str(number), log, Sql.time())
        Sql(set_sql).sql_add('log', filed, jsons)

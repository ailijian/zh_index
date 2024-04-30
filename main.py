from application.RAG.vector_search import retrieval_results


class Fase:
    def __init__(self):
        pass

    def search(self, chat):
        answer = retrieval_results(chat, 3)


from flask import Flask, request, jsonify
app = Flask(__name__)
@app.route('/request_user', methods=['POST'])
def request_user():
    user_handle = request.form.get('user_handle')
    store_handle = request.form.get('store_handle')
    user_name = request.form.get('user_name')
    store_name = request.form.get('store_name')
    chat = request.form.get('chat')
    print(user_handle, store_handle, user_name, store_name, chat)
    if not user_handle or not user_name or not chat or not store_handle or not store_name:
        return {
            'code': 500, 'msg': '参数错误'
        }
    # quse = request.args.to_dict()
    quse = request.form.to_dict()
    Chatbot().sql_time(user_handle)
    return Chatbot().index(quse)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8989)

#

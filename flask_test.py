#coding-utf8
from flask import Flask
from flask import request
import json
'''
前提：
使用python flask库
基本功能：
提供http服务，接收处理get和post请求，返回json数据或页面
测试可以使用web浏览器或postman，注意post方法传输数据是在body内部，而get方法在body外部
'''
#装饰器函数
app = Flask(__name__)
#测试flask是否正常使用
@app.route('/', methods=['GET','POST'])
def hello_world():
	return 'Hello World!'
#测试get方法
@app.route('/get',methods = ['GET'])
def test_get():
	if request.args.get('name',''):
		return 'Hello,admin!'
	p=request.args.get('name','')#get方法采用该命令接收参数
	return 'bad username or password.%s'%p
#测试post方法
@app.route('/signin', methods = ['post'])
def test_post():
	if request.json['id']== 3:
		print(request.json['content'])#如果传输采用json传，可以用该方法接收参数
		return 'Hello,admin!'
	return 'bad username or password.'
#捕获异常，返回json数据
@app.route('/es',methods = ['GET'])
def test_get():
	import json
	try:
		if request.args.get('key_word',''):
			key_word=request.args.get('key_word','')
			if request.args.get('page',''):
				page=request.args.get('page','')
				if request.args.get('size',''):
					size=request.args.get('size','')
					res=key_word+str(page)+str(size)
					return json.dumps(res,ensure_ascii=False)
				res=key_word+str(page)
				return json.dumps(res,ensure_ascii=False)
			res=key_word
			return json.dumps(res,ensure_ascii=False)
	except Exception as e:
		print(str(e))

if __name__ == '__main__':
	#debug模式可以让代码修改后立即生效，不必重新运行代码，重启服务
	app.run(debug = True)
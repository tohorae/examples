# coding=utf8
#增加分页功能，默认页数为1
from flask import Flask
from flask import request
from datetime import datetime
from elasticsearch import Elasticsearch

app = Flask(__name__)
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
	app.run(debug = True)
#coding=utf8
from datetime import datetime
from elasticsearch import Elasticsearch
import json
'''
前提：
使用python官方的elasticsearch库来实现，直接查询可使用es的client网页版或postman进行。
例子实现功能：
用python连接es数据库，并进行相关查询，同时高亮指定字段内容
基本概念：
索引=数据库 类型index=表
通过http请求传递json数据进行查询
参考文献：
es官方指南中译版https://www.gitbook.com/book/looly/elasticsearch-the-definitive-guide-cn/details
elasticsearch-py官方文档 https://elasticsearch-py.readthedocs.io/en/master/
'''

'''
官方文档例子
'''
#创建索引和类型
doc = {
    'author': 'kimchy',
    'text': 'Elasticsearch: cool. bonsai cool.',
    'timestamp': datetime.now(),
}
res = es.index(index="test-index", doc_type='tweet', id=1, body=doc)
print(res['created'])
#返回指定ID
res = es.get(index="test-index", doc_type='tweet', id=1)
print(res['_source'])
#刷新表
es.indices.refresh(index="test-index")
#查询
res = es.search(index="test-index", body={"query": {"match_all": {}}})
print("Got %d Hits:" % res['hits']['total'])
for hit in res['hits']['hits']:
    print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])

'''
改写基本查询例子
'''
#连接服务器数据库
es = Elasticsearch(host='192.168.120.90',port=9200)
#设定查询参数
form_option=['sourceOrganization','abstract']
keyword='中国'
current_type=["JournalPaper","ConferencePaper","Thesis"]
#创建查询进行检索
# res = es.search(index="scholar_paper",doc_type=current_type,body={"query": {"match_phrase":{form_option:keyword}}})
res = es.search(index="scholar_paper",doc_type=current_type,body={"query": {"multi_match":{"query":keyword,"fields":form_option,"type":"phrase"}}})
#输出结果测试查询的有效性
print("Got %d Hits:" % res['hits']['total'])

'''
基本查询并高亮指定字段
'''
es = Elasticsearch(host='192.168.120.90',port=9200)
form_option="_all"
keyword='中国'
current_type=["JournalPaper","ConferencePaper","Thesis"]
#高亮摘要字段的关键字，即使不在摘要中检索也高亮关键字
# current_body='{"query": {"match_phrase":{"%s":"%s"}}}'%(form_option,keyword)
# res = es.search(index="scholar_paper",doc_type=current_type,body={"query": {"match_phrase":{form_option:keyword}},"highlight":{"fields":{"abstract":{},"require_field_match":False}}})
#高亮的标签替换，高亮输出的片段数为0.高亮两个字段
res = es.search(index="scholar_paper",doc_type=current_type,body={"query": {"multi_match":{"query":keyword,"fields":form_option,"type":"phrase"}},"highlight":{"fields":{"number_of_fragments":0,"pre_tags" : ["<span>"], "post_tags" : ["</span>"] ,"abstract":{},"title"{}},"require_field_match": False}})

print("Got %d Hits:" % res['hits']['total'])
#输出高亮结果，与result并列的字典
print("The first result is: %s" %json.dumps(res['hits']['hits'][0]['highlight'],ensure_ascii=False) )

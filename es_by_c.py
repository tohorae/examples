# encoding:utf-8
import json
from elasticsearch import Elasticsearch

class Search():
    """
    ES搜索类
    """
    def __init__(self):
        """
        基本的配置信息
        :return:
        """
        self.host = "192.168.120.90"
        self.port = 9200
        # self.index = "zjp-index:scholarkr_index(1)"
        self.index = "scholarkr"
        self.doc_type = ['ConferencePaper', 'JournalPaper', 'Thesis']
        self.body_type = ["name^10","abstract^5","author^2","sourceOrganization"]
        self.preference= "primary"
        self.s = Elasticsearch([{"host": self.host, "port": self.port}])

    def generate_query(self, pap_type, body_type, keyvalue, sort, filter_condition=""):
        """
        生成查询语句(此查询语句仅供查询结果使用)
        :param pap_type:文献类型, 分为三类 学术 | 期刊 | 学位
        :param body_type:文献搜索位置, 全文 | 标题 | 作者 | 单位 | 摘要
        :param keyvalue:搜索关键字
        :return:返回字典 dict
        """
        dict = {}
        """
        如果为all则在['ConferencePaper', 'JournalPaper', 'Thesis']中查找,否则只在单个type中查找
        """

        if pap_type == "all":
            dict['doc_type'] = self.doc_type
        else:
            dict['doc_type'] = pap_type

        """
        如果为all则在["name","abstract","author","sourceOrganization"]中查找,否则只在单个field中查找
        """
        if body_type == "all":
            highlight_field = "*"
            match_field = self.body_type
        else:
            match_field = body_type
            highlight_field = body_type

        """
        查询结构体
        """

        # filter_condition = '{"term": {"relatedResearchTopic.raw": "数据挖掘"}},{"term": {"relatedResearchTopic.raw": "机器学习"}},{"term": {"relatedResearchTopic.raw": "数据挖掘"}},{"term": {"sourceOrganization.raw": "EducationalOrganization/1000003909|中国科学院大学"}}'
        if filter_condition:
            org_con = filter_condition.split("$+$")[0]
            subject_con = filter_condition.split("$+$")[1]
            if sort == "none":
                """
                没有什么排序
                """
                dict['body'] = json.dumps({
                    "query": {
                        "multi_match" : {
                            "query" : keyvalue,
                            "fields" : match_field,
                            "type" : "phrase",
                            "slop":10
                        }
                    },
                    "filter": {
                    "bool": {
                      "should":[
                        org_con
                      ],
                        "should":[
                        subject_con
                      ]
                    }
                },
                    "highlight":{
                        "fields": {
                          highlight_field: {}
                        },
                        "require_field_match": False
                    }
                })
            elif sort == "sensitiveness":
                """
                敏感性排序
                """
                dict['body'] = json.dumps({
                    "query": {
                        "multi_match" : {
                            "query" : keyvalue,
                            "fields" : match_field,
                            "type" : "phrase",
                            "slop":10
                        }
                    },
                    "sort": {
                        "sensibility":
                            { "order": "desc" }
                    },
                    "highlight":{
                        "fields": {
                          highlight_field: {}
                        },
                        "require_field_match": False
                    }
                })
        else:
            if sort == "none":
                """
                没有什么排序
                """
                dict['body'] = json.dumps({
                    "query": {
                        "multi_match" : {
                            "query" : keyvalue,
                            "fields" : match_field,
                            "type" : "phrase",
                            "slop":10
                        }
                    },
                    "highlight":{
                        "fields": {
                          highlight_field: {}
                        },
                        "require_field_match": False
                    }
                })
            elif sort == "sensitiveness":
                """
                敏感性排序
                """
                dict['body'] = json.dumps({
                    "query": {
                        "multi_match" : {
                            "query" : keyvalue,
                            "fields" : match_field,
                            "type" : "phrase",
                            "slop":10
                        }
                    },
                    "sort": {
                        "sensibility":
                            { "order": "desc" }
                    },
                    "highlight":{
                        "fields": {
                          highlight_field: {}
                        },
                        "require_field_match": False
                    }
                })


        return dict

    def s_search(self, pap_type, body_type, keyvalue, from_size, page_size, sort, filter_condition=""):
        """
        :param pap_type:文献类型, 分为三类 学术 | 期刊 | 学位
        :param body_type:文献搜索位置, 全文 | 标题 | 作者 | 单位 | 摘要
        :param keyvalue:搜索关键字
        :param from_size起始数   page_size每页数量
        :return:返回搜索结果
        """

        """
        初始化参数
        """
        dict = {}  #定义查询字典
        context = {}   #定义返回数据

        """
        定义查询key-value
        """
        dict = self.generate_query(pap_type, body_type, keyvalue, sort)
        dict['index'] = self.index
        dict['from_'] = from_size
        dict['size'] = page_size
        #dict['q'] = keyvalue
        print dict['body']


        """
        生成结果
        """
        results = self.s.search(**dict)

        """
        对结果进行提取
        """
        context['total'] = results['hits']['total']          #数据总数
        context['time'] = results['took']                    #数据时间
        context["result_content"] = results['hits']['hits']  #数据内容

        return context


    def card_search(self, doc_type, name, from_size, page_size):
        """
        查询到组织机构
        :param doc_type:所查询的type
        :param id:查询得到ID
        :return: 查询信息的字典
        """
        query = json.dumps({
                "query": {
                    "match_phrase":{
                        "name":{
                            "query": name,
                            "slop":8,
                        },


                    }
                }
            })
        # query = json.dumps({
        #         "multi_match": {
        #             "query": name,
        #             "type":       "best_fields",
        #             "fields":     [ "ConferencePaper" ],
        #         }
        #     })
        dict = {}
        context = {}
        dict['index'] = self.index
        dict['doc_type'] = doc_type
        dict['body'] = query
        dict['from_'] = from_size
        dict['size'] = page_size
        dict['preference'] = self.preference

        """
        生成结果
        """
        results = self.s.search(**dict)

        """
        对结果进行提取
        """
        context['total'] = results['hits']['total']          #数据总数
        context["result_content"] = results['hits']['hits']  #数据内容

        return context

    def graph_search(self, name, from_size, page_size="all"):
        """
        查询到组织机构
        :param doc_type:所查询的type
        :param id:查询得到ID
        :return: 查询信息的字典
        """
        query = json.dumps({
                "query": {
                    "match_phrase":{
                        "_all": name
                    }
                }
            })
        dict = {}
        context = {}
        dict['index'] = self.index
        #dict['doc_type'] = doc_type
        dict['body'] = query
        dict['from_'] = from_size
        if page_size != "all":
            dict['size'] = page_size

        """
        生成结果
        """
        results = self.s.search(**dict)

        """
        对结果进行提取
        """
        context['total'] = results['hits']['total']          #数据总数
        context["result_content"] = results['hits']['hits']  #数据内容

        return context


    def search_in_id(self, id, type, from_size, page_size):
        """
        查寻某一节点的信息
        :param type:所查询的type
        :param id:查询得到ID
        :return: 查询信息的字典
        """
        query = json.dumps({
                "query": {
                    "match_phrase":{
                        "_id": id
                    }
                }
            })
        dict = {}
        context = {}
        dict['index'] = self.index
        dict['doc_type'] = type
        dict['body'] = query
        dict['from_'] = from_size
        dict['size'] = page_size

        """
        生成结果
        """
        results = self.s.search(**dict)

        """
        对结果进行提取
        """
        context['total'] = results['hits']['total']          #数据总数
        context["result_content"] = results['hits']['hits']  #数据内容

        return context

    def list_agg_search(self, pap_type, body_type, keyvalue, agg_fields):
        """
        聚合查询
        :param pap_type:文献类型, 分为三类 学术 | 期刊 | 学位
        :param body_type:文献搜索位置, 全文 | 标题 | 作者 | 单位 | 摘要
        :param keyvalue:搜索关键字
        :param agg_fields: 聚合字段 主题|机构
        :return: 聚合结果 字典
        """
        dict = {}
        """
        如果为all则在['ConferencePaper', 'JournalPaper', 'Thesis']中查找,否则只在单个type中查找
        """
        dict['index'] = self.index

        if pap_type == "all":
            dict['doc_type'] = self.doc_type
        else:
            dict['doc_type'] = pap_type

        """
        如果为all则在["name","abstract","author","sourceOrganization"]中查找,否则只在单个field中查找
        """
        if body_type == "all":
            highlight_field = "*"
            match_field = self.body_type
        else:
            match_field = body_type
            highlight_field = body_type

        """
        查询语句
        """
        agg_fields = agg_fields + ".raw"

        dict['body'] = json.dumps({
                "query": {
                    "multi_match" : {
                        "query" : keyvalue,
                        "fields" : match_field,
                        "type" : "phrase",
                        "slop":10
                    }
                },
                  "aggs": {
                    "all_journals": {
                      "terms": {
                        "field": agg_fields,
                        "size": 5
                      }
                    }
                  }
            })


        """
        生成结果
        """
        results = self.s.search(**dict)

        return results

    def find_one_by_id(self, doc_type, id):
        """
        通过ID在指定的type中查找出
        :param doc_type:所查询的type
        :param id:查询得到ID
        :return: 查询信息的字典
        """
        query = json.dumps({
          "query": {
            "match": {
              "_id": id
            }
          }
        })
        dict = {}
        context = {}
        dict['index'] = self.index
        dict['doc_type'] = doc_type
        dict['body'] = query

        results = self.s.search(**dict)

        """
        对结果进行提取
        """
        context['total'] = results['hits']['total']          #数据总数
        context["result_content"] = results['hits']['hits']  #数据内容

        return context



if __name__ == "__main__":
    s = Search()
    # res = s.s_search("all", "all", "中国科学院信息工程研究所", 1, 5, "none")
    res = s.find_one_by_id("Person", "1000137817")
    print res["result_content"]
    #context = s.graph_search("Person/1000188669|柳厅文", 0)
    # print res['total']
    # print res['time']
    #print res['result_content'][0]
    # res = s.list_agg_search("all", "all", "大数据", "sourceOrganization")
    # print res['aggregations']
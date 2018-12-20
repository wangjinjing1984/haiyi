import xlrd
from haiyi.tools.es_handler import ES_Conn, bulk_index, create_new_index
import json
import jieba
from django.conf import settings
import os
from xml.sax.saxutils import escape

def read_xls(index):
    xls_file = os.path.join(settings.BASE_DIR, settings.STATIC_URL, 'products11.23.xls')
    workbook = xlrd.open_workbook(xls_file, on_demand=True)
    worksheet = workbook.sheet_by_index(0)
    i = 2
    cell = worksheet.cell(i, 0)
    try:
        # yield temp_src
        while (cell):
            product_name = jieba.cut_for_search(worksheet.cell(i, 1).value)
            data = {
                '_index': index,
                '_type': 'doc',  # '_type' field is discouraged since ES 6.x, just use the 'doc' as default
                '_source': {
                    'model_id': worksheet.cell(i, 0).value,
                    'name': ' '.join(product_name),
                    'real_name': worksheet.cell(i, 1).value,
                    'quantity': worksheet.cell(i, 2).value,
                    'price_3w': worksheet.cell(i, 3).value,
                    'price_1w': worksheet.cell(i, 4).value,
                    'price_3k': worksheet.cell(i, 5).value,
                    'price_retail': worksheet.cell(i, 6).value,
                },
                '_id': worksheet.cell(i, 0).value,
                'doc_as_upsert': True,
                '_op_type': 'index'
            }
            yield data
            i += 1
            cell = worksheet.cell(i, 0)
    except Exception as e:
        print(f'exception:{e}')


es = ES_Conn()
es.conn(hosts=['localhost', 'elasticsearch_haiyi'], port=9200, es_payload_limit=100)


def index_docs():
    index = 'haiyi_es'
    result = create_new_index(es.es, index)
    print(result)
    succ, fail = bulk_index(es=es.es, index=index, generator=read_xls)
    print(succ, fail)


def search(message):
    message = ' '.join(jieba.cut_for_search(message))
    print('keyword=%s' % message)
    es_request = []
    # req_head = json.dumps({'index': 'haiyi_es'}) + ' \n'
    req_body = {'query': {'match': {'name': message}}}
    # es_request.append(req_head)
    es_request.append(json.dumps(req_body) + ' \n')
    res = es.es.search(index='haiyi_es', body=req_body, request_timeout=120)
    docs = []
    for hit in res.get('hits', {}).get('hits'):
        src = hit['_source']
        pname= escape(src['real_name'].strip())
        str = f"<a href='www.baidu.com'>{pname}({src['model_id'].replace('.','-')})</a>\n" \
              f"库存: {src['quantity']}\n" \
              f"3万批价: {src['price_3w']}元\n" \
              f"1万批价：{src['price_1w']}元\n" \
              f"3千批价：{src['price_3k']}元\n" \
              f"零售价格：{src['price_retail']}元\n"
        docs.append(str)
    return docs

    # index_docs()
    # search('美丽工匠')
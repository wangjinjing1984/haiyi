import xlrd
from haiyi.tools.es_handler import bulk_index, create_new_index
import json
import jieba
from django.conf import settings
import os
import logging
import traceback

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def check_type(data_value, data_type):
    if data_type == 'float':
        try:
            float(data_value if data_value else 0)
        except ValueError:
            logger.error('check_type_inconsistent|value=%s, type=%s', data_value, data_type)
            return False
    if data_type == 'int':
        try:
            int(data_value if data_value else 0)
        except ValueError:
            logger.error('check_type_inconsistent|value=%s, type=%s', data_value, data_type)
            return False
    return True


def get_line(worksheet, i, columns_num):
    v = []
    for j in range(columns_num):
        v.append('%s' % worksheet.cell(i, j).value)
    line = '%s,%s\n' % (i, ','.join(v))
    return line


def read_xls(index, xls_file):
    # xls_file = os.path.join(settings.BASE_DIR, settings.UPLOAD_FOLDER, 'products11.23.xls')
    logging.info('read_xls|index=%s, xls_file=%s', index, xls_file)
    workbook = xlrd.open_workbook(xls_file, on_demand=True)
    worksheet = workbook.sheet_by_index(0)
    wrong_rows = open(os.path.join(settings.UPLOAD_FOLDER, 'exception.csv'), 'w')
    i = 2
    cell = worksheet.cell(i, 0)
    all_ok = True
    try:
        # yield temp_src
        while (cell):
            product_name = jieba.cut_for_search(worksheet.cell(i, 1).value)
            columns = [
                ('model_id', 'str'),
                ('real_name', 'str'),
                ('quantity', 'int'),
                ('real_cost', 'float'),
                ('market_cost', 'float'),
                ('price_3w', 'float'),
                ('price_1w', 'float'),
                #('price_3k', 'float'),
                ('price_retail', 'float'),
                ('hot', 'str'),
                ('difficulty', 'str'),
                #修改后的工作表列
                ('cust_clear_free', 'float'),
                ('vip_price', 'float'),
                ('customer_message', 'str'),
                ('product_hk_info', 'str'),
                ('dutyfree_storeprice', 'float'),
                ('hot_sell_product', 'str'),
                ('findpro_help', 'str')
            ]
            j = 0
            src = {}
            column_ok = True
            for c in columns:
                v = worksheet.cell(i, j).value
                if not check_type(data_type=c[1], data_value=v):
                    wrong_rows.write(get_line(worksheet, i, len(columns)))
                    all_ok = False
                    column_ok = False
                    break
                if c[1] == 'str':
                    v = ('%s' % v).strip()
                elif c[1] == 'int':
                    v = int(v) if v else 0
                elif c[1] == 'float':
                    v = round(float(v), 2) if v else 0.0
                src[c[0]] = v
                j += 1
            if column_ok:
                src['name'] = ' '.join(product_name)
                data = {
                    '_index': index,
                    '_type': 'doc',  # '_type' field is discouraged since ES 6.x, just use the 'doc' as default
                    '_source': src,
                    '_id': worksheet.cell(i, 0).value,
                    'doc_as_upsert': True,
                    '_op_type': 'index'
                }
                yield data
            i += 1
            cell = worksheet.cell(i, 0)
    except Exception as e:
        logger.error(f'exception:{traceback.format_exc()}')
    finally:
        workbook.release_resources()
        if all_ok:
            wrong_rows.write('all ok，excel 行数=%s' % i)
        wrong_rows.close()


def index_docs(xls_file):
    index = 'haiyi_es'
    result = create_new_index(index)
    print(result)
    succ, fail = bulk_index(index=index, xls_file=xls_file, generator=read_xls)
    logger.info('indexing|succ=%s, fail=%s', succ, fail)
    return succ

    # index_docs()
    # search('美丽工匠')

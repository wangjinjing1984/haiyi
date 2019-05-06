from django.db import models
from django.conf import settings
from haiyi.products.parser import index_docs
import os


class ProductsFile(models.Model):
    id = models.AutoField(primary_key=True)
    file = models.FileField('批量文件', upload_to=settings.UPLOAD_FOLDER)
    pub_date = models.DateTimeField('上传时间', auto_now_add=True)
    products_count = models.IntegerField('商品总数', default=0)
    wrong_rows = models.TextField(default='', null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(ProductsFile, self).save(force_insert, force_update, using, update_fields)
        xls_file = self.file.name
        self.products_count = index_docs(xls_file)
        with open(os.path.join(settings.UPLOAD_FOLDER, 'exception.csv')) as r:
            self.wrong_rows = r.read()
        super(ProductsFile, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return '%s' % self.file.name


class AInfo(models.Model):
    id = models.AutoField(primary_key=True)
    amount = models.IntegerField('库存数量', default=0)
    actual_cost = models.FloatField('实际成本', null=True)
    market_cost = models.FloatField('市场成本', null=True)
    price_3w = models.FloatField('3w零售价', null=True)
    price_1w = models.FloatField('1w零售价', null=True)
    price_retail = models.FloatField('零售价格', null=True)
    hot_sell_degree = models.CharField('热卖程度', max_length=10, null=True)
    buy_difficulty = models.CharField('采购难度', max_length=10, null=True)


class BInfo(models.Model):
    id = models.AutoField(primary_key=True)
    #market_cost_price = models.FloatField('市场成本', null=True)
    cust_clear_free = models.FloatField('清关费用', null=True)
    vip_price = models.TextField('活动特价', null=True)
    customer_message = models.TextField('客户留言', null=True)
    product_hk_info = models.TextField('刷货到香港返点信息', null=True)
    dutyfree_storeprice = models.FloatField('免税店价格', null=True)
    hot_sell_product = models.TextField('热卖款', null=True)
    findpro_help = models.TextField('帮助找货', null=True)


class HaiyiProduct(models.Model):
    id = models.AutoField(primary_key=True)
    a_info = models.ForeignKey(
        AInfo,
        null=True,
        on_delete=models.CASCADE,
    )
    b_info = models.ForeignKey(
        BInfo,
        null=True,
        on_delete=models.CASCADE,
    )


class HaiyiUser(models.Model):
    id = models.AutoField(primary_key=True)
    pub_date = models.DateTimeField('加入日期', auto_now_add=True)
    end_date = models.DateTimeField('会员截止', null=False)
    active = models.BooleanField('激活', default=False)
    open_id = models.TextField('Open Id', null=False, blank=False)
    name = models.TextField('名字', null=False, blank=False)
    account_id = models.TextField('微信号', null=True, blank=True)

    indexes = [
        models.Index(fields=['open_id', ]),
    ]

    def __str__(self):
        return '%s(%s)' % (self.name, self.account_id)


class ThirdPartyProduct(models.Model):
    id = models.AutoField(primary_key=True)
    source = models.TextField('商品来源', null=False, blank=False)
    category = models.TextField('商品类型', null=False, blank=False)
    name = models.TextField('商品名称', null=False, blank=False)
    price = models.TextField('商品价格', null=False, blank=False)
    brief = models.TextField('商品简介', null=False, blank=False)
    detail = models.TextField('商品详情', null=False, blank=False)

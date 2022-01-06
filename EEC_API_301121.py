#Update function connection test 30112021

from flask import Flask,request,jsonify,Response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import  Marshmallow

import requests
import pymcprotocol
import threading
import json

from sqlalchemy.sql.expression import null

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///EEC.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///EEC2.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

######DATABASE SECTION#######
#####Basket arrival DB
class Basket_arrival(db.Model):

    id = db.Column(db.Integer,primary_key=True)
    basketNo = db.Column(db.String(100))
    stockQty = db.Column(db.String(100))
    pickQty = db.Column(db.String(100))
    workType = db.Column(db.String(100))
    arrivalDateTime = db.Column(db.String(200))

    def __init__(self,basketNo,stockQty,pickQty,workType,arrivalDateTime):
        self.basketNo = basketNo
        self.stockQty = stockQty
        self.pickQty = pickQty
        self.workType = workType
        self.arrivalDateTime = arrivalDateTime

class  BasketSchema(ma.Schema):
    class Meta:
        fields = ("basketNo","stockQty","pickQty","workType","arrivalDateTime")
        ordering = ['-id']
basket_schema = BasketSchema()
baskets_schema = BasketSchema(many=True)


#####StorageResult DB
class Storage_result(db.Model):

    id = db.Column(db.Integer,primary_key=True)
    itemCode = db.Column(db.String(100))
    basketNo = db.Column(db.String(100))
    locationNo = db.Column(db.String(100))
    storageQty = db.Column(db.String(100))
    storageDateTime = db.Column(db.String(200))

    def __init__(self,itemCode,basketNo,locationNo,storageQty,storageDateTime):
        self.itemCode = itemCode
        self.basketNo = basketNo
        self.locationNo = locationNo
        self.storageQty = storageQty
        self.storageDateTime = storageDateTime

class  StorageSchema(ma.Schema):
    class Meta:
        fields = ("itemCode","basketNo","locationNo","storageQty","storageDateTime")
storage_schema = StorageSchema()
storages_schema = StorageSchema(many=True)


######PickingResult DB
class Picking_result(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    orderNo = db.Column(db.String(100))
    itemCode = db.Column(db.String(100))
    customerName = db.Column(db.String(100))
    basketNo = db.Column(db.String(100))
    pickQty = db.Column(db.String(100))
    shortageQty = db.Column(db.String(100))
    remainStockQty = db.Column(db.String(100))
    pickDateTime = db.Column(db.String(200))

    def __init__(self,orderNo,itemCode,customerName,basketNo,pickQty,shortageQty,remainStockQty,pickDateTime):
        self.orderNo = orderNo
        self.itemCode = itemCode
        self.customerName = customerName
        self.basketNo = basketNo
        self.pickQty = pickQty
        self.shortageQty = shortageQty
        self.remainStockQty = remainStockQty
        self.pickDateTime = pickDateTime

class  PickingSchema(ma.Schema):
    class Meta:
        fields = ("orderNo","itemCode","customerName","basketNo","pickQty","shortageQty","remainStockQty","pickDateTime")
picking_schema = PickingSchema()
pickings_schema = PickingSchema(many=True)

#######StockReport DB
class Stock_report(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    itemCode = db.Column(db.String(100))
    basketNo = db.Column(db.String(100))
    locationNo = db.Column(db.String(100))
    stockQty = db.Column(db.String(100))
    reportDateTime = db.Column(db.String(200))

    def __init__(self,itemCode,basketNo,locationNo,stockQty,reportDateTime):
        self.itemCode = itemCode
        self.basketNo = basketNo
        self.locationNo = locationNo
        self.stockQty = stockQty
        self.reportDateTime = reportDateTime

class  StockSchema(ma.Schema):
    class Meta:
        fields = ("itemCode","basketNo","locationNo","stockQty","reportDateTime")
stock_schema = StockSchema()
stocks_schema = StockSchema(many=True)

#######StoragePlan DB
class Storage_plan(db.Model):

    id = db.Column(db.Integer,primary_key=True)
    itemCode = db.Column(db.String(100))
    requestDatetime = db.Column(db.String(200))

    def __init__(self,itemCode,requestDatetime):
        self.itemCode = itemCode
        self.requestDatetime = requestDatetime
        
class  StorageplanSchema(ma.Schema):
    class Meta:
        fields = ("itemCode","requestDatetime")
storageplan_schema = StorageplanSchema()
storagesplan_schema = StorageplanSchema(many=True)

#######PickingPlan DB
class Picking_plan(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    orderNo = db.Column(db.String(100))
    itemCode = db.Column(db.String(100))
    customerName = db.Column(db.String(500))
    requestDateTime = db.Column(db.String(200))

    def __init__(self,orderNo,itemCode,customerName,requestDateTime):
        self.orderNo = orderNo
        self.itemCode = itemCode
        self.customerName = customerName
        self.requestDateTime = requestDateTime
        

class  PickplanSchema(ma.Schema):
    class Meta:
        fields = ("orderNo","itemCode","customerName","requestDateTime")
pickplan_schema = PickplanSchema()
pickplans_schema = PickplanSchema(many=True)

#######################################################################################
######API DATA SECTION#######
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@----------------BASKET arrival Report

#BASKET arrival GET
@app.route('/basket',methods=['GET'])
def basket_get():
    #For WebBronwser 
    basket_web = Basket_arrival.query.all()
    _basket_web = baskets_schema.dump(basket_web)

    return jsonify(_basket_web)

# @app.route('/basket/<id>',methods=['GET'])
# def basket_select(id):
#     basket_select = Basket_arrival.query.get(id)
#     return basket_schema.jsonify(basket_select)

#BASKET arrival POST
@app.route('/BasketArrivalReport',methods=['POST'])
def basket_post():

    #print(request.method)
    if request.method == 'POST':
        basketNo = request.json['basketNo']
        stockQty = request.json['stockQty']
        pickQty = request.json['pickQty']
        workType = request.json['workType']
        arrivalDateTime = request.json['arrivalDateTime']

        my_basket = Basket_arrival(basketNo,stockQty,pickQty,workType,arrivalDateTime)
        db.session.add(my_basket)
        db.session.commit()

        #TEST FOR BASKET NO GET
        _count = Basket_arrival.query.count()
        item = _count-1
        basket_all = Basket_arrival.query.all()

        basket_no=[]
        pick_qty=[]
        stock_qty=[]
        work_type=[]
        arrive_date=[]
        for baskets in basket_all:

            basket_no.append(baskets.basketNo)
            pick_qty.append(baskets.pickQty)
            stock_qty.append(baskets.stockQty)
            work_type.append(baskets.workType)
            arrive_date.append(baskets.arrivalDateTime)

        Basket_1 = convert_basketno(basket_no,item)
        Stockqty_1 = convert_stockqty(stock_qty,item)
        Pickqty_1 = convert_pickqty(pick_qty,item)
        Worktype_1 = convert_worktype(work_type,item)
        Datetime_1 = convert_datetime(arrive_date,item)
        print("BASKET ARRIVAL REPORT DATA FROM WN TO PLC (Check Method)")
        plc_baskets(Basket_1,Stockqty_1,Pickqty_1,Worktype_1,Datetime_1)


    return basket_schema.jsonify(my_basket)

####BASKET ARRIVAL DELETE
@app.route('/post_delete/<id>',methods=['DELETE'])
def post_delete(id):
    tote_del = Basket_arrival.query.get(id)
    db.session.delete(tote_del)
    db.session.commit()

    return basket_schema.jsonify(tote_del)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@----------------STORAGE RESULT

#STORAGE Result GET
@app.route('/storage',methods= ['GET'])
def storage_get():
    storage_web = Storage_result.query.all()
    _storage_web = storages_schema.dump(storage_web)

    return jsonify(_storage_web)

# @app.route('/storage/<id>',methods=['GET'])
# def storage_select(id):
#     storage_select = Storage_result.query.get(id)
#     return storage_schema.jsonify(storage_select)

#STORAGE Result POST
@app.route('/StorageResult',methods=['POST'])
def storage_post():
    itemCode = request.json['itemCode']
    basketNo = request.json['basketNo']
    locationNo = request.json['locationNo']
    storageQty = request.json['storageQty']
    storageDateTime =  request.json['storageDateTime']

    my_storage = Storage_result(itemCode,basketNo,locationNo,storageQty,storageDateTime)
    db.session.add(my_storage)
    db.session.commit()

    #TEST FOR STORAGE NO GET
    _count = Storage_result.query.count()
    item = _count-1
    storage_all = Storage_result.query.all()
    
    item_code=[]
    basket_no=[]
    location_no=[]
    storage_qty=[]
    storage_date=[]
    for storages in storage_all:
        item_code.append(storages.itemCode)
        basket_no.append(storages.basketNo)
        location_no.append(storages.locationNo)
        storage_qty.append(storages.storageQty)
        storage_date.append(storages.storageDateTime)

    Itemcode_2 = convert_itemcode(item_code,item)
    Basket_2 = convert_basketno(basket_no,item)
    Location_2 = convert_locationno(location_no,item,)
    Storageqty_2 = convert_storageqty(storage_qty,item)
    Datetime_2 = convert_datetime(storage_date,item)
    print("STORAGE RESULT DATA FROM WN TO PLC (Check Method)")
    plc_storages(Itemcode_2,Basket_2,Location_2,Storageqty_2,Datetime_2)

    return storage_schema.jsonify(my_storage)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@----------------PICKING RESULT

#PICKING Result GET
@app.route('/picking',methods= ['GET'])
def picking_get():
    picking_web = Picking_result.query.all()
    _picking_web = pickings_schema.dump(picking_web)


    return jsonify(_picking_web)

# @app.route('/picking/<id>',methods=['GET'])
# def picking_select(id):
#     picking_select = Picking_result.query.get(id)
#     return picking_schema.jsonify(picking_select)

#PICKING Result POST
@app.route('/PickingResult',methods=['POST'])
def picking_post():

    orderNo = request.json['orderNo']
    itemCode = request.json['itemCode']
    customerName = request.json['customerName']
    basketNo = request.json['basketNo']
    pickQty = request.json['pickQty']
    shortageQty = request.json['shortageQty']
    remainStockQty = request.json['remainStockQty']
    pickDateTime =  request.json['pickDateTime']

    my_picking = Picking_result(orderNo,itemCode,customerName,basketNo,pickQty,shortageQty,remainStockQty,pickDateTime)
    db.session.add(my_picking)
    db.session.commit()

    #TEST FOR PICKING NO GET
    _count = Picking_result.query.count()
    item = _count-1
    picking_all = Picking_result.query.all()
    order_no=[]
    item_code=[]
    customer_name=[]
    basket_no=[]
    pick_qty=[]
    shortage_qty=[]
    remain_qty=[]
    pick_date=[]
    for pickings in picking_all:
        order_no.append(pickings.orderNo)
        item_code.append(pickings.itemCode)
        customer_name.append(pickings.customerName)
        basket_no.append(pickings.basketNo)
        pick_qty.append(pickings.pickQty)
        shortage_qty.append(pickings.shortageQty)
        remain_qty.append(pickings.remainStockQty)
        pick_date.append(pickings.pickDateTime)

    Orderno_3 = convert_orderno(order_no,item)
    Itemcode_3 = convert_itemcode(item_code,item)
    Customer_3 = convert_customername(customer_name,item)
    Basket_3 = convert_basketno(basket_no,item)
    Pickqty_3 = convert_pickqty(pick_qty,item)
    Shortqty_3 = convert_shortqty(shortage_qty,item)
    Remainqty_3 = convert_remainqty(remain_qty,item)
    Datetime_3 = convert_datetime(pick_date,item)
    
    #Customer_clear = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    #print("PLC Pickdata Clear")
    #plc_pickdata(Orderno_3,Itemcode_3,Customer_clear,Basket_3,Pickqty_3,Shortqty_3,Remainqty_3,Datetime_3)
    print("PICKING RESULT DATA FROM WN TO PLC (Check Method)")
    plc_pickdata(Orderno_3,Itemcode_3,Customer_3,Basket_3,Pickqty_3,Shortqty_3,Remainqty_3,Datetime_3)

    return picking_schema.jsonify(my_picking)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@----------------STOCK RESULT

#STOCK Result GET
@app.route('/stock',methods= ['GET'])
def stock_get():
    stock_web = Stock_report.query.all()
    _stock_web = stocks_schema.dump(stock_web)


    return jsonify(_stock_web)

######STOCK Result POST
@app.route('/StockReport',methods=['POST'])
def stock_post():
    itemCode = request.json['itemCode']
    basketNo = request.json['basketNo']
    locationNo = request.json['locationNo']
    stockQty = request.json['stockQty']
    reportDateTime =  request.json['reportDateTime']

    my_stock = Stock_report(itemCode,basketNo,locationNo,stockQty,reportDateTime)
    db.session.add(my_stock)
    db.session.commit()

    #TEST FOR STORAGE NO GET
    _count = Stock_report.query.count()
    item = _count-1
    stock_all = Stock_report.query.all()
    
    item_code=[]
    basket_no=[]
    location_no=[]
    stock_qty=[]
    report_date=[]
    for stocks in stock_all:
        item_code.append(stocks.itemCode)
        basket_no.append(stocks.basketNo)
        location_no.append(stocks.locationNo    )
        stock_qty.append(stocks.stockQty)
        report_date.append(stocks.reportDateTime)

    # print(item_code,basket_no,location_no,stock_qty,report_date)
    #print(item)
    # print(item_code[item])
    # print(basket_no[item])
    # print(location_no[item])
    # print(stock_qty[item])
    # print(report_date[item])

    Itemcode_4 = convert_itemcode(item_code,item)
    Basket_4 = convert_basketno(basket_no,item)
    Location_4 = convert_locationno(location_no,item)
    Stockqty_4 = convert_stockqty(stock_qty,item)
    Datetime_4 = convert_datetime(report_date,item)
    print("STOCK DATA FROM WN (Check Method)")
    plc_stocks(Itemcode_4,Basket_4,Location_4,Stockqty_4,Datetime_4)
    return stock_schema.jsonify(my_stock)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@----------------STORAGE PLAN
#STORAGE PLAN GET
@app.route('/storageplan',methods=['GET'])
def storageplan_get():
    #For WebBronwser 
    storageplan_web = Storage_plan.query.all()
    _storageplan_web = storagesplan_schema.dump(storageplan_web)

    return jsonify(_storageplan_web)

#STORAGE PLAN POST
@app.route('/storageplan',methods=['POST'])
def storageplan_post():

    #print(request.method)
    if request.method == 'POST':
        itemCode = request.json['itemCode']
        requestDateTime = request.json['requestDateTime']

        my_storageplan = Storage_plan(itemCode,requestDateTime)
        db.session.add(my_storageplan)
        db.session.commit()

    return storageplan_schema.jsonify(my_storageplan)


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@----------------PICKING PLAN
#PICKING PLAN GET
@app.route('/pickingplan',methods=['GET'])
def pickingplan_get():
    #For WebBronwser 
    pickingplan_web = Picking_plan.query.all()
    _pickingplan_web = pickplans_schema.dump(pickingplan_web)

    return jsonify(_pickingplan_web)

#PICKING PLAN POST
@app.route('/pickingplan',methods=['POST'])
def pickingplan_post():

    #print(request.method)
    if request.method == 'POST':
        orderNo = request.json['orderNo']
        itemCode = request.json['itemCode']
        customerName = request.json['customerName']
        requestDateTime = request.json['requestDateTime']

        my_pickingplan = Picking_plan(orderNo,itemCode,customerName,requestDateTime)
        db.session.add(my_pickingplan)
        db.session.commit()

    return pickplan_schema.jsonify(my_pickingplan)



#Use for create new database
#db.create_all()

##################################################################
######CONVERT DATA SECTION#######
###################################################################

def convert_basketno(basket_item,item): #8digit
    #CONVERT BASKET
    s = basket_item[item]
    #insert ,
    _s = s[:2]+','+s[2:4]+','+s[4:6]+','+s[6:] #00,00,00,09
    #split data
    _sp = _s.split(",") #['00', '00', '00', '09']
    Basket_no=[]
    for _it in _sp:
        if _it == "":
            # _it=null
            _it= 0
        else:
            _it1 = _it[:1]
            _it2 = _it[1:]
            #print(_it1)
            #print(_it2)
            if _it1 == "":
                _its1= 0
            else:
                _its1 = (ord(_it1))
            if _it2 == "":
                _its2= 0
            else:
                _its2 = (ord(_it2))
            its22 = _its2<<8
            its33 = _its1 | its22
            Basket_no.append(its33)

    #     _sps1 = sps[:1]
    #     _sps2 = sps[1:]
    #     #print(_sps1) #0
    #     #print(_sps2) #0
    #     _as1 = (ord(_sps1))
    #     _as2 = (ord(_sps2))
    #     as22 = _as2<<8
    #     as33 = _as1 | as22
    #     #print(_as1) #48
    #     #print(_as2) #57
    #     print(as33)
    #     Basket_no.append(as33)
    # #print(Basket_no) #[12336, 12336, 12336, 14640]
    return Basket_no
def convert_datetime(date_data,item): #14digit
    #CONVERT DATE TIME
    date_time = date_data[item]
    _date_time = date_time[:2]+','+date_time[2:4]+','+date_time[4:6]+','+date_time[6:8]+','+date_time[8:10]+','+date_time[10:12]+','+date_time[12:]
    #print(_date_time) #2021,09,29,12,55,19
    _date_time1 = _date_time.split(",") #['00', '00', '00', '09'] 
    Date_time=[]
    for _it in _date_time1:
        if _it == "":
            # _it=null
            _it= 0
        else:
            _it1 = _it[:1]
            _it2 = _it[1:]
            #print(_it1)
            #print(_it2)
            if _it1 == "":
                _its1= 0
            else:
                _its1 = (ord(_it1))
            if _it2 == "":
                _its2= 0
            else:
                _its2 = (ord(_it2))
            its22 = _its2<<8
            its33 = _its1 | its22
            Date_time.append(its33)
    
        # _dt1 = _dt[:1]
        # _dt2 = _dt[1:]
        # #print(_dt1) 
        # #print(_dt2) 
        # _dts1 = (ord(_dt1))
        # _dts2 = (ord(_dt2))
        # dts22 = _dts2<<8
        # dts33 = _dts1 | dts22
        # #print(_as1) #48
        # #print(_as2) #57
        # print(dts33)
        # Date_time.append(dts33)
    #print(Date_time)
    return Date_time
def convert_itemcode(itemcode_item,item): #20digit
    #CONVERT ITEM CODE
    item_code = itemcode_item[item]
    _item_code = item_code[:2]+','+item_code[2:4]+','+item_code[4:6]+','+item_code[6:8]+','+item_code[8:10]+','+item_code[10:12]+','+item_code[12:14]+','+item_code[14:16]+','+item_code[16:18]+','+item_code[18:]
    #print(_item_code) #2021,09,29,12,55,19
    _item_code1 = _item_code.split(",") #['00', '00', '00', '09']
    Item_code=[]
    for _it in _item_code1:
        if _it == "":
            _it= 0
        else:
            _it1 = _it[:1]
            _it2 = _it[1:]
            if _it1 == "":
                _its1= 0
            else:
                _its1 = (ord(_it1))
            if _it2 == "":
                _its2= 0
            else:
                _its2 = (ord(_it2))
            its22 = _its2<<8
            its33 = _its1 | its22
            Item_code.append(its33)
    return Item_code
def convert_locationno(location_item,item): #12digit
    #CONVERT LOCATION NO
    location_no = location_item[item]
    _location_no = location_no[:2]+','+location_no[2:4]+','+location_no[4:6]+','+location_no[6:8]+','+location_no[8:10]+','+location_no[10:]
    #print(_location_no) #2021,09,29,12,55,19
    _location_no1 = _location_no.split(",")
    #print(type(_location_no1)) #['00', '00', '10', '10', '00', '1 ']
    Location_no=[]
    for _it in _location_no1:
        if _it == "":
            # _it=null
            _it= 0
        else:
            _it1 = _it[:1]
            _it2 = _it[1:]
            #print(_it1)
            #print(_it2)
            if _it1 == "":
                _its1= 0
            else:
                _its1 = (ord(_it1))
            if _it2 == "":
                _its2= 0
            else:
                _its2 = (ord(_it2))
            its22 = _its2<<8
            its33 = _its1 | its22
            Location_no.append(its33)
    return Location_no
def convert_orderno(order_item,item): #20digit
    #CONVERT ORDER NO
    order_code = order_item[item]
    _order_code = order_code[:2]+','+order_code[2:4]+','+order_code[4:6]+','+order_code[6:8]+','+order_code[8:10]+','+order_code[10:12]+','+order_code[12:14]+','+order_code[14:16]+','+order_code[16:18]+','+order_code[18:]
    #print(_order_code) #2021,09,29,12,55,19
    _order_code1 = _order_code.split(",")
    #print(_order_code1) #['00', '00', '00', '09']
    Order_no=[]
    for _it in _order_code1:
        if _it == "":
            # _it=null
            _it= 0
        else:
            _it1 = _it[:1]
            _it2 = _it[1:]
            #print(_it1)
            #print(_it2)
            if _it1 == "":
                _its1= 0
            else:
                _its1 = (ord(_it1))
            if _it2 == "":
                _its2= 0
            else:
                _its2 = (ord(_it2))
            its22 = _its2<<8
            its33 = _its1 | its22
            Order_no.append(its33)
    return Order_no
def convert_customername(customer_item,item): #50digit
    #CONVERT ORDER NO
    cus_name = customer_item[item]
    _cus_name = cus_name[:2]+','+cus_name[2:4]+','+cus_name[4:6]+','+cus_name[6:8]+','+cus_name[8:10]+','+cus_name[10:12]+','+cus_name[12:14]+','+cus_name[14:16]+','+cus_name[16:18]+','+cus_name[18:20]+','+cus_name[20:22]+','+cus_name[22:24]+','+cus_name[24:26]+','+cus_name[26:28]+','+cus_name[28:30]+','+cus_name[30:32]+','+cus_name[32:34]+','+cus_name[34:36]+','+cus_name[36:38]+','+cus_name[38:40]+','+cus_name[42:44]+','+cus_name[44:46]+','+cus_name[46:48]+','+cus_name[48:]
    #print(_cus_name) #2021,09,29,12,55,19
    _cus_name1 = _cus_name.split(",")
    #print(_cus_name1) #['00', '00', '00', '09']
    Customer_name=[]
    for _it in _cus_name1:
        #print(sps)
        if _it == "":
            #_it=null
            _it= 0
            # print("NULL")
        else:
            _it1 = _it[:1]
            _it2 = _it[1:]
            # print(_it1)
            # print(_it2)
            if _it1 == "":
                _its1= 0
            else:
                _its1 = (ord(_it1))
                # print(_its1)
            if _it2 == "":
                _its2= 0
            else:
                _its2 = (ord(_it2))
                print(_its2)

            its22 = _its2<<8
            its33 = _its1 | its22
            Customer_name.append(its33)
    return Customer_name
def convert_stockqty(stock_item,item): #2digit
    #CONVERT STOCK QTY
    stock_qty = stock_item[item]
    _stock_qty = stock_qty[:2] #13
    _stock_qty1 = _stock_qty.split(",") #['13']
    Stock_qty=[]
    for _dt in _stock_qty1:
        _dt1 = _dt[:1]
        _dt2 = _dt[1:]
        if _dt1 == "":
            _dts1= 0
        else:
            _dts1 = (ord(_dt1))
        if _dt2 == "":
            _dts2 = 0
        else:
            _dts2 = (ord(_dt2))

        dts22 = _dts2<<8
        dts33 = _dts1 | dts22
        Stock_qty.append(dts33)
    return Stock_qty
def convert_remainqty(remain_item,item): #2digit
    #CONVERT REMAIN QTY
    remain_qty = remain_item[item]
    _remain_qty = remain_qty[:2]#20
    _remain_qty1 = _remain_qty.split(",")#['00']
    Remain_qty=[]
    for _dt in _remain_qty1:
        _dt1 = _dt[:1]
        _dt2 = _dt[1:]
        if _dt1 == "":
            _dts1= 0
        else:
            _dts1 = (ord(_dt1))
        if _dt2 == "":
            _dts2= 0
        else:
            _dts2 = (ord(_dt2))
        dts22 = _dts2<<8
        dts33 = _dts1 | dts22
        Remain_qty.append(dts33)
    return Remain_qty
def convert_storageqty(storage_item,item): #2digit
    #CONVERT REMAIN QTY
    storage_qty = storage_item[item]
    _storage_qty = storage_qty[:2]
    _storage_qty1 = _storage_qty.split(",")
    Storage_qty=[]
    for _dt in _storage_qty1:
        _dt1 = _dt[:1]
        _dt2 = _dt[1:]
        if _dt1 == "":
            _dts1= 0
        else:
            _dts1 = (ord(_dt1))
        if _dt2 == "":
            _dts2= 0
        else:
            _dts2 = (ord(_dt2))
        dts22 = _dts2<<8
        dts33 = _dts1 | dts22
        Storage_qty.append(dts33)
    return Storage_qty
def convert_pickqty(pick_item,item): #2digit
    #CONVERT REMAIN QTY
    pick_qty = pick_item[item]
    _pick_qty = pick_qty[:2] #5
    _pick_qty1 = _pick_qty.split(",")#['00']
    Picking_qty=[]
    for _dt in _pick_qty1:
        _dt1 = _dt[:1]
        _dt2 = _dt[1:]
        if _dt1 == "":
            _dts1= 0
        else:
            _dts1 = (ord(_dt1))
        if _dt2 == "":
            _dts2= 0
        else:
            _dts2 = (ord(_dt2))
        dts22 = _dts2<<8
        dts33 = _dts1 | dts22
        Picking_qty.append(dts33)
    return Picking_qty
def convert_shortqty(short_item,item): #1digit
    #CONVERT REMAIN QTY
    short_qty = short_item[item]
    _short_qty = short_qty[:1] #00
    _short_qty1 = _short_qty.split(",") #['00']
    Short_qty=[]
    for _dt in _short_qty1:
        _dt1 = _dt[:1]
        _dt2 = _dt[1:]

        if _dt1 == "":
            _dts1= 0
        else:
            _dts1 = (ord(_dt1))

        if _dt2 == "":
            _dts2= 0
        else:
            _dts2 = (ord(_dt2))

        dts22 = _dts2<<8
        dts33 = _dts1 | dts22
        Short_qty.append(dts33)

    return Short_qty
def convert_worktype(worktype_item,item): #1digit
    #CONVERT REMAIN QTY
    work_type = worktype_item[item]
    _work_type = work_type[:1] #00
    _work_type1 = _work_type.split(",") #['00']
    Work_type=[]
    for _dt in _work_type1:
        _dt1 = _dt[:1]
        _dt2 = _dt[1:]
        
        if _dt1 == "":
            _dts1= 0
        else:
            _dts1 = (ord(_dt1))

        if _dt2 == "":
            _dts2= 0
        else:
            _dts2 = (ord(_dt2))

        dts22 = _dts2<<8
        dts33 = _dts1 | dts22
        Work_type.append(dts33)
    
    return Work_type


######SEND DATA TO PLC SECTION#######
#BASKET ARRIVAL REPORT
def plc_baskets(Basket_1,Stockqty_1,Pickqty_1,Worktype_1,Datetime_1):
    print("PLC Basket POST data from WN (Check PLC Function)")
    #threading.Timer(1.0,plc_baskets).start()
    # Set frame type
    slmp = pymcprotocol.Type3E()
    # Set PLC type
    slmp = pymcprotocol.Type3E(plctype="iQ-R")
    # Connect PLC
    slmp.connect("192.168.1.81",8880)
    print("D8120 BasketNo:",Basket_1)
    print("D8124 StockQty:",Stockqty_1)
    print("D8126:PickingNo",Pickqty_1)
    print("D8128 WorkType:",Worktype_1)
    print("D8129 ArrivalDateTime:",Datetime_1)

    # SLMP batch word write
    slmp.batchwrite_wordunits(headdevice="D8120", values=Basket_1) #8digit
    slmp.batchwrite_wordunits(headdevice="D8124", values=Stockqty_1) #2digit
    slmp.batchwrite_wordunits(headdevice="D8126", values=Pickqty_1) #2digit
    slmp.batchwrite_wordunits(headdevice="D8128", values=Worktype_1) #1digit
    slmp.batchwrite_wordunits(headdevice="D8129", values=Datetime_1) #14digit

    if Worktype_1 == [48]:
        print("BASKET SEND M8006 TO PLC WORKTYPE 0")
        slmp.randomwrite_bitunits(bit_devices=["M8006"], values=[1]) #Using working = 0***

    if Worktype_1 == [49]:
        print("BASKET SEND M8016 TO PLC WORKTYPE 1")
        slmp.randomwrite_bitunits(bit_devices=["M8016"], values=[1]) #Using working = 1***
#STORAGE RESULT
def plc_storages(Itemcode_2,Basket_2,Location_2,Storageqty_2,Datetime_2): 
    print("PLC Storage POST data from WN (Check PLC Function)")
    #threading.Timer(1.0,plc_storages).start()
    # Set frame type
    slmp = pymcprotocol.Type3E()
    # Set PLC type
    slmp = pymcprotocol.Type3E(plctype="iQ-R")
    # Connect PLC
    slmp.connect("192.168.1.81",8880)
    print("D8040 BasketNo:",Itemcode_2)
    print("D8050 StockQty:",Basket_2)
    print("D8060:PickingNo",Location_2)
    print("D8070 WorkType:",Storageqty_2)
    print("D8072 ArrivalDateTime:",Datetime_2)

    # SLMP batch word write
    slmp.batchwrite_wordunits(headdevice="D8040", values=Itemcode_2) #20digit
    slmp.batchwrite_wordunits(headdevice="D8050", values=Basket_2) #8digit
    slmp.batchwrite_wordunits(headdevice="D8054", values=Location_2) #12digit
    slmp.batchwrite_wordunits(headdevice="D8060", values=Storageqty_2) #2digit
    slmp.batchwrite_wordunits(headdevice="D8061", values=Datetime_2) #14digit
    print("STORAGE RESULT SEND M8009 TO PLC")
    slmp.randomwrite_bitunits(bit_devices=["M8009"], values=[1])
#PICKING RESULT    
def plc_pickdata(Orderno_3,Itemcode_3,Customer_3,Basket_3,Pickqty_3,Shortqty_3,Remainqty_3,Datetime_3):
    print("PLC PICKING POST data from WN (Check PLC Function)")
    #threading.Timer(1.0,plc_pickdata).start()
    # Set frame type
    slmp = pymcprotocol.Type3E()
    # Set PLC type
    slmp = pymcprotocol.Type3E(plctype="iQ-R")
    # Connect PLC
    slmp.connect("192.168.1.81",8880)
    print("D8140 OrderNo:",Orderno_3)
    print("D8150 ItemCode:",Itemcode_3)
    print("D8160:CustomerName:",Customer_3)
    print("D8185 BasketNo:",Basket_3)
    print("D8189 PickingQty:",Pickqty_3)
    print("D8190 ShortageQty:",Shortqty_3)
    print("D8191 RemainQty:",Remainqty_3)
    print("D8192 PickDateTime:",Datetime_3)
    
    # SLMP batch word write
    slmp.batchwrite_wordunits(headdevice="D8140", values= Orderno_3) #20 digit
    slmp.batchwrite_wordunits(headdevice="D8150", values= Itemcode_3) #20 digit
    slmp.batchwrite_wordunits(headdevice="D8160", values= Customer_3) #50 digit
    slmp.batchwrite_wordunits(headdevice="D8185", values= Basket_3) #8 digit
    slmp.batchwrite_wordunits(headdevice="D8189", values= Pickqty_3) #1 digit
    slmp.batchwrite_wordunits(headdevice="D8190", values= Shortqty_3) #1 digit
    slmp.batchwrite_wordunits(headdevice="D8191", values= Remainqty_3) #2 digit
    slmp.batchwrite_wordunits(headdevice="D8192", values= Datetime_3) #14 digit

    print("PICKING RESULT SEND M8019 TO PLC")
    slmp.randomwrite_bitunits(bit_devices=["M8019"], values=[1])
    #Clear Customer data 
    #if Customer_3 == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] : 
    #    print("Customer data clear : ")
    #else:
     #   print("PICKING RESULT SEND M8020 TO PLC")
    #    slmp.randomwrite_bitunits(bit_devices=["M8020"], values=[1])

#STOCK REPORT
def plc_stocks(Itemcode_4,Basket_4,Location_4,Stockqty_4,Datetime_4):
    #print("PLC Stock POST data from WN (Check PLC Function)")
    #threading.Timer(1.0,plc_stocks).start()
    # Set frame type
    slmp = pymcprotocol.Type3E()
    # Set PLC type
    slmp = pymcprotocol.Type3E(plctype="iQ-R")
    # Connect PLC
    slmp.connect("192.168.1.81",8880)
    print("D8200 ItemCode:",Itemcode_4)
    print("D8210 BasketNo:",Basket_4)
    print("D8220:LocationNo",Location_4)
    print("D8230 StockQty:",Stockqty_4)
    print("D8232 ReportDateTime:",Datetime_4)

    #Confirm STOCK REPORT RESET Everyday
    M8025_bit = slmp.batchread_bitunits(headdevice="M8025", readsize=1)
    #if M8025_bit[0] == 0:
    #    print("STOCK SEND M8026 TO PLC")
    #    slmp.randomwrite_bitunits(bit_devices=["M8026"], values=[1]) 
    #Confirm STOCK REPORT Manual Insert 
    if M8025_bit[0] == 0:
        # SLMP batch word write
        slmp.batchwrite_wordunits(headdevice="D8200", values= Itemcode_4) #20digit
        slmp.batchwrite_wordunits(headdevice="D8210", values= Basket_4) #8digit
        slmp.batchwrite_wordunits(headdevice="D8220", values= Location_4) #12digit
        slmp.batchwrite_wordunits(headdevice="D8230", values= Stockqty_4) #2digit
        slmp.batchwrite_wordunits(headdevice="D8232", values= Datetime_4) #14digit
        print("STOCK REPORT SEND M8020 TO PLC")
        slmp.randomwrite_bitunits(bit_devices=["M8020"], values=[1]) 


######PLC START OPERATION SECTION#######
def run_plc():
    print("PLC ScanTime 2 seconds")
    threading.Timer(2.0,run_plc).start()
    # Set frame type
    slmp = pymcprotocol.Type3E()
    # Set PLC type
    slmp = pymcprotocol.Type3E(plctype="iQ-R")
    # Connect PLC
    slmp.connect("192.168.1.81",8880)
    # SLMP batch bit read M8000#
    batch_read_val_bit = slmp.batchread_bitunits(headdevice="M8000", readsize=25)
    batch_read_connection = slmp.batchread_bitunits(headdevice="M8200", readsize=5)


    #M8004 Condition
    if batch_read_val_bit[4] == 1:
        print("*****Read Storage Plan data M8004 On*****")
        # Request empty Basket data
        storage_item_code = slmp.batchread_wordunits(headdevice="D8000", readsize=10)
        #print(storage_item_code)
   
        item_result=[]
        for num in storage_item_code:
            data = int(num)
            w1 = data & 0x00ff
            w2 = data & 0xff00
            _w2 = w2>>8
            #print("W1 :",w1)
            #print("W2 :",_w2)
            a_data = (chr(w1))+(chr(_w2))
            #print("2 Char : ",a_data)
            item_result += a_data
            #print(item_result)
        str_item = ''.join(item_result)
        #print("Join Item code : ",str_item)
        _str_item = str_item.replace("\x00","",-1)
        #print("Old Item",_str_item) #Old Item 2110140003123100
        sprit_str_item = _str_item[:10]+','+_str_item[10:11]+','+_str_item[11:] #2110150001,2,7
        ####Sprit Item code data#####
        #print("Storage ItemCode:",_str_item)  #Storage ItemCode: 2110140003123100
        #sprit_str_item = _str_item[:10]+','+_str_item[10:13]+','+_str_item[13:] #2110140003,123,100
        #sprit_str_item = _str_item[:10]+','+_str_item[10:] #2110150001,27
        #print(sprit_str_item) #2110150001,27
        #_sprit_str_item = _str_item[10:]
        pen_item = _str_item[10:11]
        mouse_item = _str_item[11:]
        #print("BASKET Pen:",pen_item, "and Mouse :",mouse_item) # 2,7
        #print("Sprit Item : ",_sprit_str_item) #Sprit Item :  27
        
        #Request Data Time data
        storage_datetime = slmp.batchread_wordunits(headdevice="D8010", readsize=14)
        result=[]
        for num in storage_datetime:
            data = int(num)
            w1 = data & 0x00ff
            w2 = data & 0xff00
            _w2 = w2>>8
            #print(w1)
            #print(_w2)
            a_data = (chr(w1))+(chr(_w2))
            #print(a_data)
            result += a_data
            #print(result)
        str_date = ''.join(result)
        #print(str_date)
        _str_date = str_date.replace("\x00","",-1)
        #print(_str_date)
        
        _sprit_str_item = sprit_itemcode(int(pen_item),int(mouse_item))
        #print(_sprit_str_item)

        #print("Request Basket to WN")
        send_storage(_sprit_str_item,_str_date,slmp)


    if batch_read_val_bit[14] == 1:
        print("*****Picking Plan data M8014 On*****")
        #Request Order No'''
        picking_order_no = slmp.batchread_wordunits(headdevice="D8060", readsize=10)
        result=[]
        for num in picking_order_no:
            data = int(num)
            w1 = data & 0x00ff
            w2 = data & 0xff00
            _w2 = w2>>8
            #print(w1)
            #print(_w2)c
            a_data = (chr(w1))+(chr(_w2))
            #print(a_data)
            result += a_data
            #print(result)
        pk_order = ''.join(result)
        #print(pk_order)
        
        _pk_order = pk_order.replace("\x00","",-1)

        #Request Item Code'''
        picking_item_code = slmp.batchread_wordunits(headdevice="D8070", readsize=10)
        result=[]
        for num in picking_item_code:
            data = int(num)
            w1 = data & 0x00ff
            w2 = data & 0xff00
            _w2 = w2>>8
            #print(w1)
            #print(_w2)
            a_data = (chr(w1))+(chr(_w2))
            #print(a_data)
            result += a_data
            #print(result)
        pk_item = ''.join(result)
        #print(pk_item)
        _pk_item = pk_item.replace("\x00","",-1)

        ####Sprit Item code data#####
        #sprit_str_item = _pk_item[:10]+','+_pk_item[10:13]+','+_pk_item[13:]
        #_sprit_pk_item = _pk_item[10:13]
        
        sprit_str_item = _pk_item[:10]+','+_pk_item[10:11]+','+_pk_item[11:] #2110150001,2,7
        ####Sprit Item code data#####
        pen_item = _pk_item[10:11]
        mouse_item = _pk_item[11:]
        #print("PICKING Pen:",pen_item, "and Mouse :",mouse_item) # 2,7
        _sprit_pk_item = sprit_itemcode(int(pen_item),int(mouse_item))
   

        #Request CustomerName'''
        picking_Customer_name = slmp.batchread_wordunits(headdevice="D8080", readsize=25)
        result=[]
        for num in picking_Customer_name:
            data = int(num)
            w1 = data & 0x00ff
            w2 = data & 0xff00
            _w2 = w2>>8
            #print(w1)
            #print(_w2)
            a_data = (chr(w1))+(chr(_w2))
            #print(a_data)
            result += a_data
            #print(result)
        pk_cus_name = ''.join(result)
        #print(pk_cus_name)
        _pk_cus_name = pk_cus_name.replace("\x00","",-1)
        #print(_pk_cus_name)
        #last_len = len(_pk_cus_name)
        #print(last_len)
        # if last_len > XX:
        #     print("Last len over")
        # else:
        #     print("Lower")
        

        #Request Data Time data'''
        picking_datetime = slmp.batchread_wordunits(headdevice="D8105", readsize=14)
        result=[]
        for num in picking_datetime:
            data = int(num)
            w1 = data & 0x00ff
            w2 = data & 0xff00
            _w2 = w2>>8
            #print(w1)
            #print(_w2)
            a_data = (chr(w1))+(chr(_w2))
            #print(a_data)
            result += a_data
            #print(result)
        pk_date = ''.join(result)
        #print(pk_date)
        _pk_date = pk_date.replace("\x00","",-1)

        #SEND PICKING DATA TO WN
        #print("Request Picking to WN")
        send_picking(_pk_order,_sprit_pk_item,_pk_cus_name,_pk_date,slmp)
        
        
    #M8200 CONNECTION TEST TO WN
    if batch_read_connection[0] == 1:
        print("*****Connection Test M8200 On*****")
        
        #SEND CONNECTION TEST TO WN
        send_picking(slmp)



def sprit_itemcode(pen,mouse):
    #print(type(pen),type(mouse))
    print("Sprit Itemcode Function")
    #BLACK
    if pen == 1:
        print("Pen : 1")
        if mouse == 1:
            print("Pen Black:",pen, "Mouse:",mouse , " Send 1A1")
            _sprit_str_item = "1A1"
        elif mouse == 2:
            print("Pen Black:",pen, "Mouse:",mouse , " Send 1A2")
            _sprit_str_item = "1A2"
        elif mouse == 3:
            print("Pen Black:",pen, "Mouse:",mouse , " Send 1B1")
            _sprit_str_item = "1B1"
        elif mouse == 4:
            print("Pen Black:",pen, "Mouse:",mouse , " Send 1B2")
            _sprit_str_item = "1B2"
        elif mouse == 5:
            print("Pen Black:",pen, "Mouse:",mouse , " Send 1C1")
            _sprit_str_item = "1C1"
        elif mouse == 6:
            print("Pen Black:",pen, "Mouse:",mouse , " Send 1C2")
            _sprit_str_item = "1C2"
        elif mouse == 7:
            print("Pen Black:",pen, "Mouse:",mouse , " Send 1S(Original)")
            _sprit_str_item = "1S"
        elif mouse == 9:
            print("Pen Black:",pen, "Mouse:",mouse , " Send 1bypass")
            _sprit_str_item = "19"
    #BLUE
    elif pen == 2:
        print("Pen : 2")
        if mouse == 1:
            print("Pen Blue:",pen, "Mouse:",mouse , " Send 2A1")
            _sprit_str_item = "2A1"
        elif mouse == 2:
            print("Pen Blue:",pen, "Mouse:",mouse , " Send 2A2")
            _sprit_str_item = "2A2"
        elif mouse == 3:
            print("Pen Blue:",pen, "Mouse:",mouse , " Send 2B1")
            _sprit_str_item = "2B1"
        elif mouse == 4:
            print("Pen Blue:",pen, "Mouse:",mouse , " Send 2B2")
            _sprit_str_item = "2B2"
        elif mouse == 5:
            print("Pen Blue:",pen, "Mouse:",mouse , " Send 2C1")
            _sprit_str_item = "2C1"
        elif mouse == 6:
            print("Pen Blue:",pen, "Mouse:",mouse , " Send 2C2")
            _sprit_str_item = "2C2"
        elif mouse == 7:
            print("Pen Blue:",pen, "Mouse:",mouse , " Send 2S(Original)")
            _sprit_str_item = "2S"
        elif mouse == 9:
            print("Pen Blue:",pen, "Mouse:",mouse , " Send 2bypass")
            _sprit_str_item = "29"
    #RED
    elif pen == 3:
        print("Pen : 3")
        if mouse == 1:
            print("Pen Red:",pen, "Mouse:",mouse , " Send 3A1")
            _sprit_str_item = "3A1"
        elif mouse == 2:
            print("Pen Red:",pen, "Mouse:",mouse , " Send 3A2")
            _sprit_str_item = "3A2"
        elif mouse == 3:
            print("Pen Red:",pen, "Mouse:",mouse , " Send 3B1")
            _sprit_str_item = "3B1"
        elif mouse == 4:
            print("Pen Red:",pen, "Mouse:",mouse , " Send 3B2")
            _sprit_str_item = "3B2"
        elif mouse == 5:
            print("Pen Red:",pen, "Mouse:",mouse , " Send 3C1")
            _sprit_str_item = "3C1"
        elif mouse == 6:
            print("Pen Red:",pen, "Mouse:",mouse , " Send 3C2")
            _sprit_str_item = "3C2"
        elif mouse == 7:
            print("Pen Red:",pen, "Mouse:",mouse , " Send 3S(Original)")
            _sprit_str_item = "3S"
        elif mouse == 9:
            print("Pen Red:",pen, "Mouse:",mouse , " Send 3bypass")
            _sprit_str_item = "39"
    #BYPASS
    elif pen == [9]:
        if mouse == 1:
            print("Pen Bypass:",pen, "Mouse:",mouse , " Send 9A1")
            _sprit_str_item = "9A1"
        elif mouse == 2:
            print("Pen Bypass:",pen, "Mouse:",mouse , " Send 9A2")
            _sprit_str_item = "9A2"
        if mouse == 3:
            print("Pen Bypass:",pen, "Mouse:",mouse , " Send 9B1")
            _sprit_str_item = "9B1"
        elif mouse == 4:
            print("Pen Bypass:",pen, "Mouse:",mouse , " Send 9B2")
            _sprit_str_item = "9B2"
        elif mouse == 5:
            print("Pen Bypass:",pen, "Mouse:",mouse , " Send 9C1")
            _sprit_str_item = "9C1"
        elif mouse == 6:
            print("Pen Bypass:",pen, "Mouse:",mouse , " Send 9C2")
            _sprit_str_item = "9C2"
        elif mouse == 7:
            print("Pen Bypass:",pen, "Mouse:",mouse , " Send 9S(Original)")
            _sprit_str_item = "9S"
        else:
            print("Can not bypass")
            _sprit_str_item = "99"
    else:
        print("No data")
        _sprit_str_item = "ERR"
           
        
    return _sprit_str_item 

#*************FUNCTION FOR PLC >> DAIFUKI
#Request BASKET
def send_storage(item_storage,datetime,slmp):
    #For POST Request'''
    print("Send StoragePlan function to WN ")
    API = 'http://192.168.1.120:8094/storageplan/' #for Daifuku
    #print("Send StoragePlan function to LocalDB ")
    PLCAPI = 'http://192.168.1.105:8888/storageplan' #for local DB
    
    data1 = {
        #"ItemCode"
        "itemCode": item_storage,
        #"RequestDataTime"
        #"req_datatime": datetime,
        "requestDateTime": datetime,
    }
    
    data2 = {
        #"ItemCode"
        "itemCode": item_storage,
        #"itemCode": item_storage,

        #"RequestDataTime"
        "requestDateTime": datetime,
    }
    print("Data to Daifuku",data1) #{'itemCode': 'A000079', 'requestDateTime': '20210927133557'}
    print("Data to Local DB",data2)
    #_storage_data = json.dumps(data)
    #print(_storage_data) #{"itemCode": "A000079", "requestDateTime": "20210927133557"}
    
    
    response = requests.post(API,json=data1)
    res_plc = requests.post(PLCAPI,json=data2)
    
    print("Response TEXT to Daifuku :",response.text)
    print("Response JSON to Daifuku :",response.json)
    print("Status Code to Daifuku :",type(response.status_code))
    print("Response TEXT to PLC :",res_plc.text)
    print("Response JSON to PLC",res_plc.json)
    print("Status Code to Local DB :",type(res_plc.status_code))
    
    
    if response.status_code == 200   :
        print("send Storage plan 200 to Daifuku complete!!",response.status_code)
        slmp.randomwrite_bitunits(bit_devices=["M8005"], values=[1]) #Confirm status 200 Flag M8005 to PLC
        
    elif response.status_code == 201   :
        print("send Storage plan 201 to Daifuku complete!!",response.status_code)
        slmp.randomwrite_bitunits(bit_devices=["M8005"], values=[1]) #Confirm status 201 Flag M8005 to PLC
    else:
        print("The Storage plan data incomplete",response.status_code)
        #slmp.randomwrite_bitunits(bit_devices=["M8005"], values=[1])

#Request PICKING PLAN
def send_picking(pk_order,pk_item,pk_cus_name,pk_date,slmp):
    print("Send PickingPlan function to WN ")
    #For POST Requests'''
    #API = 'http://192.168.1.108:8000/pickingplan/?format=json'
    API = 'http://192.168.1.120:8094/pickingplan/' #for Daifuku
    PLCAPI = 'http://192.168.1.105:8888/pickingplan' #for local DB
    
    
    data3 = {
        "orderNo": pk_order,
        "itemCode": pk_item,
        "customerName":pk_cus_name,
        "requestDateTime": pk_date,
        #"req_Datetime": pk_date,
    }
    data4 = {
        "orderNo": pk_order,
        "itemCode": pk_item,
        "customerName":pk_cus_name,
        "requestDateTime": pk_date,
        #"req_Datetime": pk_date,
    }
    
    print("Data to Daifuku",data3) #{'orderNo': '0000001', 'itemCode': 'A000001', 'customerName': 'Prayuy ChanOcha', 'requestDateTime': '051021103059'}
    print("Data to Local DB",data4)
    #_data = json.dumps(data)
    response = requests.post(API,json=data3)
    res_plc = requests.post(PLCAPI,json=data4)
    #print(response.text) #{"id":7,"orderNo":"0000001","itemCode":"A000001","customerName":"Prayuy ChanOcha","req_Datetime":null,"published":"2021-10-05T07:08:06.310632Z"}
    if response.status_code == 200 :
        print("send Picking Plan 200 to Daifuku complete!!",response.status_code)
        slmp.randomwrite_bitunits(bit_devices=["M8015"], values=[1]) #Confirm status 200 Flag M8015 to PLC
    elif response.status_code == 201:
        print("send Picking Plan 201 to Daifuku complete!!",response.status_code)
        slmp.randomwrite_bitunits(bit_devices=["M8015"], values=[1]) #Confirm status 201 Flag M8015 to PLC
    else:
        print("The Picking plan data incomplete",response.status_code)
        #slmp.randomwrite_bitunits(bit_devices=["M8015"], values=[1])
    
    # print("Response TEXT to WN :",response.text)
    # print("Response JSON to WN",response.json)
    # print("Status Code to Daifuku :",type(response.status_code))
    # print("Response TEXT to PLC :",res_plc.text)
    # print("Response JSON to PLC",res_plc.json)
    # print("Status Code to Local DB :",type(res_plc.status_code))

def send_connection(slmp):
    print("Send Connection Test function to WN ")
    testapi_s = 'http://192.168.1.120:8094/storageplan/test' #for Daifuku
    testapi_p = 'http://192.168.1.120:8094/pickingplan/test' #for Daifuku

    data_s = {
        
        "itemCode": "888",
        #"req_datatime": "20210101",
        "requestDateTime": "20210101",
    }
    data_p = {
        "orderNo": "picki_Test",
        "itemCode": "999",
        "customerName":"customer_Test",
        "requestDateTime": "20210101",
        #"req_Datetime": "20210101",
    }

    print("Storage test data :",data_s)
    print("Picking test data :",data_p)
    ####Condition storage connection test
    response_s = requests.post(testapi_s,json=data_s)

    if response_s.status_code == 200 :
        print("Connection Test Complete !!!( storage 200)",response_s.status_code)
        slmp.randomwrite_bitunits(bit_devices=["M8206"], values=[1]) #Confirm status 200 Flag M8206 to PLC
    elif response_s.status_code == 201:
        print("Connection Test Complete !!!(storage 201)",response_s.status_code)
        slmp.randomwrite_bitunits(bit_devices=["M8206"], values=[1]) #Confirm status 201 Flag M8206 to PLC
    else:
        print("Connection incomplete (storage)",response_s.status_code)
        slmp.randomwrite_bitunits(bit_devices=["M8207"], values=[1]) #Confirm status 201 Flag M8207 to PLC

    ####Condition picking connection test
    response_p = requests.post(testapi_p,json=data_p)

    if response_p.status_code == 200 :
        print("Connection Test Complete !!!( storage 200)",response_p.status_code)
        slmp.randomwrite_bitunits(bit_devices=["M8208"], values=[1]) #Confirm status 200 Flag M8208 to PLC
    elif response_p.status_code == 201:
        print("Connection Test Complete !!!(storage 201)",response_p.status_code)
        slmp.randomwrite_bitunits(bit_devices=["M8208"], values=[1]) #Confirm status 201 Flag M8208 to PLC
    else:
        print("Connection incomplete (storage)",response_p.status_code)
        slmp.randomwrite_bitunits(bit_devices=["M8209"], values=[1]) #Confirm status 201 Flag M8297 to PLC

if __name__ == '__main__':
    run_plc()
    app.run(host="0.0.0.0",port="8888",debug=True)

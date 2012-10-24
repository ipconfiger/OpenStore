# encoding: utf-8
import settings
import datetime
from sqlalchemy import Column,Integer,String,DateTime,Boolean,Text,UniqueConstraint,Table, MetaData,ForeignKey
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship,backref
import utils


TABLEARGS = {
    'mysql_engine': 'InnoDB',
    'mysql_charset':'utf8'
}

class DeclaredBase(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id =  Column(Integer, primary_key=True)
    create_time = Column(DateTime,default=datetime.datetime.now())
    last_modify = Column(DateTime,default=datetime.datetime.now())

Base = declarative_base(cls=DeclaredBase)

class UserLogin(Base):
    """
    用户登陆，用于存放用户登陆验证的必要信息，作为用户标示，表明唯一用户身份
    """
    login_name = Column(String(50))        #登陆名
    password = Column(String(50))          #登陆密码
    is_ban = Column(Boolean)               #是否禁止登陆 false＝允许登陆 true＝禁止登陆
    is_delete = Column(Boolean)            #是否删除

    __table_args__ = (
        UniqueConstraint(login_name,),
        TABLEARGS
    )

    def __init__(self, login_name, raw_password):
        """
        创建新的用户登陆对象，并自动初始化密码
        @login_name: 登陆名
        @raw_password: 登陆密码原文
        """
        self.login_name = login_name
        self.password = utils.hash_passwd(raw_password)
        self.is_ban = False
        self.create_time = datetime.datetime.now()
        self.last_modify = datetime.datetime.now()
        self.is_delete = False

    def reset_password(self, new_password):
        """
        更新用户的密码
        @new_password: 新密码原文
        """
        self.password = utils.hash_passwd(new_password)
    
    def cmp_password(self, raw_password):
        """
        检测密码是否正确
        @raw_password: 输入待验证的密码
        """
        return utils.check_passwd(raw_password, self.password)



class UserProfile(Base):
    """
    用户扩展属性，用于存放用户扩展属性
    """
    user_id = Column(Integer,ForeignKey("userlogin.id")) #关联用户ID
    user = relationship('UserLogin',uselist = False,remote_side=[UserLogin.id],backref=backref('profile', remote_side=[user_id], uselist = False)) #关联用户登陆对象
    company_name = Column(String(50))         #用户显示的名称
    contact_name = Column(String(10))         #用户真实姓名
    mobile = Column(String(15))            #联系手机号码
    company_addr =Column(String(100))
    province = Column(String(50))          #省份
    city = Column(String(50))              #城市
    email = Column(String(100))            #安全邮箱地址
    icon = Column(String(150))             #头像地址
    val_email = Column(Boolean)            #邮件是否验证通过
    val_mobile = Column(Boolean)           #手机是否验证通过

    __table_args__ = (
        UniqueConstraint(user_id,),
        TABLEARGS
    )

    def __init__(self, user):
        """
        初始化用户属性，暂时不用移动电话，先用邮件验证
        @user: 用户登陆对象
        @user_name: 用户显示的名称
        @email: 注册安全邮箱
        """
        self.user_id = user.id
        self.email = user.login_name
        self.val_email = False
        self.val_mobile = False
        self.company_name = ""
        self.company_addr = ""
        self.contact_name = ""
        self.mobile = ""
        self.create_time = datetime.datetime.now()
        self.last_modify = datetime.datetime.now()


class UserAccount(Base):
    """
    用户帐户，用于开通在线支付后存储用户帐户信息
    """
    user_id = Column(Integer,ForeignKey("userlogin.id")) #关联用户ID
    user = relationship('UserLogin',uselist = False,remote_side=[UserLogin.id],backref=backref('account',remote_side=[user_id],uselist=False)) #关联用户登陆对象
    balance = Column(Integer)             #帐户余额
    transed = Column(Boolean)             #是否发生过交易
    last_trans = Column(DateTime)         #最后交易时间
    tenant_id = Column(String(32))        #关联租户
    tenant_password = Column(String(50))  #关联租户密码

    __table_args__ = (
        UniqueConstraint(user_id,),
        TABLEARGS
    ) 

    def __init__(self, user):
        """
        初始化用户帐户
        @user: 用户登陆对象
        """
        self.user_id=user.id
        self.balance = 0
        self.transed = False
        self.last_trans = datetime.datetime.now()
        self.create_time = datetime.datetime.now()
        self.last_modify = datetime.datetime.now()


class UserTenant(Base):
    user_id = Column(Integer)   #关联用户
    tenant_id = Column(String(32))        #租户ID
    tenant_name = Column(String(50))      #租户名称
    admin_user_id = Column(String(32))
    oper_password = Column(String(100))   #后台操作密码
    keypair = Column(String(2000))        #密钥对缓存
    __table_args__ = (
        UniqueConstraint(user_id,),
        TABLEARGS
    )

    def __init__(self, user):
        self.user_id = user.id


class LookKey(Base):
    key = Column(String(32))
    user_id = Column(Integer)
    __table_args__ = (
        UniqueConstraint(key,),
        TABLEARGS
    )

    def __init__(self, user_id, key):
        self.user_id = user_id
        self.key = key


class Product(Base):
    """
    产品定义，定义了产品的各项属性用于展示和作为计费标准数据使用
    """
    key = Column(String(20))               #产品编号
    name = Column(String(50))              #产品名称
    detail = Column(String(2000))          #产品详情
    cpu = Column(Integer)                  #计算单元个数
    memory = Column(Integer)               #内存大小 单位为M
    storage = Column(Integer)              #存储大小 单位为G
    flover_id = Column(String(36))         #性能指标编号
    monthly_price = Column(Integer)        #按月计费价格 单位 元
    yearly_price = Column(Integer)         #按年计费价格 单位 元

    __table_args__ = (
        UniqueConstraint(key,),
        TABLEARGS
    ) 
 
    def __init__(self, key, name, detail, cpu, memory, storage, flover_id, price_m,price_y):
        """
        初始化产品定义
        @key: 产品自定义编号
        @name: 产品名称
        @detail: 产品详细信息
        @cpu: 计算单元个数
        @memory: 内存大小
        @storage: 存储单元大小
        @flover_id: 性能指标编号
        @price_m: 按月计费价格
        @price_y: 按年计费价格
        """
        self.key = key
        self.name = name
        self.detail = detail
        self.cpu = cpu
        self.memory = memory
        self.storage = storage
        self.flover_id = flover_id
        self.monthly_price = price_m
        self.yearly_price = price_y


class Order(Base):
    """
    订单记录
    """
    serial_number = Column(String(30))     #流水号
    user_id = Column(Integer)              #关联用户编号
    total_fee = Column(Integer)            #总价
    favor_fee = Column(Integer)            #优惠后的价格
    charge_date = Column(DateTime)         #下订单的时间
    status = Column(Integer)               #订单状态 0-下单未付款 1-已付款 2－已确认付款 3-已经部署 10－用户自己取消 11-操作员取消 12-系统自动取消 13-失效

    __table_args__ = (
        UniqueConstraint(serial_number,),
        TABLEARGS
    ) 
    
    def __init__(self, user, total_fee, favor_fee):
        """
        初始化订单记录
        @user: 订单用户
        @total_fee: 总费用
        @favor_fee: 优惠费用
        @favorable_id: 优惠计划编号
        """
        self.serial_number = utils.serial_maker()
        self.user_id = user.id
        self.total_fee = total_fee
        self.favor_fee = favor_fee
        self.charge_date = datetime.datetime.now()
        self.status = 0

class OrderProduct(Base):
    """
    订单包含的产品
    """
    order_id = Column(Integer,ForeignKey("order.id")) #关联用户ID
    order = relationship('Order',uselist = True,remote_side=[Order.id],backref=backref('products',remote_side=[order_id])) #关联订单对象
    user_id = Column(Integer)              #关联用户编号
    product_key = Column(String(20),ForeignKey("product.key")) #关联产品ID
    product = relationship('Product',uselist = False,remote_side=[Product.key]) #关联产品对象
    pay_type = Column(Integer)      #租用类型 0－按月 1－按年
    price = Column(Integer)         #费用单价
    pay_timelimit = Column(Integer) #付费时限 按月就是月数，按年就是年数
    fee = Column(Integer)           #订单价格
    favor_fee = Column(Integer)     #优惠价格
    status = Column(Integer)        #订单状态 0-等待执行 1-已经部署 10－用户自己取消 11-操作员取消 12-系统自动取消 13-失效

    __table_args__ = TABLEARGS

    def __init__(self, user, order, product, pay_type, limit, favor = None):
        """
        初始化订单包含产品的数据
        @user: 用户登陆对象
        @order: 订单对象
        @product: 产品对象
        @image_id: 产品操作系统镜像编号
        @pay_type: 付费类型（按月、按年）
        @limit: 付费时间
        """
        self.order_id = order.id
        self.user_id = user.id
        self.product_key = product.key
        self.pay_type = pay_type
        if pay_type:
            self.price = product.yearly_price
        else:
            self.price = product.monthly_price
        self.pay_timelimit = limit
        if favor:
            self.favor_fee = favor.yearly_price if pay_type else favor.monthly_price
        else:
            self.favor_fee = self.price * limit
        self.fee = self.price * limit if not favor else self.favor_fee*limit
        self.status = 0

class Favorable(Base):
    """
    优惠定义
    """
    key = Column(String(20))               #优惠编码
    detail = Column(String(2000))          #详细描述
    start = Column(DateTime)               #开始生效时间
    end = Column(DateTime)                 #结束生效时间
    product_key = Column(String(20),ForeignKey("product.key")) #关联产品ID
    product = relationship('Product',uselist = False,remote_side=[Product.key]) #关联产品对象
    monthly_price = Column(Integer)        #按月计费价格 单位 元
    yearly_price = Column(Integer)         #按年计费价格 单位 元
    status = Column(Integer)               #状态 0-内部测试 1-上线运行 2-失效

    __table_args__ = (
        UniqueConstraint(key,),
        TABLEARGS
    ) 

    def __init__(self, key, detail, start, end, product, month, year):
        """
        初始化优惠定义
        @key: 优惠编码
        @detail: 优惠说明详细内容
        @start: 开始生效时间
        @end: 结束生效时间
        @code: 执行优惠的代码
        """
        self.key = key
        self.detail = detail
        self.start = start
        self.end = end
        self.product_key = product.key
        self.monthly_price = month
        self.yearly_price = year
        self.status = 0

class UserProduct(Base):
    """
    用户已经部署生效的实例
    """
    user_id = Column(Integer,ForeignKey("userlogin.id")) #关联用户ID
    product_key = Column(String(20),ForeignKey("product.key")) #关联产品ID
    instance_name = Column(String(50)) #产品实例的名称
    order_product_id = Column(Integer) #关联的订单对象ID
    image_id = Column(String(36))   #操作系统镜像编号
    server_id = Column(String(36))  #虚拟机实例的编号
    adminpass = Column(String(20))  #虚拟机admin的密码
    instance_ip = Column(String(15)) #NOVA分配的IP地址
    status = Column(Integer)        #系统状态 0-刚初始化 1-提交创建申请 2－正常运行 3-等待操作 4-状态异常
    disabled = Column(Boolean)      #是否被禁用掉

    __table_args__ = (
        UniqueConstraint(user_id,product_key,server_id,),
        TABLEARGS
    )

    def __init__(self, user, orderproduct):
        """
        初始化用户虚拟机实例
        @user: 用户登陆对象
        @product: 产品对象
        @image_id: 操作系统实例对象
        """
        self.user_id = user.id
        self.order_product_id = orderproduct.id
        self.instance_name = u"未命名主机"
        self.product_key = orderproduct.product_key
        self.image_id = ""
        self.status = 0
        self.disabled = False


class SysImage(Base):
    """
    操作系统镜像
    """
    image_key = Column(String(36))         #操作系统镜像编号
    image_name = Column(String(50))        #操作系统名称
    disabled = Column(Boolean)             #是否禁用

    __table_args__ = (
        UniqueConstraint(image_key,),
        TABLEARGS
    ) 

    def __init__(self, key):
        """
        初始化操作系统镜像
        @key: 镜像在系统内的编号
        """
        self.image_key = key
        self.disabled = False

class Tenant(Base):
    id = Column(String(32),primary_key=True)
    name = Column(String(50))
    admin_user_id =Column(String(32))
    used = Column(Boolean)
    __table_args__ = TABLEARGS
    def __init__(self, id, name, user_id):
        """
        初始化操作系统镜像
        @key: 镜像在系统内的编号
        """
        self.id = id
        self.name = name
        self.admin_user_id = user_id
        self.used = False


class Manager(Base):
    """
    管理员
    """
    email = Column(String(50))               #登陆邮箱地址（也是流程流转的邮箱）
    password = Column(String(46))            #登陆密码
    disabled = Column(Boolean)               #是否禁用

    __table_args__ = (
        UniqueConstraint(email,),
        TABLEARGS
    ) 
 
    def __init__(self, email, password):
        """
        初始化管理员对象
        @email: 登陆邮箱
        @password: 登陆密码
        """
        self.email = email
        self.password = utils.hash_passwd(password)
        self.disabled = False


class Group(Base):
    """
    管理员组
    """
    name =Column(String(20))                 #组名称

    __table_args__ = (
        UniqueConstraint(name,),
        TABLEARGS
    ) 

    def __init__(self, name):
        """
        初始化管理员组对象
        @name: 管理员组名称
        """
        self.name = name

class GroupManager(Base):
    """
    管理员组的管理员
    """
    manager_id = Column(Integer,ForeignKey("manager.id")) #关联管理员ID
    group_id = Column(Integer,ForeignKey("group.id")) #关联管理员组ID

    __table_args__ = TABLEARGS

    def __init__(self, manager, group):
        """
        初始化管理员组关系对象
        """
        self.manager_id = manager.id
        self.group_id = group.id

class Purview(Base):
    """
    权限定义
    """
    name = Column(String(50))                #权限名称

    __table_args__ = (
        UniqueConstraint(name,),
        TABLEARGS
    ) 

    def __init__(self, name):
        """
        初始化权限对象
        @name: 权限名称
        """
        self.name = name


class PurviewAccess(Base):
    """
    权限包含URL
    """
    purview_id = Column(Integer,ForeignKey("purview.id")) #关联权限ID
    access = Column(String(200))                          #权限包含的url
    __table_args__ = TABLEARGS

    def __init__(self, purview, url):
        """
        初始化权限包含url的对象
        @purview: 权限对象
        @url: 可以访问的url
        """
        self.purview_id = purview.id
        self.access = url


class GroupPurview(Base):
    """
    管理员组所有权限关系
    """
    purview_id = Column(Integer,ForeignKey("purview.id")) #关联权限ID
    group_id = Column(Integer,ForeignKey("group.id"))     #关联管理员组ID

    __table_args__ = TABLEARGS

    def __init__(self, purview, group):
        """
        初始化管理员组权限关系
        @purview: 权限对象
        @group: 管理员组对象
        """
        self.purview_id = purview.id
        self.group_id = group.id

class WorkSheet(Base):
    """
    工单定义
    """
    name = Column(String(50))                #工单名称
    disabled = Column(Boolean)               #是否禁用

    __table_args__ = (
        UniqueConstraint(name,),
        TABLEARGS
    ) 

    def __init__(self, name):
        """
        初始化工单对象
        @name: 工单名称
        """
        self.name = name
        self.disabled = False


class WorkSheetNode(Base):
    """
    工单节点定义
    """
    father_node_id =Column(Integer)          #父级结点编号
    name = Column(String(50))                #结点名称
    action = Column(String(200))             #操作连接
    disabled = Column(Boolean)               #是否有效

    __table_args__ = (
        UniqueConstraint(name,),
        TABLEARGS
    ) 

    def __init__(self, father_node, name, action):
        """
        工单结点定义对象
        @father_node: 父级结点对象
        @name: 结点名称
        @action: 操作URL
        """
        self.father_node_id = father_node.id
        self.name = name
        self.action = action
        self.disabled = False


def WorkSeetInstance(Base):
    """
    工单实例对象
    """
    user_id = Column(Integer,ForeignKey("userlogin.id"))    #关联用户编号
    worksheet_id = Column(Integer,ForeignKey("worksheet.id")) #关联工单编号
    worksheet = relationship('WorkSheet',uselist = False,remote_side=[WorkSheet.id]) #关联的工单对象
    current_node_id = Column(Integer,ForeignKey("worksheetnode.id"))
    current_node = relationship('WorkSheetNode',uselist = False,remote_side=[WorkSheetNode.id]) #关联的工单结点对象
    status = Column(Integer)                 #工单状态 0-刚初始化 1-处理过程中 2－处理完成

    __table_args__ = (
        UniqueConstraint(id,user_id,worksheet_id,current_node_id),
        TABLEARGS
    ) 

    def __init__(self, user, worksheet, node):
        """
        初始化工单实例对象
        @user: 发起工单用户
        @worksheet: 工单对象
        @node: 当前结点
        """
        self.user_id = user.id
        self.worksheet_id = worksheet.id
        self.current_node_id = node.id
        self.status = 0

class WorkSheetPurview(Base):
    """
    工单权限
    """
    node_id = Column(Integer,ForeignKey("worksheetnode.id")) #关联结点ID
    group_id = Column(Integer,ForeignKey("group.id")) #关联用户组ID

    __table_args__ = TABLEARGS

    def __init__(self, node, group):
        """
        初始化工单结点权限实例
        @node: 匹配的结点对象
        @group: 用户组对象
        """
        self.node_id = node.id
        self.group_id = group.id

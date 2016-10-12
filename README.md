# esl
esl

所有脚本直接使用python. py即可运行
需要搭起数据库mongodb，暂时不用但是不搭建会造成无法运行
MongoClient("127.0.0.1", 27017).test.syntax2，身份验证user: test, password: test
使用数据库solr，当前使用数据库，其构建方法和数据生成方式见script文件夹下的readme.txt

# 工程

python文件如下：
clean\_sentence用于结果显示
util, qtree, extree，comnex为早期版本
ftree为对comnex的加速版本
parse为结构化语法树生成与获取语法树字符串
ftree2为当前使用版本

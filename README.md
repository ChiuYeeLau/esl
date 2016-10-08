# esl
esl

所有脚本直接使用python. py即可运行
使用数据库为MongoClient("127.0.0.1", 27017).test.syntax2，身份验证user: test, password: test
newdb.py建立数据库（要求同一目录包含list.txt，其中包含parse过的txt列表）

# 工程

python文件如下：
clean\_sentence用于结果显示
util, qtree, extree已废弃
comnex为最后一个使用class Node的版本
ftree为加速版本
parse为结构化语法树生成与获取语法树字符串

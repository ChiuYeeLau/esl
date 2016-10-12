当前使用solr作为数据库
solr的建立方法：
解压solr文件进入文件夹
开启服务
bin/solr start
建立新的数据集
bin/solr create -c syntax
配置数据集
./initial1
（清空数据）
（./removeall）
运行ftree_gen.py以分析原始语法树处理结果，示例：
python ftree_gen.py solr index.txt
参数solr表示生成json的结果，为将要post到服务器的内容
参数index.txt表示索引文件，一行一个，内部可使用绝对路径或相对ftree_gen的路径
运行结束后会在ftree_gen同目录下生成文件夹totalsolr，内包含若干json文件
在solr文件夹下使用post
bin/post -c syntax <totalsolr>
<totalsolr>表示之前生成的文件夹，需要注意路径
solr配置完成

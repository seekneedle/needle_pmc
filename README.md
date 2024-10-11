## Introduction
本项目是基于haystack的向量知识库检索系统。提供以下功能：
1. 创建向量知识库：支持pdf,txt,docx文件上传，切分，embedding，存储到ES数据库。
2. 向量知识库上传/更新文件：上传文件到指定向量知识库(重复文件名覆盖)。
3. 查询向量知识库中的文件：返回某向量知识库下的所有文件名。
4. 查询所有向量知识库：返回目前所有的向量知识库id和名称。
5. 查询文件chunks:根据index_id和filename，返回该文件的chunks信息(chunkid & content)
6. 删除向量知识库
7. 删除向量知识库中的文件
8. 向量知识库检索:支持rerank，需要搭建xinference
9. RAG评估:支持的评估指标(faithfulness, answer_correctness, context_recall, context_precision, answer_relevancy, context_entity_recall, answer_similarity)

## Environment preparation
1. 安装xinference：xinference是一款开源模型推理平台，除了支持LLM，它还可以部署Embedding和ReRank模型。支持分布式部署。直接可提供支持openai api的接口。安装部署参考文档：https://inference.readthedocs.io/zh-cn/latest/getting_started/index.html。本项目中，用于提供ReRank模型。
2. 安装ES：本项目中使用ES作为向量数据库。
3. 安装mysql：保存index_id和index_name的映射关系。

## Build docker image and upload to harbor
```sh
sh upload.sh
```

## Local run
创建mysql表
```
建表语句：res/sql/mysql.sql
```
添加环境变量
```
linux：export needle_pwd="your_pwd"
IDE配置：Configuration->Enviroment->Environment variables中添加needle_pwd=your_pwd
```
修改配置文件res/prod/application.yml
```
username: basic_auth username
password: basic_auth password加密后的值。 加密代码使用：security/security.py sha256_encode函数
MYSQL_DB_PASSWORD：真实mysql password加密后的值，加密代码使用security/security.py encrypt函数
```

The app will be running on http://0.0.0.0:8471
```sh
python main.py
```
Run in background:
```sh
sh run.sh
```

Shutdown background:
```sh
sh shutdown.sh
```
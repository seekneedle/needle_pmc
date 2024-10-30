## Introduction
用户权限管理项目，支持用户、资源、权限的增删改查。

## Build docker image and upload to harbor
```sh
sh upload.sh
```

## Local run
添加环境变量
```
linux：export needlepmc_pwd="your_pwd"
IDE配置：Configuration->Enviroment->Environment variables中添加needlepmc_pwd=your_pwd
```
修改配置文件res/prod/application.yml
```
username: basic_auth username
password: basic_auth password加密后的值。 加密代码使用：security/security.py sha256_encode函数
```

The app will be running on http://0.0.0.0:8461
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
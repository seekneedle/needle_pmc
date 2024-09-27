## Build docker image and upload to harbor

```sh
sh upload.sh
```

## Local run

The app will be running on http://0.0.0.0:8471
```sh
python main.py
```
Run in background:
```sh
sh run.sh
```

## Analysis

Install pygraphviz
```sh
pygraphviz==1.13 # Only for analysis
```

Start analysis
```sh
sh analysis
```

Result will be saved to output folder

## Server deployment on k8s

deployment.yaml
```sh
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hcc-rag-deployment
  labels:
    app: hcc-rag
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hcc-rag
  template:
    metadata:
      labels:
        app: hcc-rag
    spec:
      containers:
      - name: hcc-rag-container
        image: harbor.homecredit.cn/ai/hcc-rag:latest
        imagePullPolicy: Always
        securityContext:
          privileged: true
        ports:
          - containerPort: 8471
```

service.yaml
```sh
apiVersion: v1
kind: Service
metadata:
  name: hcc-rag-service
  labels:
    app: hcc-rag
spec:
  selector:
    app: hcc-rag
  type: NodePort
  ports:
  - name: hcc-rag-port
    protocol: TCP
    port: 8471
    nodePort: 31817
    targetPort: 8471
```

Apply deployment and service
```sh
sudo kubectl apply -f deployment.yaml
sudo kubectl apply -f service.yaml
```

Server will be running on http://server_ip:31817

## Server update on k8s

Reload image and restart service
```sh
sudo kubectl rollout restart deployment/hcc-rag-deployment
```




# tips

本地pythoncharm 运行的话，需要 Python 3.10
run的config里面需要加一个 环境变量 
researchlab_pwd=S2LI(#@slF


postman 测试配置项
basicAuth 
hcc-rag/45355$%Dff
docker build -t needle:latest .
docker tag needle:latest **.**.cn/ai/needle:latest
docker login -u ai -p your_pwd **.**.cn
docker push **.**.cn/ai/needle:latest

docker build -t needle:latest .
docker tag needle:latest **.**.cn/ai/needle:latest
docker login -u ai -p 123456 **.**.cn
docker push **.**.cn/ai/needle:latest

docker build -t needle:latest .
docker tag needle:latest **.**.cn/ai/needle:latest
docker login -u ai -p Passw0rd! **.**.cn
docker push **.**.cn/ai/needle:latest

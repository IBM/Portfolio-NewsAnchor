echo '---------------------------------'
echo '=====>run Portfolio-NewsAnchor'
echo '---------------------------------'

echo '=====>Removing existing image if exists...'
docker stop portfolio-newsanchor
docker rm portfolio-newsanchor
sleep 2

echo '=====>docker build'
docker build --no-cache -t portfolio-newsanchor .

echo '=====>docker run'
docker run -d --restart always --name portfolio-newsanchor -p 8080:8080 portfolio-newsanchor

echo '---------------------------------'
echo '=====>Portfolio-NewsAnchor running on port 8080'
echo '---------------------------------'

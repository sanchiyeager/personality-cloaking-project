The dockerfile is present in the current directory 
Firstly start docker after installing 
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

docker build -t personality-cloak .


docker run -d -p 8501:8501 --name pcloak personality-cloak

Now we can access the website on the url http://localhost:8501

The requirements are to be specified in the Dockerfile

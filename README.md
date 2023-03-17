# QuickEC2
### A simple Flask application to quickly launch EC2 instances with minimal configuration.
#### - _*Development in progress*_
<img width="1433" alt="image" src="https://user-images.githubusercontent.com/30906750/224453101-9d4c3b47-a6a9-4e12-ad55-2cbd485c8718.png">


#### Docker
1. Setup 
- Mofiy `ENV KEYSTORE_PATH=<your_local_path>` in `Dockerfile.back` to a directory in your local computer. SSH keys will be stored in this directory.
- Add AWS credentials to `flask/credentials.json`:
```json
{
"access_key":"<access_key>",
"secret_key":"<secret_key>",
"region":"<region>"
}
```
2. Build 
- `docker build -t quickec2_back . -f ./Dockerfile.back`
- `docker build -t quickec2_front . -f ./Dockerfile.front`
3. Run 
- `docker run -dit -p:5000:5000 -v <your_local_path>:/keystore quickec2_back`
- `docker run -dit -p:8080:80 quickec2_front`


Open `http://localhost:8080` in your browser.





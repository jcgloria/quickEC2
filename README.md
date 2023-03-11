# QuickEC2
### A simple Flask application to quickly launch EC2 instances with minimal configuration.
#### - _*Development in progress*_
## Installation
1. Back-end
- Open a new terminal
- Add AWS credentials to `credentials.json` in parent directory:
```json
{
    "access_key":"<access_key>",
    "secret_key":"<secret_key>",
    "region":"<region>"
}
```
- `python3 -m venv .venv`
- `source .venv/bin/activate`
- `python3 -m pip install -r requirements.txt`
- `flask --app app run`
2. Front-End
- Open a new terminal
- `cd ec2webapp`
- `npm run build`
- `npm run start`





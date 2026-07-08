<!-- in order to test phone and pc project in local server make django run in your ip , and use ip as target adress in your front end . 0.0.0.0:8001 in django and use computer ip to catch it . in your phon euse the compter ip tonaccess the fron  -->


in order to host both front and back  with engrok you must add this in the back 
<!-- # 3. Allow JWT and ngrok headers
from corsheaders.defaults import default_headers
CORS_ALLOW_HEADERS = list(default_headers) + [
    "authorization",
    "ngrok-skip-browser-warning" ,
]

# CORS_ALLOW_ALL_ORIGINS = True
# the hosts the host where to make request to here, thats your frontend host 
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000', #local 
    "https://1b69-102-89-76-171.ngrok-free.app", # ngrok
]

CSRF_TRUSTED_ORIGINS = [
    "https://1b69-102-89-76-171.ngrok-free.app", # ngrok 
    "https://19a1-102-89-76-171.ngrok-free.app", # ngrok 
]
ALLOWED_HOSTS = ["*"]
# The host allowed to host Django Back no need of https:// here 
# ALLOWED_HOSTS = ["19a1-102-89-76-171.ngrok-free.app",'127.0.0.1']  # ngrok and local -->



and in the front inside the fetch 
<!-- your option should be sth like this let options = {
            signal: Aborter.signal,
            method: method,
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
                "ngrok-skip-browser-warning": "true"
            }
        } -->
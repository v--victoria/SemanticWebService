from utils2 import *
    
def UserProcessor(request):
    cookies = request.COOKIES
    isAuth = False
    lang = "en"
    user = "anonymous"
    ws = "not defined"
    
    if "USER" in cookies:
        user = get_short_uri(cookies["USER"])
        #TODO: check USER isAuth
        isAuth = True#TODO: replace with real value
    if "LANG" in cookies:
        lang = cookies["LANG"]
    if "WS" in cookies:
        ws = get_short_uri(cookies["WS"])
    return {'user': user, 'isAuth': isAuth, 'lang' : lang, 'ws': ws}

def SectionsProcessor(request):
    f = get_factory()
    lang = get_cookie_value(request.COOKIES, "LANG")
    roots = get_section_roots(f, lang)
    #temp = temp + None
    return {'roots': roots}

response.logo = A(B('Project_Chaperon'),XML('&nbsp;'),
                  _class="navbar-brand",_href="http://127.0.0.1:8000/login/default/start",
                  _id="web2py-logo")
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = myconf.get('app.author')
response.meta.description = myconf.get('app.description')
response.meta.keywords = myconf.get('app.keywords')
response.meta.generator = myconf.get('app.generator')

## your http://google.com/analytics id
response.google_analytics_id = None



response.menu = []

if auth.is_logged_in():
    response.menu.append(('Home', False, URL(request.application,'default','index'))),
    response.menu.append(('Search Projects', False, URL(request.application,'default','search2')))

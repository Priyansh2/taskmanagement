def index():
    if auth.is_logged_in():
        response.flash = T("WELCOME TO TASK MANAGEMENT APP")
        redirect(URL('default','home'))
    else:
        redirect(URL('default','start'))

def deletetask():
    vars=request.vars 
    db(db.checklist.id ==  vars.commid).delete()
    return "deleted"

def delete_pro():
    pid=request.args(0)
    db(db.project.id ==  pid).delete()
    redirect(URL('home'))
    return locals()

def start():
    
    print request.post_vars
    is_clicked = False
    if request.post_vars["remember_me"]:
        is_clicked = True
    
    fregister=auth.register()
    flogin=auth.login()
    flpswd=auth.request_reset_password()
    return locals()

def home():
    if auth.is_logged_in():
        pform=SQLFORM(db.project).process()
        accessible={}
        for i in range(1,100):
            accessible[i]=0
        allmembers = db(db.member.uid==auth.user.id).select(db.member.ALL)
        print allmembers
        for mem in allmembers:
                accessible[mem.pid]=1
        print accessible
        
        pform.element('textarea[name=description]')['_style']='height:5em'
        if pform.accepted:
            take=3
            rows = db().select(db.project.ALL,orderby=db.project.created_on)
            for latest in rows:
                take=latest.id
            db.member.insert(uid=auth.user.id,pid=take)
            redirect(URL('home'))
        if len(request.args):
            page=int(request.args[0])
        else: 
            page=0
        items_per_page=20
        limitby=((page)*items_per_page,(page+1)*items_per_page+1)
        rows = db().select(db.project.ALL,limitby=limitby,orderby=~db.project.created_on)
        return dict(form=FORM(INPUT(_id='keyword',_name='keyword',_onkeyup="ajax('callback', ['keyword'], 'target');")),target_div=DIV(_id='target'),rows=rows,page=page,items_per_page=items_per_page,pform=pform,accessible=accessible)
    else:
        redirect(URL('default','start'))

def search2():
    return dict(form1=FORM(INPUT(_id='keyword1',_name='keyword1', _onkeyup="ajax('callback2', ['keyword1'], 'target1');")),target_div1=DIV(_id='target1'),form2=FORM(INPUT(_id='keyword2',_name='keyword2', _onkeyup="ajax('callback3', ['keyword2'], 'target2');")),target_div2=DIV(_id='target2'),form3=FORM(INPUT(_id='keyword3',_name='keyword3', _onkeyup="ajax('callbackcomb', ['keyword3'], 'target3');")),target_div3=DIV(_id='target3'))

def callback2():
    if not request.vars.keyword1: return ''
    query = db.project.name.startswith(request.vars.keyword1)
    projects = db(query).select(orderby=db.project.name)
    links = [A(p.name, _href=URL('main',args=p.id)) for p in projects]
    return UL(*links)

def callback3():
    if not request.vars.keyword2: return ''
    
    query1 = db.auth_user.first_name.startswith(request.vars.keyword2)
    query2 = db.auth_user.last_name.startswith(request.vars.keyword2)
    q2=db.auth_user.id==db.project.created_by
    projects = db(((query1)&(q2))|((query2)&(q2))).select(db.project.ALL,orderby=db.project.name)
    links = [A(p.name, _href=URL('main',args=p.id)) for p in projects]
    return UL(*links)

def callbackcomb():
    if not request.vars.keyword3: return ''
    query1 = db.project.name.contains(request.vars.keyword3)
    projects = db(query1).select(orderby=db.project.name)
    
    links = [A(p.name, _href=URL('main',args=p.id)) for p in projects]
   
    return UL(*links)

        
            
def create_project():
    db.task.created_by.readable=True
    db.task.created_on.readable=True
    form=SQLFORM(db.project).process()
    if form.accepted:
        redirect(URL('home'))
    return locals()

def main():
    db.task.pid.default=request.args(0)
    form=SQLFORM(db.task).process()
    form.element('input[name=title]')['_style']='width:20em'
    form.element('textarea[name=description]')['_style']='width:20em;height:5em'
    form.element('input[name=duedat]')['_style']='width:20em'
    if form.accepted:
        redirect(URL('main',args=request.args(0)))
    project=db.project(request.args(0,cast=int))
    store=db(db.auth_user.id>0).select()
    tasks=db((db.task.pid==project.id)).select(orderby=~db.task.created_on)
    subtasks=db((db.checklist.pid==project.id)).select(orderby=~db.checklist.created_on)
    return locals()

def add_member():
    vars=request.vars
    var1= vars.uid
    var2= vars.pid
    st="You have been assigned to project "
    st1="Click here to approve:-"
    url="http://127.0.0.1:8000/project1/default/approval?uid=" + var1 + "&pid=" + var2
    pname=vars.project_name
    fname=vars.sender_fname.capitalize()
    lname=vars.sender_lname.capitalize()
    sub=st+pname+" by "+fname+" "+lname +"\n" +st1 +url
    print sub
    current.send_mail(vars.emailto,"Project Chaperon Invitation",sub)
    return locals()

def approval():
    msg = ""
    return locals()

def add_approved():
    var1=request.args(0)
    var2=request.args(1)
    db.member.insert(uid=var1,pid=var2)
    redirect(URL('main',args=request.args(1)))
    return locals()

def asktocontri():
    pid=request.vars.pid
    uid=request.vars.uid
    projects=db(db.project.id==pid).select(db.project.ALL)
    project=projects.last()
    print "its=",project.name
    st=" has asked to join your project: "
    st1="Click here to grant permissions "
#   print "id=",currid
    url="http://127.0.0.1:8000/project1/default/grant_permission?uid=" + uid + "&pid=" + pid + "&name=" + auth.user.first_name.capitalize()
    pname=project.name
    curr=auth.user.first_name.capitalize()
    sub=" " + curr+st+pname+ "\n" + st1 + url
    print sub
    store=db(db.auth_user.id==project.created_by).select() # created_by gives id
    owner=store.first()
    current.send_mail(owner.email,"Project Chaperon Invitation",sub)
    return locals()

def task():
    db.task.pid.default=request.args(0)
    form=SQLFORM(db.task).process()
    if form.accepted:
        redirect(URL('main',args=request.args(0)))
    return locals()

def grant_permission():
    msg = ""
    return locals()

def checklist():
    db.checklist.pid.default=request.args(0)
    db.checklist.tid.default=request.args(1)
    form=SQLFORM(db.checklist).process()
    if form.accepted:
        redirect(URL('main',args=request.args(0)))
    return locals()

def changeitall():
    vars=request.vars 
    db(db.checklist.id ==  vars.commid).delete()
    return "deleted"

def done():
    vars=request.vars 
    complete=db.checklist(id =  vars.commid)
    if complete.status:
        complete.update_record(status=0)
    else:
        complete.update_record(status=1)
    return complete.status
     

def move():
    vars = request.vars
    move=db.checklist(id =  vars.it)
    move.update_record(tid=vars.to)
    return "done"




def callback():
    """an ajax callback that returns a <ul> of links to wiki pages"""
    query = db.project.name.contains(request.vars.keyword)
    pages = db(query).select(orderby=db.project.name)
    links = [A(p.name, _href=URL('main',args=p.id)) for p in pages]

    return UL(*links)






me=auth.user_id


def tm():
    query=(db.tm.assigned_to==me) | (db.tm.created_by==me)
    grid=SQLFORM.grid(query, orderby=~db.tm.modified_on,create=False,details=False,editable=False,deletable=lambda  row:(row.created_by==me))
    return locals()














def product():
    product=SQLFORM(db.product).process()
    if product.accepted:
        response.flash="Done"
    return dict(product=product)


def login():
    login=SQLFORM(db.auth_user)
    return dict(form=login)

def user():
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

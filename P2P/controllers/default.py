# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

def index():
    return locals()


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

def browse():
    rows = db(db.poem).select()
    return locals()

def poem():
    if not request.args(0): redirect(URL('browse'))
    poem = db.poem(request.args(0,cast=int))
    rows = db(db.newline.poem_id == poem.id).select()
    contributors = db().select(db.newline.author, groupby=db.newline.author)
    return locals()

@auth.requires_login()
def create():
    form = SQLFORM(db.poem).process()
    if form.accepted:
        if form.vars.permission == 'Private': db.permission.insert(user_id = auth.user , poem_id = form.vars.id)
        redirect(URL('browse'))
    return locals()

@auth.requires_login()
def edit():
    poem = db.poem(request.args(0,cast=int))
    form = SQLFORM(db.poem, record=poem, fields=['title','body']).process()
    if form.accepted: redirect(URL('browse'))
    forms = FORM('Username: ',
              INPUT(_name='username'),
              INPUT(_type='submit'))
    if forms.accepts(request,session):
        added = False
        for users in db(db.auth_user).select():
            if(users.username == forms.vars.username):
                for permission in db(db.permission).select():
                    if(permission.user_id == users.id and permission.poem_id == poem.id):
                        response.flash = 'Already Added'
                    else:
                        added = True
                if(added == True):
                    db.permission.insert(user_id = users.id , poem_id = poem.id)
                    response.flash = 'Added'
    return locals()

@auth.requires_login()
def add():
    if not request.args(0): redirect(URL('browse'))
    poem = db.poem(request.args(0,cast=int))
    form = SQLFORM(db.newline)
    form.vars.poem_id = poem.id
    form.process()
    if form.accepted: redirect(URL('poem', args=poem.id))
    return locals()

@auth.requires_login()
def profile():
    user = auth.user
    poem = db.poem
    return locals()

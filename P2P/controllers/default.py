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
    return dict(form=auth())

def browse():
    rows = db(db.poem).select()
    return locals()

def poem():
    # Redirect to poem browser if no argument for poem id
    if not request.args(0): redirect(URL('browse'))

    # Load poem using the URL argument as poem id
    poem = db.poem(request.args(0,cast=int))
    rows = db(db.newline.poem_id == poem.id).select()
    contributors = db(db.newline.poem_id == poem.id).select(db.newline.author, groupby=db.newline.author)

    return locals()

@auth.requires_login()
def create():
    form = SQLFORM(db.poem).process()
    if form.accepted:
        # Create a new insert into permission table if poem was created Private (give owner permission)
        if form.vars.permission == 'Private':
            db.permission.insert(user_id = auth.user, poem_id = form.vars.id)
        redirect(URL('browse'))
    return locals()

@auth.requires_login()
def edit():
    # Redirect to poem browser if no argument for poem id
    if not request.args(0): redirect(URL('browse'))

    # Load poem using the URL argument as poem id
    poem_id = request.args(0,cast=int)
    poem = db.poem(poem_id)

    # Redirect if current user is not owner of poem
    if poem.author != auth.user:
        session.flash = 'You are not the owner of this poem and cannot edit it'
        redirect(URL('poem',args=poem.id))

    # Create SQLFORM
    form = SQLFORM(db.poem, record=poem, fields=['title','body']).process()
    lines = db(db.newline.poem_id == poem_id).select()
    lines_form = []
    for line in lines:
        lines_form.append(SQLFORM(db.newline, record=line.id, showid=False, deletable=True, submit_button = 'Delete', fields=['line']).process())
    #
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
    # Redirect to poem browser if no argument for poem id
    if not request.args(0): redirect(URL('browse'))

    # Load poem using the URL argument as poem id
    poem = db.poem(request.args(0,cast=int))
    rows = db(db.newline.poem_id == poem.id).select()

    # Check if poem is private and if current user has proper permissions, redirect if no permission
    if poem.permission == 'Private':
        if not db(db.permission.poem_id == poem.id, db.permission.user_id == auth.user).select():
            session.flash = 'You do not have permission to add to this poem'
            redirect(URL('poem', args=poem.id))

    # Grab last word in the second to last line to rhyme by default (for ABAB rhyme scheme)
    rhyme_word = ''
    if poem.line_count == 2:
        rhyme_word = poem.body.splitlines()[0].split(' ')[-1]
    elif poem.line_count == 3:
        rhyme_word = poem.body.splitlines()[1].split(' ')[-1]
    else:
        rhyme_line = db(db.newline.poem_id == poem.id, db.newline.line_number == poem.line_count-1).select().first()
        rhyme_word = rhyme_line.line.split(' ')[-1]

    # Create SQLFORM for the user to add a single line as a String
    form = SQLFORM(db.newline, fields=['line', 'date_posted'])
    form.vars.poem_id = poem.id
    form.vars.line_number = poem.line_count

    form.process()
    if form.accepted:
        poem.update_record(line_count=line_count)
        redirect(URL('poem', args=poem.id))
    return locals()

@auth.requires_login()
def profile():
    user = auth.user
    poem = db.poem
    poems_owned = db(db.poem.author == user.id).select()
    poems_contributed = db(db.newline.author == user.id, db.poem.id == db.newline.poem_id).select(groupby=db.poem.id)
    return locals()

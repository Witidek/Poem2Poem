# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
import datetime

def index():
    return locals()

def user():
    return dict(form=auth())

def browse():
    rows = db(db.poem).select()
    return locals()

def search():
    rows = db(db.poem).select()
    searchKey = ""
    searchType = 'Poems'
    form = FORM('Search: ',
              INPUT(_name='search'),
              '    Search By:  ',
              INPUT(_type ='radio', _name = 'searchType', _value = 'Poems', _checked="checked"), '  Poems ',
              INPUT(_type ='radio', _name = 'searchType', _value = 'Authors'),'  Authors  ',
              INPUT(_type='submit'))
    if form.accepts(request,session):
        searchKey = form.vars.search
        searchType = form.vars.searchType

    return locals()

def poem():
    # Redirect to poem browser if no argument for poem id
    if not request.args(0): redirect(URL('browse'))

    # Load poem using the URL argument as poem id
    poem = db.poem(request.args(0,cast=int))

    # Displaying ABAB
    if poem.category == '16 line ABAB rhyme':
        abab = db(db.abab.poem_id == poem.id).select().first()
        lines = db(db.new_line.poem_id == poem.id).select(orderby=db.new_line.line_number)
        contributors = db(db.new_line.poem_id == poem.id).select(db.new_line.author, groupby=db.new_line.author)
    # Displaying Haiku
    elif poem.category == 'Haiku':
        haiku = db(db.haiku.poem_id == poem.id).select().first()
        words = db(db.new_word.poem_id == poem.id).select(orderby=db.new_word.word_number)
        contributors = db(db.new_word.poem_id == poem.id).select(db.new_word.author, groupby=db.new_word.author)

    return locals()

def count_syllables(str):
    import urllib
    import urllib2
    from gluon.contrib import simplejson

    # GET JSONP from RhymeBrain API and parse
    url = 'http://rhymebrain.com/talk'
    data = {}
    data['function'] = 'getWordInfo'
    data['word'] = str
    url_values = urllib.urlencode(data)
    full_url = url + '?' + url_values
    data = urllib2.urlopen(full_url)
    result = data.read()
    parsed_json = simplejson.loads(result)

    # Return number of syllables cast as int
    return int(parsed_json['syllables'])

@auth.requires_login()
def create():
    # Create SQLFORM from db.poem
    form = SQLFORM(db.poem).process()
    if form.accepted:
        # Do an insert if ABAB
        if form.vars.category == '16 line ABAB rhyme':
            db.abab.insert(poem_id = form.vars.id, line_count = 2)
        # Do an insert if Haiku
        elif form.vars.category == 'Haiku':
            word_count = len(str(form.vars.body).split(' '))
            syllable_count = count_syllables(str(form.vars.body))
            db.haiku.insert(poem_id = form.vars.id, word_count = word_count, syllable_count = syllable_count)

        # Create new mutex for this poem
        db.mutex.insert(poem_id = form.vars.id, editing = False, edit_timestamp = request.now)

        # Create a new insert into permission table if poem was created Private (give owner permission)
        if form.vars.permission == 'Private':
            db.permission.insert(user_id = auth.user, poem_id = form.vars.id)
        redirect(URL('poem', args=form.vars.id))

    return locals()

@auth.requires_login()
def edit():
    # Redirect to poem browser if no argument for poem id
    if not request.args(0): redirect(URL('browse'))

    # Load poem using the URL argument as poem id
    poem_id = request.args(0,cast=int)
    poem = db.poem(poem_id)

    # Redirect if current user is not owner of poem
    if poem.author != auth.user.id:
        session.flash = 'You are not the owner of this poem and cannot edit it'
        redirect(URL('poem',args=poem.id))

    # Create SQLFORM
    form = SQLFORM(db.poem, record=poem, fields=['title','body']).process()
    lines = db(db.new_line.poem_id == poem_id).select(orderby=db.new_line.line_number)
    lines_form = []
    for line in lines:
        delete_form = FORM('Line: ' + line.line, INPUT(_name="line_id", _type='hidden',value=line.id), INPUT(_type='submit')).process(onvalidation=delete_line, next=URL('edit', args=poem.id))
        delete_form.vars.line = line.line
        lines_form.append(delete_form)

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

def delete_line(form):
    print form.vars.line_id
    row = db(db.new_line.id == form.vars.line_id).select().first()
    row.update_record(line = '')

KEY = 'mykey'

@auth.requires_login()
def add_check():
    # Redirect to poem browser if no argument for poem id
    if not request.args(0): redirect(URL('browse'))
    poem_id = request.args(0,cast=int)
    poem = db.poem(poem_id)
    mutex = db(db.mutex.poem_id == poem_id).select().first()

    if request.vars.quit:
        mutex.update_record(editing = False)
    else:
        # Check if poem is private and if current user has proper permissions, redirect if no permission
        if poem.permission == 'Private':
            print 'private'
            print db(db.permission.poem_id == poem.id).select().first().user_id
            print auth.user.id
            if not db((db.permission.poem_id == poem.id) & (db.permission.user_id == auth.user_id)).select():
                session.flash = 'You do not have permission to add to this poem'
                redirect(URL('poem', args=poem.id))

        # Check and redirect if another user is currently trying to add a line for this poem
        if mutex.editing:
            edit_timestamp = mutex.edit_timestamp
            minutes_elapsed = (datetime.datetime.now() - edit_timestamp).total_seconds() / 60
            if minutes_elapsed < 0.2:
                session.flash = 'A user is currently adding a line!'
                redirect(URL('poem', args=poem_id))

        mutex.update_record(editing = True, edit_timestamp = request.now)
        redirect(URL('add', args=poem_id, hmac_key=KEY))
        print 'should not get here'

def unlocked_mutex():
    print 'trying to unlock...'
    if not request.args(0): redirect(URL('browse'))
    poem_id = request.args(0,cast=int)
    mutex = db(db.mutex.poem_id == poem_id).select().first()
    if request.vars.quit:
        mutex.update_record(editing = False)
        print 'unlocked mutex?'

@auth.requires_login()
def add():
    import urllib
    import urllib2
    from gluon.contrib import simplejson

    if not URL.verify(request, hmac_key=KEY): redirect(URL('browse'))
    # Redirect to poem browser if no argument for poem id
    if not request.args(0): redirect(URL('browse'))

    # Load poem using the URL argument as poem id
    poem = db.poem(request.args(0,cast=int))

    # Add form for ABAB
    if poem.category == '16 line ABAB rhyme':
        abab = db(db.abab.poem_id == poem.id).select().first()
        rows = db(db.new_line.poem_id == poem.id).select(orderby=db.new_line.line_number)

        # Grab last word in the second to last line to rhyme by default (for ABAB rhyme scheme)
        rhyme_word = ''
        if abab.line_count == 2:
            rhyme_word = poem.body.splitlines()[0].split(' ')[-1]
        elif abab.line_count == 3:
            rhyme_word = poem.body.splitlines()[1].split(' ')[-1]
        else:
            rhyme_line = db((db.new_line.poem_id == poem.id) & (db.new_line.line_number == abab.line_count-1)).select().first()
            rhyme_word = rhyme_line.line.split(' ')[-1]

        #Get use the rhymebrain API
        url = 'http://rhymebrain.com/talk'
        data = {}
        data['function'] = 'getRhymes'
        data['word'] = rhyme_word
        url_values = urllib.urlencode(data)
        full_url = url + '?' + url_values
        data = urllib2.urlopen(full_url)
        result = data.read()
        parsed_json = simplejson.loads(result)

        # Create SQLFORM for the user to add a single line as a String
        form = SQLFORM(db.new_line, fields=['line'])
        form.vars.poem_id = poem.id
        form.vars.line_number = abab.line_count + 1

        form.process()
        if form.accepted:
            abab.update_record(line_count = abab.line_count + 1)
            mutex = db(db.mutex.poem_id == poem.id).select().first()
            mutex.update_record(editing = False)
            redirect(URL('poem', args=poem.id))
    # Add form for Haiku
    elif poem.category == 'Haiku':
        haiku = db(db.haiku.poem_id == poem.id).select().first()
        words = db(db.new_word.poem_id == poem.id).select(orderby=db.new_word.word_number)
        form = SQLFORM(db.new_word, fields=['word'])
        form.vars.poem_id = poem.id
        form.vars.word_number = haiku.word_count + 1

        form.process()
        if form.accepted:
            syllable_count = count_syllables(form.vars.word)
            db.new_word(form.vars.id).update_record(syllables = syllable_count)
            haiku.update_record(word_count = haiku.word_count + 1, syllable_count = haiku.syllable_count + syllable_count)
            mutex = db(db.mutex.poem_id == poem.id).select().first()
            mutex.update_record(editing=False)
            redirect(URL('poem', args=poem.id))

    return locals()

@auth.requires_login()
def specialadd():
    import urllib
    import urllib2
    from gluon.contrib import simplejson

    # Redirect to poem browser if no argument for poem id
    if not request.args(0): redirect(URL('browse'))
    lineNumber = request.args(1,cast = int)
    # Load poem using the URL argument as poem id
    poem = db.poem(request.args(0,cast=int))
    rows = db(db.new_line.poem_id == poem.id).select(orderby=db.new_line.line_number)
    check = db((db.new_line.poem_id == poem.id) & (db.new_line.line_number == request.args(1))).select().first()
    if check:
        if not check.line == '':
            redirect(URL('browse'))
    # Check if poem is private and if current user has proper permissions, redirect if no permission
    if poem.permission == 'Private':
        print 'private'
        print db(db.permission.poem_id == poem.id).select().first().user_id
        print auth.user.id
        if not db((db.permission.poem_id == poem.id) & (db.permission.user_id == auth.user_id)).select():
            session.flash = 'You do not have permission to add to this poem'
            redirect(URL('poem', args=poem.id))

    # Grab last word in the second to last line to rhyme by default (for ABAB rhyme scheme)
    rhyme_word = ''
    rhyme_line = db((db.new_line.poem_id == poem.id) & (db.new_line.line_number == lineNumber+2)).select().first()
    test = False
    if lineNumber-1 == 2:
        rhyme_word = poem.body.splitlines()[0].split(' ')[-1]
    elif lineNumber-1 == 3:
        rhyme_word = poem.body.splitlines()[1].split(' ')[-1]
    elif rhyme_line:
        rhyme_word = rhyme_line.line.split(' ')[-1]
        test = True
    else:
        rhyme_line = db((db.new_line.poem_id == poem.id) & (db.new_line.line_number == lineNumber-2)).select().first()
        rhyme_word = rhyme_line.line.split(' ')[-1]


    #Get use the rhymebrain API
    url = 'http://rhymebrain.com/talk'
    data = {}
    data['function'] = 'getRhymes'
    data['word'] = rhyme_word
    url_values = urllib.urlencode(data)
    full_url = url + '?' + url_values
    try:
        data = urllib2.urlopen(full_url)
        result = data.read()
        parsed_json = simplejson.loads(result)
        pass
    except IOERROR:
        raise HTTP(404)
        pass

    # Create SQLFORM for the user to add a single line as a String
    form = FORM(INPUT(_name = "line"),
                INPUT(_type="submit",_value = "Add"))
    if form.accepts(request,session):
        response.flash = form.vars.line
        if rows:
                update = db((db.new_line.line == '') & (db.new_line.line_number == request.args(1))).select().first()
                update.update_record(line = form.vars.line)
                update.update_record(author = auth.user.id)
        redirect(URL('poem', args=poem.id))
    return locals()

@auth.requires_login()
def profile():
    user = auth.user
    poem = db.poem
    poems_owned = db(db.poem.author == user.id).select()
    poems_contributed = db((db.new_line.author == user.id) & (db.poem.id == db.new_line.poem_id)).select(groupby=db.poem.id)
    return locals()

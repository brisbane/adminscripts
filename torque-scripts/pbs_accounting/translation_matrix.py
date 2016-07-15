global csv
#A file in format 
#unix or adgroup,user,AD SN, AD initial, Supervisor
#or
#ad group,@unixgroup,-,-,Owner/Supervisor
csv='userstranslation.csv'
global trans_arrayu
trans_arrayu=None
global trans_arrayg
trans_arrayg=None
global user2group
user2group={}
def translate_group (group, user):
    global trans_arrayu, trans_arrayg, csv
    if not trans_arrayu :
        trans_arrayu={}
        trans_arrayg={}

      
        for l in open(csv,'r').readlines():
           tokens=l.split(',')
           destgroup=tokens[0].strip()
           src_user_or_group=tokens[1].strip()
           if src_user_or_group[0]=='@':
               trans_arrayg[src_user_or_group[1:] ] = destgroup
           else:
               trans_arrayu[src_user_or_group]=destgroup
    retgrp=group
    #Notw we can cope with a double transaltion in this order
    if user in trans_arrayu:
           retgrp=trans_arrayu[user]
    if retgrp in trans_arrayg:
            retgrp=trans_arrayg[retgrp]
    return retgrp
def set_user2group(user,group):
    global user2group
    if user not in user2group.keys():
         user2group[user]=group
    elif user2group[user] != group: 
         print 'WARNING user', user , ' group changes to :', group , ' from ', user2group[user]
    user2group[user]=group 
def print_user2group():
    global user2group
    print user2group


from re import M
from flask import Blueprint,request,jsonify,Flask
from firebase_admin import firestore
from flask_jwt_extended import create_access_token
import shortuuid
import time
import datetime
import json

db = firestore.client()
message_Ref = db.collection('message')

messageApi = Blueprint('messageApi',__name__)
#2022/06/09 15:07
#新增文章
@messageApi.route('/add',methods=['POST'])
def add():
    try:
        jsonData ={
            'id':shortuuid.uuid(),
            'message':request.json.get('message'),
            'name' : request.json.get('name'),
            'time' : datetime.datetime.now().strftime('%Y/%m/%d %H:%M')    
            
        }            
        name = jsonData['id']
        #document(這個是想要的欄位名稱若沒給則隨機產生，這
        # 邊則是設定成抓取json內的name)
        message_Ref.document(name).set(jsonData)
        return jsonify(jsonData),200
    except Exception as e:
        return f"An Error Occuered:{e}"
#取得所有文章       
@messageApi.route('/',methods=['GET'])
def read():
        try:
            all_message = [doc.to_dict() for doc in message_Ref.stream()]            
            return jsonify(all_message)
        except Exception as e:
            return f"An Error Occured:{e}"

#新增留言
@messageApi.route('/comment',methods=['POST','PUT'])
def addComment():
    checkKey = ['name','message','messageID']
    jsonDataList = (list((request.json).keys()))
    if(sorted(checkKey)!=sorted(jsonDataList)):
        return jsonify({"error":'格式錯誤'}),400
    else:    
        try:
            commentData ={
                'id':shortuuid.uuid(),
                'message':request.json.get('message',None),
                'name' : request.json.get('name',None),
                'time' : datetime.datetime.now().strftime('%Y/%m/%d %H:%M')                
            }        
            message_ID = request.json.get('messageID')                                         
            #因不知道如何在一個已經有的資料下內添加無該欄位資訊的資料，因此作法是將所有資料拉出來，然後再將資料塞入原始資料內，
            #在整個覆蓋。
            dbMessageStr = format((message_Ref.document(message_ID).get()).to_dict()).replace('\'',"\"")
            dbMessageJson = json.loads(dbMessageStr)
            if(dbMessageJson.__contains__('comment')):
                dbMessageJson['comment'].append(commentData)
            else:   
                commentArray = []
                commentArray.append(commentData)             
                dbMessageJson['comment'] = commentArray   
            message_Ref.document(message_ID).set(dbMessageJson,merge=True)
            return jsonify({"success":'留言成功'}),200
        except Exception as e:
            return f"An Error Occured:{e}"    
#編輯留言
@messageApi.route('/editComment',methods=['POST','PUT'])
def editComment():
    checkKey = ['name','message','messageID','commentID']
    jsonDataList = (list((request.json).keys()))
    if(sorted(checkKey)!=sorted(jsonDataList)):
        return jsonify({"error":'格式錯誤'}),400
    else:    
        try:
            message_ID = request.json.get('messageID')                                         
            comment_ID = request.json.get('commentID')
            #因不知道如何在一個已經有的資料下內添加無該欄位資訊的資料，因此作法是將所有資料拉出來，然後再將資料塞入原始資料內，
            #在整個覆蓋。
            if(not message_Ref.document(message_ID).get().exists):
                return jsonify({"error":'無該筆資料ID'}),400
            dbMessageStr = format((message_Ref.document(message_ID).get()).to_dict()).replace('\'',"\"")
            dbMessageJson = json.loads(dbMessageStr)
            dbcomment = dbMessageJson['comment']                           
            commentIndex = next((index for (index,d) in enumerate(dbcomment) if d['id']==comment_ID),None)
            if(commentIndex==None):
                return jsonify({"error":'無該筆留言ID'}),400                        
            editCommentData ={
                'id':shortuuid.uuid(),
                'message':request.json.get('message',None),
                'name' : request.json.get('name',None),
                'time' : datetime.datetime.now().strftime('%Y/%m/%d %H:%M')                
            }        
            if(dbcomment==None):
                return jsonify({"error":'該筆並無留言'}),400
            else:
                commentIndex = next((index for (index,d) in enumerate(dbcomment) if d['id']==comment_ID),None)          
                dbcomment[commentIndex]['message']  = editCommentData['message']
                dbcomment[commentIndex]['time']  = editCommentData['time']
                dbMessageJson['comment'] = dbcomment
                message_Ref.document(message_ID).set(dbMessageJson,merge=True)
                return jsonify({"success":'編輯成功'}),200                         
        except Exception as e:
            return f"An Error Occured:{e}"    

#編輯文章
@messageApi.route('/editArticle',methods=['POST','PUT'])
def editArticle():
    
    checkKey = ['message','messageID']
    jsonDataList = (list((request.json).keys()))
    if(sorted(checkKey)!=sorted(jsonDataList)):
        return jsonify({"error":'格式錯誤'}),400
    else:    
        try:
            message_ID = request.json.get('messageID')     
            message = request.json.get('message',None)                                         
            #因不知道如何在一個已經有的資料下內添加無該欄位資訊的資料，因此作法是將所有資料拉出來，然後再將資料塞入原始資料內，
            #在整個覆蓋。
            if(not message_Ref.document(message_ID).get().exists):
                return jsonify({"error":'無該筆資料ID'}),400
            dbMessageStr = format((message_Ref.document(message_ID).get()).to_dict()).replace('\'',"\"")
            dbMessageJson = json.loads(dbMessageStr)                                                                            
            dbMessageJson['message'] = message;
            if(message == '' or message== None):
                return jsonify({"error":'留言不能為空'}),400
            else:                
                message_Ref.document(message_ID).set(dbMessageJson,merge=True)
                return jsonify({"success":'編輯成功'}),200                         
        except Exception as e:
            return f"An Error Occured:{e}"   

#刪除文章
@messageApi.route('/deleteArticle',methods=['GET','DELETE'])
def deleteArticle():
    try:
        message_ID = request.args.get('id')
        dbMessage = message_Ref.document(message_ID)
        if(not dbMessage.get().exists):
            return jsonify({"error":"此訊息不存在"}),400                        
        else:
            dbMessage.delete()
            return jsonify({"success":'刪除成功'}),200               
    except Exception as e:
        return f"An Error Occured:{e}"            

#刪除留言
@messageApi.route('/deleteComment',methods=['POST','DELETE'])
def deleteComment():
    try:
        message_ID = request.json.get('messageID')
        comment_ID = request.json.get('commentID')
        dbMessage = message_Ref.document(message_ID)
        if(not message_Ref.document(message_ID).get().exists):
            return jsonify({"error":'無該筆文章ID'}),400                    
        else:
            dbMessageStr = format((message_Ref.document(message_ID).get()).to_dict()).replace('\'',"\"")
            dbMessageJson = json.loads(dbMessageStr)
            dbcomment = dbMessageJson['comment']                           
            commentIndex = next((index for (index,d) in enumerate(dbcomment) if d['id']==comment_ID),None)
            if(commentIndex==None):
                return jsonify({"error":'無該筆留言ID'}),400         
            else:            
                del dbMessageJson['comment'][commentIndex]; 
                print(dbMessageJson);
                message_Ref.document(message_ID).set(dbMessageJson,merge=True)                               
                return jsonify({"success":'刪除成功'}),200                         
    except Exception as e:
        return f"An Error Occured:{e}"               
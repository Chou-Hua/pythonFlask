from flask import Blueprint,request,jsonify,Flask
from firebase_admin import firestore
from flask_jwt_extended import create_access_token


db = firestore.client()
user_Ref = db.collection('user')

userAPI = Blueprint('userAPI',__name__)

@userAPI.route('/')
def testHeroku():
    return "<h1>TEST is Success</h1>"

@userAPI.route('/add',methods=['POST'])
#TODO 需加入檢測是否有傳入account or email
#否則會因為傳入非相關key而導致新增成功一筆髒資料
def create():
    try:
        account = request.json.get('account')
        email = request.json.get('email')    
        if(account==None or email==None):
            return jsonify({"error":'格式錯誤'}),400            
        getEmail = user_Ref.document(email).get()
        getAccount = user_Ref.document(account).get()
        if(not getAccount.exists):   
            user_Ref.document(account).set(request.json)
            return jsonify({"success":True}),200
        else:
            return jsonify({"error":'此帳號已被使用'}),400
        if(not getEmail.exists):
            user_Ref.document(email).set(request.json)
            return jsonify({"success":True}),200
        else:
            return jsonify({"error":'此信箱已被使用'}),400
    except Exception as e:
        return f"An Error Occuered:{e}"
    
@userAPI.route('/list')
def read():
    try:
        all_users = [doc.to_dict() for doc in user_Ref.stream()]
        return jsonify(all_users)
    except Exception as e:
        return f"An Error Occured:{e}"
    
@userAPI.route('/login',methods=['POST','GET'])
def login():
    try:
        if request.method =='POST':        
            account = request.json.get('account',None)
            password = request.json.get('password',None)
            if(not user_Ref.document(account).get().exists):
                return jsonify({"error":"帳號尚未申請過"}),400                        
            dbAccount = format((user_Ref.document(account).get()).to_dict()['account'])
            dbPassword = format((user_Ref.document(account).get()).to_dict()['password'])
            accountVerify = account==dbAccount and password==dbPassword        
            if(accountVerify):
                access_token = create_access_token(identity=account)
                return jsonify({
                    "success":True,
                    "access_token":access_token
                    }),200
            return jsonify({"error":"帳號或密碼錯誤"}),400                           
                
    except Exception as e:
        return f"An Error Occured:{e}"
    
@userAPI.route('/changePassword',methods=['POST','PUT'])
def changePassword():
    try:
        account = request.json.get('account',None)
        oldPassword = request.json.get('oldPassword',None)
        newPassword = request.json.get('newPassword',None)
        dbAccount = user_Ref.document(account)
        accountOldPassword = format((user_Ref.document(account).get()).to_dict()['password'])
        if(account=='admin'):
            return jsonify({"error":"無權限修改管理者密碼"}),400                                                         
        elif(oldPassword==accountOldPassword):
            if(oldPassword==newPassword):
                return jsonify({"error":'新舊密碼禁止一樣'}),400                
            # dbAccount.update(password)
            doc = {'password':newPassword}
            dbAccount.update(doc)
            return jsonify({"success":'密碼修改成功 請重新登入'}),200
        else:
            return jsonify({"error":'密碼錯誤'}),400               
    except Exception as e:
        return f"An Error Occured:{e}"
    
@userAPI.route('/delete',methods=['GET','DELETE'])   
def deleteUser():
    try:
        account = request.args.get('account')
        dbAccount = user_Ref.document(account)
        if(not dbAccount.get().exists):
            return jsonify({"error":"此帳號不存在"}),400                        
        else:
            dbAccount.delete()
            return jsonify({"success":'刪除成功'}),200
    except Exception as e:
        return f"An Error Occured:{e}"
        
            

from crypt import methods
import email
import imp
import uuid
from flask import Blueprint,request,jsonify,Flask
from firebase_admin import firestore
#from flask_jwt_extended import(JWTManager,jwt_required,create_access_token)


#jwt = JWTManager()
#app.config['JWT_SECRET_KEY'] = 'ji3g4jwtau4au42k7ul4g6'  
#jwt.init_app(app)

db = firestore.client()
user_Ref = db.collection('user')
print(user_Ref)



#Get Doc
'''
doc_ref = db.collection('user').document('admin')
docs = doc_ref.get()
print('姓名 => {}'.format(docs.to_dict()['account']))
print('年紀 => {}'.format(docs.to_dict()['email']))
print('工作 => {}'.format(docs.to_dict()['password']))

print('Done')
'''



userAPI = Blueprint('userAPI',__name__)

@userAPI.route('/add',methods=['POST'])
def create():
    try:
        account = request.json.get('account')
        getAccount = user_Ref.document(account).get()
        if(not getAccount.exists):   
            user_Ref.document(account).set(request.json)
            return jsonify({"success":True}),200
        else:
            return jsonify({"error":'account is repeat'}),500
    except Exception as e:
        return f"An Error Occuered:{e}"
    
@userAPI.route('/list')
def read():
    try:
        all_users = [doc.to_dict() for doc in user_Ref.stream()]
        print(all_users)
        return jsonify(all_users)
    except Exception as e:
        return f"An Error Occured:{e}"
    
@userAPI.route('/login',methods=['GET','POST'])
def login():
    try:
        if request.method =='POST':        
            account = request.json.get('account',None)
            password = request.json.get('password',None)
            if(not user_Ref.document(account).get().exists):
                return jsonify({"Fail":"帳號尚未申請過"}),500                        
            dbAccount = format((user_Ref.document(account).get()).to_dict()['account'])
            dbPassword = format((user_Ref.document(account).get()).to_dict()['password'])
            accountVerify = account==dbAccount and password==dbPassword        
            if(accountVerify):
                return jsonify({"success":"登入成功"}),200
            return jsonify({"Fail":"帳號或密碼錯誤"}),500                           
                
    except Exception as e:
        return f"An Error Occured:{e}"
    
@userAPI.route('/changePassword',methods=['POST','PUT'])
def changePassword():
    try:
        account = request.json.get('account',None)
        password = request.json.get('password',None)
        dbAccount = user_Ref.document(account)
        print('dbacount',dbAccount)
        if(not dbAccount.get().exists):
            return jsonify({"Fail":"帳號尚未申請過"}),500                        
        else:
            # dbAccount.update(password)
            doc = {'password':password}
            dbAccount.update(doc)
            return jsonify({"success":'密碼修改成功'}),200
    except Exception as e:
        return f"An Error Occured:{e}"
    
@userAPI.route('/delete',methods=['GET','DELETE'])   
def deleteUser():
    try:
        account = request.args.get('account')
        dbAccount = user_Ref.document(account)
        if(not dbAccount.get().exists):
            return jsonify({"Fail":"此帳號不存在"}),500                        
        else:
            dbAccount.delete()
            return jsonify({"success":'刪除成功'}),200
    except Exception as e:
        return f"An Error Occured:{e}"
        
            

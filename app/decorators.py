from functools import wraps
from flask import redirect, render_template, request, jsonify, current_app
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            return redirect("/login")
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return render_template("login.html", error="Token expirado")
        except jwt.InvalidTokenError:
            return render_template("login.html", error="Token invalido")
        
        return f(data, *args, **kwargs)
    
    return decorated
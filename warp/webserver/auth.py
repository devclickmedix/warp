from zope.interface import implements

from twisted.web.resource import IResource

from warp.common.avatar import Avatar, JWTSession
from warp.runtime import avatar_store, config
import jwt
from datetime import datetime, timedelta


class LoginBase(object):

    isLeaf = True

    def render(self, request):
        self.doIt(request)
        
        if request.session.avatar is not None and request.session.afterLogin is not None:
            url = request.session.afterLogin
            request.session.afterLogin = None
        else:
            url = "/%s" % "/".join(request.postpath)

        request.redirect(url)
        return "Redirecting..."


def defaultCheckPassword(avatar, password):
    return avatar.password == password.decode("utf-8")


class LoginHandler(LoginBase):
    implements(IResource)

    def doIt(self, request):
        if request.method != 'POST':
            return False

        [email] = request.args.get('email', [None])
        [password] = request.args.get('password', [None])

        if not (email and password):
            request.session.addFlashMessage("Login failed: Email or password not given",
                                            _domain="_warp:login")
            return False

        avatar = avatar_store.find(Avatar,
                                   Avatar.email == email.decode("utf-8")
                                   ).one()

        checker = config.get('checkPassword', defaultCheckPassword)
        
        if avatar is None or not checker(avatar, password):
            request.session.addFlashMessage("Login failed: Email or password incorrect",
                                            _domain="_warp:login")
            return False

        if config.get("jwt") and config["jwt"].get("session"):
            jwt_secret = config["jwt"].get("jwt_secret") or "jwt_secret"
            dt = datetime.utcnow() + timedelta(days=1)
            payload = {
                'avatar_id': avatar.id,
                'username': email,
                'exp': int(dt.strftime("%s"))
            }
            encoded = jwt.encode(payload, jwt_secret, algorithm='HS256')
            request.session = JWTSession(encoded)

            cookiename = b"_".join([b'TWISTED_SESSION'] + request.sitepath)
            request.addCookie(cookiename, request.session.uid, path=b'/')
        else:
            request.session.setAvatarID(avatar.id)
            request.avatar = request.session.avatar

        return True


class LogoutHandler(LoginBase):

    def doIt(self, request):
        request.session.setAvatarID(None)

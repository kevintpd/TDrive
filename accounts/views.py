from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from .models import User, RegisterInfo
# Create your views here.
from .serializers import UserSerializer, RegisterSerializer, UserSigninSerializer
from rest_framework.generics import ListCreateAPIView, CreateAPIView, GenericAPIView
import hashlib
from TDrive.settings import SECRET_KEY, DEFAULT_FROM_EMAIL
from django.utils import timezone
from django.core.mail import send_mail


class UserListView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer

class LoggedInUserDetailView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(id=user.id)
class UserSigninAPIView(GenericAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSigninSerializer

    def post(self, request, *args, **kwargs):
        # print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        data = {"username": user.username}

        return Response(
            data=data,
            status=status.HTTP_200_OK
        )

@api_view(['GET'])
def sendcode_view(request):
    """
    先查询是否已经发送了，并且依然有效
    """
    try:
        email = request.query_params['email']
    except:
        return Response({"msg":"no email"}, status=status.HTTP_400_BAD_REQUEST)

    usercode = RegisterInfo.objects.filter(email=email)
    if usercode.exists():
        send_time = usercode.values()[0].get('create_time')
        # 如果已经过期了，则删除原来的，再创建一个新的
        print(send_time)
        if (timezone.now() - send_time).seconds >= 30 * 60:
            usercode.delete()
            newcode = RegisterInfo.objects.create(email=email)
            text = ("Your TDrive Account Verification Code:" + hashlib.sha256(
                (str(newcode.email) + str(newcode.create_time) + SECRET_KEY).encode('utf-8')).hexdigest()[:6].upper()+"\nCaptcha is valid for 30 minutes")
            try:
                send_mail(
                    subject="Email Verification for TDrive",
                    html_message=text,
                    message=text,
                    recipient_list=[newcode.email],
                    from_email=DEFAULT_FROM_EMAIL,
                    fail_silently=False,

                )
            except:
                # TODO: Handle unable to send mail situation
                pass
            content = {"msg": "code have send again"}
            return Response(content, status=status.HTTP_200_OK)
        # 如果没过期，则提示失败，验证码依然有效
        else:
            content = {"msg": "code has been send"}
            return Response(content, status=status.HTTP_204_NO_CONTENT)
    else:
        newcode = RegisterInfo.objects.create(email=email)
        text = ("Your TDrive Account Verification Code:" + hashlib.sha256(
            (str(newcode.email) + str(newcode.create_time) + SECRET_KEY).encode('utf-8')).hexdigest()[:6].upper()+"\nCaptcha is valid for 30 minutes")
        try:
            send_mail(
                subject="Email Verification for TDrive",
                html_message=text,
                message=text,
                recipient_list=[newcode.email],
                from_email=DEFAULT_FROM_EMAIL,
                fail_silently=False,

            )
        except:
            # TODO: Handle unable to send mail situation
            pass
        content = {"msg": "code has been send"}
        return Response(content, status=status.HTTP_200_OK)
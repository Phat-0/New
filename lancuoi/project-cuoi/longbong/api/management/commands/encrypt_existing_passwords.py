import bcrypt
from api.models import NguoiDung  # Thay 'your_app' bằng tên app của bạn

def encrypt_existing_passwords():
    users = NguoiDung.objects.all()
    for user in users:
        # Kiểm tra nếu mật khẩu chưa được mã hóa (ví dụ: không bắt đầu bằng $2b$)
        if not user.matkhau.startswith('$2b$'):
            matkhau_bytes = user.matkhau.encode('utf-8')
            salt = bcrypt.gensalt()
            matkhau_hash = bcrypt.hashpw(matkhau_bytes, salt).decode('utf-8')
            user.matkhau = matkhau_hash
            user.save()
            print(f"Đã mã hóa mật khẩu cho {user.email}")

# Chạy script trong Django shell:
# python manage.py shell
# from encrypt_existing_passwords import encrypt_existing_passwords
# encrypt_existing_passwords()
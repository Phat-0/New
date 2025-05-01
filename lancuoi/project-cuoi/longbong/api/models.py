from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

# ----------------------------- #
#       USER CUSTOM MODEL       #
# ----------------------------- #


class NguoiDungManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email là bắt buộc')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('loainguoidung', 'QuanTriVien')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser phải có is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser phải có is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class NguoiDung(AbstractBaseUser, PermissionsMixin):
    LOAI_NGUOI_DUNG = [
        ('KhachHang', 'Khách Hàng'),
        ('QuanTriVien', 'Quản Trị Viên'),
    ]

    mand = models.AutoField(primary_key=True)
    hoten = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
  # Django yêu cầu trường này để lưu mật khẩu đã hash
    sdt = models.CharField(max_length=15, blank=True, null=True)
    loainguoidung = models.CharField(max_length=20, choices=LOAI_NGUOI_DUNG, default='KhachHang')
    ngaytao = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = NguoiDungManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['hoten']

    class Meta:
        db_table = "nguoidung"
        ordering = ['-ngaytao']

    def __str__(self):
        return self.hoten


# ----------------------------- #
#            PRODUCT            #
# ----------------------------- #

class SanPham(models.Model):
    masp = models.AutoField(primary_key=True)
    tensp = models.CharField(max_length=255)
    mota = models.TextField()
    gia = models.DecimalField(max_digits=10, decimal_places=3)
    soluongtonkho = models.IntegerField()
    hinhanh = models.ImageField(upload_to='sanpham/', null=True, blank=True)
    danhmuc = models.CharField(max_length=255, default='Chưa phân loại')
    ngaytao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sanpham"
        ordering = ['-ngaytao']

    def __str__(self):
        return self.tensp

    @property
    def in_stock(self):
        return (self.soluongtonkho or 0) > 0


# ----------------------------- #
#             CART              #
# ----------------------------- #

class GioHang(models.Model):
    magh = models.AutoField(primary_key=True)
    nguoidung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='giohangs')

    class Meta:
        db_table = 'giohang'

    def __str__(self):
        return f"Giỏ hàng của {self.nguoidung.hoten}"


class ChiTietGioHang(models.Model):
    id = models.AutoField(primary_key=True)
    giohang = models.ForeignKey(GioHang, on_delete=models.CASCADE, related_name="chitiet")
    sanpham = models.ForeignKey(SanPham, on_delete=models.CASCADE, related_name="chitiet_giohang")
    soluong = models.PositiveIntegerField()

    class Meta:
        db_table = "chitietgiohang"
        unique_together = ('giohang', 'sanpham')

    def __str__(self):
        return f"{self.soluong} x {self.sanpham.tensp} trong giỏ hàng {self.giohang.magh}"  
    @property
    def item_subtotal(self):
        return self.sanpham.gia * self.soluong


# ----------------------------- #
#            ORDER              #
# ----------------------------- #

class DonHang(models.Model):
    TRANG_THAI_CHOICES = [
        ('ChoXacNhan', 'Chờ Xác Nhận'),
        ('DangGiao', 'Đang Giao'),
        ('HoanThanh', 'Hoàn Thành'),
        ('DaHuy', 'Đã Hủy'),
    ]

    madh = models.AutoField(primary_key=True)
    nguoidung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name="donhangs")
    ngaydathang = models.DateTimeField(auto_now_add=True)
    tongtien = models.DecimalField(max_digits=10, decimal_places=3)
    trangthai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES, default='ChoXacNhan')

    class Meta:
        db_table = "donhang"
        ordering = ['-ngaydathang']

    def __str__(self):
        return f"Đơn hàng {self.madh} - {self.nguoidung.hoten}"


class ChiTietDonHang(models.Model):
    id = models.AutoField(primary_key=True)
    donhang = models.ForeignKey(DonHang, on_delete=models.CASCADE, related_name="chitiet")
    sanpham = models.ForeignKey(SanPham, on_delete=models.CASCADE, related_name="chitiet_donhang")
    soluong = models.PositiveIntegerField(default=1)
    gia = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    class Meta:
        db_table = "chitietdonhang"
        unique_together = ('donhang', 'sanpham')

    def __str__(self):
        return f"{self.soluong} x {self.sanpham.tensp} trong đơn hàng {self.donhang.madh}"

    @property
    def item_subtotal(self):
        if self.gia is not None and self.soluong is not None:
            return self.gia * self.soluong
        return 0


# ----------------------------- #
#         PAYMENT & REVIEW      #
# ----------------------------- #

class ThanhToan(models.Model):
    PHUONG_THUC_THANH_TOAN = [
        ('TienMat', 'Tiền Mặt'),
        ('ChuyenKhoan', 'Chuyển Khoản'),
        ('TheTinDung', 'Thẻ Tín Dụng'),
    ]
    TRANG_THAI_THANH_TOAN = [
        ('ChuaThanhToan', 'Chưa Thanh Toán'),
        ('DaThanhToan', 'Đã Thanh Toán'),
    ]

    matt = models.AutoField(primary_key=True)
    donhang = models.OneToOneField(DonHang, on_delete=models.CASCADE, related_name="thanhtoan")
    sotien = models.DecimalField(max_digits=10, decimal_places=3)
    phuongthucthanhtoan = models.CharField(max_length=20, choices=PHUONG_THUC_THANH_TOAN)
    trangthaithanhtoan = models.CharField(max_length=20, choices=TRANG_THAI_THANH_TOAN, default='ChuaThanhToan')
    ngaythanhtoan = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "thanhtoan"

    def __str__(self):
        return f"Thanh toán {self.matt} - Đơn hàng {self.donhang.madh}"


class DanhGia(models.Model):
    madg = models.AutoField(primary_key=True)
    nguoidung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name="danhgias")
    sanpham = models.ForeignKey(SanPham, on_delete=models.CASCADE, related_name="danhgias")
    sosao = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    binhluan = models.TextField(blank=True, null=True)
    ngaydanhgia = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "danhgia"
        ordering = ['-ngaydanhgia']

    def __str__(self):
        return f"{self.nguoidung.hoten} - {self.sanpham.tensp} ({self.sosao} sao)"

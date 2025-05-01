from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
# Tạm thời không đăng ký viewset người dùng ở đây
router.register(r'sanpham', SanPhamViewSet)
router.register(r'giohang', GioHangViewSet)
router.register(r'chitietgiohang', ChiTietGioHangViewSet)
router.register(r'donhang', DonHangViewSet)
router.register(r'chitietdonhang', ChiTietDonHangViewSet)
router.register(r'thanhtoan', ThanhToanViewSet)
router.register(r'danhgia', DanhGiaViewSet)
router.register(r'nguoidung', NguoiDungViewSet)

urlpatterns = [
    path('nguoidung/dangnhap/', DangNhapView.as_view(), name='dangnhap'),
    path('nguoidung/dangky/', DangKyView.as_view(), name='dangky'),
    path('', include(router.urls)),  # Đặt router cuối cùng
]

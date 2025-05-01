from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    
    NguoiDung, SanPham, GioHang, ChiTietGioHang,
    DonHang, ChiTietDonHang, ThanhToan, DanhGia
)

# Quản lý NguoiDung
@admin.register(NguoiDung)
class NguoiDungAdmin(UserAdmin):
    model = NguoiDung
    list_display = ('mand', 'hoten', 'email', 'sdt', 'loainguoidung', 'is_staff', 'is_active')
    list_filter = ('loainguoidung', 'is_staff', 'is_active')
    search_fields = ('hoten', 'email', 'sdt')
    ordering = ('mand',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Thông tin cá nhân', {'fields': ('hoten', 'sdt', 'loainguoidung')}),
        ('Phân quyền', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Lịch sử', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'hoten', 'sdt', 'loainguoidung', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

# Quản lý SanPham
@admin.register(SanPham)
class SanPhamAdmin(admin.ModelAdmin):
    list_display = ('masp', 'tensp', 'gia', 'soluongtonkho', 'danhmuc', 'in_stock', 'ngaytao')
    list_filter = ('danhmuc',)
    search_fields = ('tensp',)
    readonly_fields = ('in_stock',)

# Quản lý Giỏ hàng
@admin.register(GioHang)
class GioHangAdmin(admin.ModelAdmin):
    list_display = ('magh', 'nguoidung')

# Quản lý Chi tiết giỏ hàng
@admin.register(ChiTietGioHang)
class ChiTietGioHangAdmin(admin.ModelAdmin):
    list_display = ('id', 'giohang', 'sanpham', 'soluong', 'item_subtotal')
    readonly_fields = ('item_subtotal',)

# Quản lý Đơn hàng
@admin.register(DonHang)
class DonHangAdmin(admin.ModelAdmin):
    list_display = ('madh', 'nguoidung', 'ngaydathang', 'tongtien', 'trangthai')
    list_filter = ('trangthai',)
    search_fields = ('madh', 'nguoidung__hoten')

# Quản lý Chi tiết đơn hàng
@admin.register(ChiTietDonHang)
class ChiTietDonHangAdmin(admin.ModelAdmin):
    list_display = ('id', 'donhang', 'sanpham', 'soluong', 'gia', 'item_subtotal')
    readonly_fields = ('item_subtotal',)

# Quản lý Thanh toán
@admin.register(ThanhToan)
class ThanhToanAdmin(admin.ModelAdmin):
    list_display = ('matt', 'donhang', 'sotien', 'phuongthucthanhtoan', 'trangthaithanhtoan', 'ngaythanhtoan')
    list_filter = ('phuongthucthanhtoan', 'trangthaithanhtoan')

# Quản lý Đánh giá
@admin.register(DanhGia)
class DanhGiaAdmin(admin.ModelAdmin):
    list_display = ('madg', 'nguoidung', 'sanpham', 'sosao', 'ngaydanhgia')
    list_filter = ('sosao',)
    search_fields = ('nguoidung__hoten', 'sanpham__tensp')

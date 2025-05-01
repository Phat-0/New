from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password

# Serializer cho người dùng
class NguoiDungSerializer(serializers.ModelSerializer):
    class Meta:
        model = NguoiDung
        fields = '__all__'

    def create(self, validated_data):
        # Băm mật khẩu trước khi lưu
        if 'matkhau' in validated_data:
            validated_data['matkhau'] = make_password(validated_data['matkhau'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Băm mật khẩu nếu được cập nhật
        if 'matkhau' in validated_data:
            validated_data['matkhau'] = make_password(validated_data['matkhau'])
        return super().update(instance, validated_data)

# Serializer cho đăng ký
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = NguoiDung
        fields = ['hoten', 'email', 'matkhau', 'sdt', 'loainguoidung']

    def create(self, validated_data):
        validated_data['matkhau'] = make_password(validated_data['matkhau'])
        return super().create(validated_data)

# Serializer cho sản phẩm

class SanPhamSerializer(serializers.ModelSerializer):
    class Meta:
        model = SanPham
        fields = ['masp', 'tensp', 'mota', 'gia', 'soluongtonkho', 'danhmuc', 'hinhanh', 'ngaytao']

# Serializer cho giỏ hàng
class GioHangSerializer(serializers.ModelSerializer):
    class Meta:
        model = GioHang
        fields = '__all__'

class ChiTietGioHangSerializer(serializers.ModelSerializer):
    sanpham = SanPhamSerializer(read_only=True)
    sanpham_id = serializers.PrimaryKeyRelatedField(
        queryset=SanPham.objects.all(), source='sanpham', write_only=True
    )
    gia = serializers.SerializerMethodField()  # Sử dụng SerializerMethodField để tính gia

    class Meta:
        model = ChiTietGioHang
        fields = ['id', 'giohang', 'sanpham', 'sanpham_id', 'soluong', 'gia']
        read_only_fields = ['giohang']

    def get_gia(self, obj):
        return obj.item_subtotal

# Serializer cho đơn hàng
class DonHangSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonHang
        fields = '__all__'

# Serializer cho chi tiết đơn hàng
class ChiTietDonHangSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChiTietDonHang
        fields = '__all__'

# Serializer cho thanh toán
class ThanhToanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThanhToan
        fields = '__all__'

# Serializer cho đánh giá
class DanhGiaSerializer(serializers.ModelSerializer):
    sanpham = SanPhamSerializer(read_only=True)  # lấy thông tin sản phẩm chi tiết
    class Meta:
        model = DanhGia
        fields = '__all__'

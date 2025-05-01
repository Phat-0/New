from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import *
from .serializers import *
from rest_framework.generics import CreateAPIView
from django.utils.text import slugify  # Để xử lý không dấu

# -----------------------------
# ViewSet cho người dùng
# -----------------------------
class NguoiDungViewSet(viewsets.ModelViewSet):
    queryset = NguoiDung.objects.all()
    serializer_class = NguoiDungSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -----------------------------
# ViewSet cho sản phẩm
# -----------------------------
class SanPhamViewSet(viewsets.ModelViewSet):
    queryset = SanPham.objects.all()
    serializer_class = SanPhamSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Lọc theo ID
        sanpham_id = self.request.query_params.get('id', None)
        if sanpham_id is not None:
            try:
                sanpham_id = int(sanpham_id)
                queryset = queryset.filter(masp=sanpham_id)
                if not queryset.exists():
                    return SanPham.objects.none()
            except ValueError:
                return SanPham.objects.none()

        # Tìm kiếm theo từ khóa
        search_query = self.request.query_params.get('search', None)
        if search_query:
            search_query_no_diacritics = slugify(search_query).replace('-', ' ')
            queryset = queryset.filter(
                Q(tensp__icontains=search_query) |
                Q(mota__icontains=search_query) |
                Q(tensp__icontains=search_query_no_diacritics) |
                Q(mota__icontains=search_query_no_diacritics)
            )

        return queryset

    def partial_update(self, request, *args, **kwargs):
        sanpham_id = request.query_params.get('id', None)
        if not sanpham_id:
            return Response({"detail": "Thiếu id trên query param"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            instance = SanPham.objects.get(masp=sanpham_id)
        except SanPham.DoesNotExist:
            return Response({"detail": "Không tìm thấy sản phẩm."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
# -----------------------------
# Các ViewSet khác
# -----------------------------
class GioHangViewSet(viewsets.ModelViewSet):
    queryset = GioHang.objects.all()
    serializer_class = GioHangSerializer
    permission_classes = [AllowAny] 

class ChiTietGioHangViewSet(viewsets.ModelViewSet):
    queryset = ChiTietGioHang.objects.all()
    serializer_class = ChiTietGioHangSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.request.query_params.get('giohang__nguoidung')
        if user_id:
            return ChiTietGioHang.objects.filter(giohang__nguoidung__mand=user_id)
        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        try:
            nguoidung_id = request.data.get("nguoidung")
            sanpham_id = request.data.get("sanpham")
            soluong = request.data.get("soluong", 1)

            if not nguoidung_id or not sanpham_id:
                return Response({"message": "Thiếu thông tin người dùng hoặc sản phẩm"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                soluong = int(soluong)
                if soluong <= 0:
                    return Response({"message": "Số lượng phải lớn hơn 0"}, status=status.HTTP_400_BAD_REQUEST)
            except (ValueError, TypeError):
                return Response({"message": "Số lượng không hợp lệ"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                nguoidung = NguoiDung.objects.get(mand=nguoidung_id)
            except NguoiDung.DoesNotExist:
                return Response({"message": f"Người dùng với mand={nguoidung_id} không tồn tại"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                sanpham = SanPham.objects.get(masp=sanpham_id)
            except SanPham.DoesNotExist:
                return Response({"message": f"Sản phẩm với masp={sanpham_id} không tồn tại"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                giohang, created = GioHang.objects.get_or_create(nguoidung=nguoidung)
            except Exception as e:
                return Response({"message": f"Lỗi khi tạo giỏ hàng: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            try:
                chitiet, created = ChiTietGioHang.objects.get_or_create(
                    giohang=giohang,
                    sanpham=sanpham,
                    defaults={"soluong": soluong}
                )
                if not created:
                    chitiet.soluong += soluong
                    chitiet.save()
            except Exception as e:
                return Response({"message": f"Lỗi khi thêm chi tiết giỏ hàng: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            serializer = self.get_serializer(chitiet)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"message": f"Lỗi server: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DonHangViewSet(viewsets.ModelViewSet):
    queryset = DonHang.objects.all()
    serializer_class = DonHangSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        donhang = self.get_object()
        donhang.trangthai = 'DangGiao'
        donhang.save()
        return Response({'message': 'Đơn hàng đang được giao'}, status=status.HTTP_200_OK)

class ChiTietDonHangViewSet(viewsets.ModelViewSet):
    queryset = ChiTietDonHang.objects.all()
    serializer_class = ChiTietDonHangSerializer
    permission_classes = [permissions.IsAuthenticated]

class ThanhToanViewSet(viewsets.ModelViewSet):
    queryset = ThanhToan.objects.all()
    serializer_class = ThanhToanSerializer
    permission_classes = [permissions.IsAuthenticated]

class DanhGiaViewSet(viewsets.ModelViewSet):
    queryset = DanhGia.objects.all()
    serializer_class = DanhGiaSerializer
    permission_classes = [AllowAny]

# -----------------------------
# Đăng ký người dùng (plain text password)
# -----------------------------
class DangKyView(CreateAPIView):
    queryset = NguoiDung.objects.all()
    serializer_class = NguoiDungSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        data = request.data
        user = NguoiDung(
            hoten=data.get("hoten"),
            email=data.get("email"),
            sdt=data.get("sdt"),
            loainguoidung=data.get("loainguoidung")
        )
        user.set_password(data.get("matkhau"))  # BẢO MẬT mật khẩu
        user.save()
        return Response({"message": "Đăng ký thành công!"}, status=status.HTTP_201_CREATED)
# -----------------------------
# Đăng nhập người dùng (so sánh plain text)
# -----------------------------
class DangNhapView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        matkhau = request.data.get('matkhau')

        if not email or not matkhau:
            return Response({"message": "Thiếu email hoặc mật khẩu!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = NguoiDung.objects.get(email=email)
            if user.check_password(matkhau):  # ✅ Dùng check_password để so sánh đúng
                return Response({
                    "message": "Đăng nhập thành công!",
                    "mand": user.mand,
                    "hoten": user.hoten,
                    "email": user.email,
                    "loainguoidung": user.loainguoidung
                }, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Sai mật khẩu!"}, status=status.HTTP_401_UNAUTHORIZED)
        except NguoiDung.DoesNotExist:
            return Response({"message": "Email không tồn tại!"}, status=status.HTTP_404_NOT_FOUND)

package lab2;

import static org.junit.jupiter.api.Assertions.assertEquals;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.time.LocalDateTime;

public class LoginServiceTest {

    private LoginService loginService;

    @BeforeEach
    public void setUp() {
        // Khởi tạo lại hệ thống trước mỗi ca test để không bị trùng lặp dữ liệu
        loginService = new LoginService();
    }

    // --- NHÓM 1: Đăng nhập cơ bản ---
    @Test
    public void testLoginSuccess() {
        assertEquals("Đăng nhập thành công", loginService.login("daivuong123", "matkhau123"));
    }

    // --- NHÓM 2: Kiểm thử giá trị biên ---
    @Test
    public void testUsernameBelowBoundary() {
        // Tên đăng nhập 5 ký tự
        assertEquals("Lỗi: Tên đăng nhập phải từ 6 đến 20 ký tự", loginService.login("admin", "matkhau123"));
    }

    @Test
    public void testPasswordAboveBoundary() {
        // Mật khẩu 26 ký tự
        String longPass = "abcdefghijklmnopqrstuvwxyz"; 
        assertEquals("Lỗi: Mật khẩu phải từ 6 đến 25 ký tự", loginService.login("daivuong123", longPass));
    }

    // --- NHÓM 3: Kiểm thử luồng sai mật khẩu và KHÓA TÀI KHOẢN ---
    @Test
    public void testWrongPasswordNotLockedYet() {
        // Sai dưới 5 lần
        assertEquals("Sai thông tin đăng nhập", loginService.login("daivuong123", "saipass1"));
    }

    @Test
    public void testLockAccountOnSixthFail() {
        // Giả lập đã sai 5 lần trước đó
        loginService.setFailCountForTest(5);
        
        // Lần thứ 6 sẽ kích hoạt khóa
        String response = loginService.login("daivuong123", "saipass6");
        assertEquals("Tài khoản đã bị khóa do đăng nhập thất bại quá 5 lần. Bạn vui lòng đăng nhập lại sau 15 phút", response);
    }

    @Test
    public void testUnlockAfter15Minutes() {
        // Giả lập tài khoản đã bị khóa từ 16 phút trước
        loginService.setLockTimeForTest(LocalDateTime.now().minusMinutes(16));
        
        // Đăng nhập lại với thông tin đúng -> Sẽ thành công
        String response = loginService.login("daivuong123", "matkhau123");
        assertEquals("Đăng nhập thành công", response);
    }
}
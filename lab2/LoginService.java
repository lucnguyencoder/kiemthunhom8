package lab2;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;

public class LoginService {
    // Giả lập tài khoản đúng trong hệ thống
    private final String VALID_USER = "daivuong123";
    private final String VALID_PASS = "matkhau123";
    
    private int failCount = 0;
    private LocalDateTime lockTime = null;

    public String login(String username, String password) {
        // 1. Kiểm tra trạng thái khóa tài khoản trước
        if (lockTime != null) {
            long minutesPassed = ChronoUnit.MINUTES.between(lockTime, LocalDateTime.now());
            if (minutesPassed < 15) {
                return "Tài khoản đã bị khóa do đăng nhập thất bại quá 5 lần. Bạn vui lòng đăng nhập lại sau 15 phút";
            } else {
                // Đã qua 15 phút -> Mở khóa và reset bộ đếm
                lockTime = null;
                failCount = 0;
            }
        }

        // 2. Kiểm tra độ dài giá trị biên
        if (username == null || username.length() < 6 || username.length() > 20) {
            return "Lỗi: Tên đăng nhập phải từ 6 đến 20 ký tự";
        }
        if (password == null || password.length() < 6 || password.length() > 25) {
            return "Lỗi: Mật khẩu phải từ 6 đến 25 ký tự";
        }

        // 3. Kiểm tra logic đăng nhập
        if (username.equals(VALID_USER) && password.equals(VALID_PASS)) {
            failCount = 0; // Reset số lần sai nếu đăng nhập thành công
            return "Đăng nhập thành công";
        } else {
            failCount++;
            if (failCount > 5) {
                lockTime = LocalDateTime.now();
                return "Tài khoản đã bị khóa do đăng nhập thất bại quá 5 lần. Bạn vui lòng đăng nhập lại sau 15 phút";
            }
            return "Sai thông tin đăng nhập";
        }
    }

    // --- Các phương thức hỗ trợ cho việc viết Test ---
    public void setLockTimeForTest(LocalDateTime time) {
        this.lockTime = time;
    }

    public void setFailCountForTest(int count) {
        this.failCount = count;
    }
}
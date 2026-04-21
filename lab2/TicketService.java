package lab2;

public class TicketService {

    public String getTicketType(String timeStr) {
        // Kiểm tra rỗng
        if (timeStr == null || timeStr.trim().isEmpty()) {
            return "Lỗi định dạng";
        }

        try {
            // Tách giờ và phút
            String[] parts = timeStr.split(":");
            if (parts.length != 2) {
                return "Lỗi định dạng";
            }

            int hour = Integer.parseInt(parts[0]);
            int minute = Integer.parseInt(parts[1]);

            // Kiểm tra vùng thời gian không hợp lệ (Vùng 5 và Vùng 6)
            if (hour < 0 || hour > 23 || minute < 0 || minute > 59) {
                return "Thời gian không hợp lệ";
            }

            // Đổi tất cả ra phút để dễ so sánh (0 đến 1439 phút)
            int totalMinutes = hour * 60 + minute;

            // Vùng 1: 00:00 -> 09:29 (0 -> 569)
            // Vùng 3: 16:01 -> 19:30 (961 -> 1170)
            if ((totalMinutes >= 0 && totalMinutes <= 569) || 
                (totalMinutes >= 961 && totalMinutes <= 1170)) {
                return "Vé thường";
            } 
            // Các khoảng thời gian hợp lệ còn lại thuộc Vùng 2 và Vùng 4
            else {
                return "Vé tiết kiệm";
            }

        } catch (NumberFormatException e) {
            // Bắt lỗi nếu nhập chữ cái thay vì số
            return "Lỗi định dạng";
        }
    }
}
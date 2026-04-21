package lab2;

import static org.junit.jupiter.api.Assertions.assertEquals;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class TicketServiceTest {

    private TicketService ticketService;

    @BeforeEach
    public void setUp() {
        ticketService = new TicketService();
    }

    // --- NHÓM 1: KIỂM THỬ VÉ THƯỜNG ---
    @Test
    public void testTC01_VeThuong_BienDuoiVung1() {
        assertEquals("Vé thường", ticketService.getTicketType("00:00"));
    }

    @Test
    public void testTC02_VeThuong_BienTrenVung1() {
        assertEquals("Vé thường", ticketService.getTicketType("09:29"));
    }

    @Test
    public void testTC03_VeThuong_GiuaVung1() {
        assertEquals("Vé thường", ticketService.getTicketType("07:15"));
    }

    @Test
    public void testTC04_VeThuong_BienDuoiVung3() {
        assertEquals("Vé thường", ticketService.getTicketType("16:01"));
    }

    @Test
    public void testTC05_VeThuong_BienTrenVung3() {
        assertEquals("Vé thường", ticketService.getTicketType("19:30"));
    }

    @Test
    public void testTC06_VeThuong_GiuaVung3() {
        assertEquals("Vé thường", ticketService.getTicketType("17:45"));
    }

    // --- NHÓM 2: KIỂM THỬ VÉ TIẾT KIỆM ---
    @Test
    public void testTC07_VeTietKiem_BienDuoiVung2() {
        assertEquals("Vé tiết kiệm", ticketService.getTicketType("09:30"));
    }

    @Test
    public void testTC08_VeTietKiem_BienTrenVung2() {
        assertEquals("Vé tiết kiệm", ticketService.getTicketType("16:00"));
    }

    @Test
    public void testTC09_VeTietKiem_GiuaVung2() {
        assertEquals("Vé tiết kiệm", ticketService.getTicketType("12:00"));
    }

    @Test
    public void testTC10_VeTietKiem_BienDuoiVung4() {
        assertEquals("Vé tiết kiệm", ticketService.getTicketType("19:31"));
    }

    @Test
    public void testTC11_VeTietKiem_BienTrenVung4() {
        assertEquals("Vé tiết kiệm", ticketService.getTicketType("23:59"));
    }

    @Test
    public void testTC12_VeTietKiem_GiuaVung4() {
        assertEquals("Vé tiết kiệm", ticketService.getTicketType("21:30"));
    }

    // --- NHÓM 3: KIỂM THỬ DỮ LIỆU NGOẠI LỆ ---
    @Test
    public void testTC13_ThoiGianAm() {
        assertEquals("Thời gian không hợp lệ", ticketService.getTicketType("-01:30"));
    }

    @Test
    public void testTC14_ThoiGianVuotQua() {
        assertEquals("Thời gian không hợp lệ", ticketService.getTicketType("24:00"));
    }

    @Test
    public void testTC15_SaiDinhDang() {
        assertEquals("Lỗi định dạng", ticketService.getTicketType("abc"));
    }
}
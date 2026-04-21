package lab1;
import static org.junit.jupiter.api.Assertions.assertEquals;
import org.junit.jupiter.api.Test;

public class MathUtilsPathTest {

    MathUtils utils = new MathUtils();

    // Đường đi 1: Nhập vào mảng null
    @Test
    public void testNullArrayPath() {
        assertEquals(-1, utils.processNumbers(null));
    }

    // Đường đi 2: Nhập vào mảng rỗng (vượt qua kiểm tra null nhưng dính kiểm tra length == 0)
    @Test
    public void testEmptyArrayPath() {
        assertEquals(-1, utils.processNumbers(new int[]{}));
    }

    // Đường đi 3: Mảng chỉ có số chẵn (chỉ đi qua nhánh if trong vòng lặp)
    @Test
    public void testOnlyEvenNumbersPath() {
        // result = 4 + 6 = 10
        int[] input = {4, 6};
        assertEquals(10, utils.processNumbers(input));
    }

    // Đường đi 4: Mảng chỉ có số lẻ (chỉ đi qua nhánh else trong vòng lặp)
    @Test
    public void testOnlyOddNumbersPath() {
        // result = -1 - 5 = -6
        int[] input = {1, 5};
        assertEquals(-6, utils.processNumbers(input));
    }

    // Đường đi 5: Mảng kết hợp (đi qua cả hai nhánh rẽ trong vòng lặp)
    @Test
    public void testMixedNumbersPath() {
        // result = 2 - 3 + 4 = 3
        int[] input = {2, 3, 4};
        assertEquals(3, utils.processNumbers(input));
    }
}
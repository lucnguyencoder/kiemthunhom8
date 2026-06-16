// Mục tiêu: Đạt 100% Statement Coverage - Resolve #1
package lab1;
import static org.junit.jupiter.api.Assertions.assertEquals;
import org.junit.jupiter.api.Test;

public class MathUtilsStatementTest {

    MathUtils utils = new MathUtils();

    @Test
    public void testNullOrEmptyArray() {
        // Bao phủ dòng lệnh: if (arr == null ...) return -1;
        assertEquals(-1, utils.processNumbers(null));
    }

    @Test
    public void testMixedNumbers() {
        // Bao phủ vòng lặp, nhánh số chẵn (2) và nhánh số lẻ (3)
        // result = 2 (chẵn) - 3 (lẻ) = -1
        int[] input = {2, 3};
        assertEquals(-1, utils.processNumbers(input));
    }
}
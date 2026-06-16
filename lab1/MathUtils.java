package lab1;
public class MathUtils {
    /**
     * Tính tổng các số chẵn và trừ đi các số lẻ trong mảng.
     * Nếu mảng rỗng hoặc null, trả về -1.
     */
    public int processNumbers(int[] arr) {
        int result = 0;
        
        // Lệnh rẽ nhánh 1
        if (arr == null || arr.length == 0) { 
            return -1;
        }
        
        // Vòng lặp
        for (int i = 0; i < arr.length; i++) { 
            // Lệnh rẽ nhánh 2
            if (arr[i] % 2 == 0) { 
                result += arr[i];
            } else { 
                // Lệnh rẽ nhánh 3
                result -= arr[i];
            }
        }
        
        return result;
    }
}
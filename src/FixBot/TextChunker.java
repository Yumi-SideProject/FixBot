package FixBot; 
import java.util.ArrayList;
import java.util.List;

public class TextChunker {

    public static List<String> splitIntoChunks(String text, int chunkSize) {
        List<String> chunks = new ArrayList<>();
        int length = text.length();
        for (int i = 0; i < length; i += chunkSize) {
            chunks.add(text.substring(i, Math.min(length, i + chunkSize)));
        }
        return chunks;
    }
}

package FixBot; 
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.List;
import org.json.JSONObject;
import org.json.JSONArray;

public class LlamaSequentialProcessor {

    private static final String API_URL = "https://api.groq.com/openai/v1/chat/completions";
    private static final String API_KEY = "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";
    private static final String MODEL = "llama-3.3-70b-versatile";
    private static final String OUTPUT_FILE = "C:/Users/tyumi/Desktop/side_pjt/Samsung_generated_questions.txt"; 

    public static void main(String[] args) {
        String filePath = "C:/Users/tyumi/Desktop/side_pjt/Samsung_questions.txt";  

        try {
            // ✅ 파일 읽기
            String documentText = Files.readString(Paths.get(filePath), StandardCharsets.UTF_8);
            List<String> chunks = TextChunker.splitIntoChunks(documentText, 1000);

            // ✅ 순차적으로 LLM 호출
            for (String chunk : chunks) {
                try {
                    int sleepTime = 3000 + (int) (Math.random() * 2000);
                    Thread.sleep(sleepTime);  // ✅ Rate Limit 초과 방지

                    String prompt = generatePrompt(chunk);
                    String response = callLLMApi(API_URL, API_KEY, MODEL, prompt);

                    // ✅ 응답이 정상적인 경우 즉시 파일에 저장
                    if (response != null && !response.contains("응답에서 content 값을 찾을 수 없음")) {
                        saveResultToFile(response, OUTPUT_FILE);
                    } else {
                        System.out.println("❗ 유효한 LLM 응답 없음, 저장 안 함");
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    // ✅ 결과를 즉시 파일에 저장하는 함수 (줄 단위 추가)
    public static void saveResultToFile(String result, String filePath) {
        try {
            long lineCount = Files.exists(Paths.get(filePath)) ? Files.lines(Paths.get(filePath)).count() : 0;
            char index = (char) ('a' + (lineCount % 26));

            String formattedResult = index + ". " + result + System.lineSeparator();
            
            Files.write(Paths.get(filePath), formattedResult.getBytes(StandardCharsets.UTF_8), 
                        StandardOpenOption.CREATE, StandardOpenOption.APPEND);

            System.out.println("💾 저장 완료: " + formattedResult);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    // ✅ JSON 문자열 안전 변환 함수
    public static String escapeJsonString(String str) {
        return str.replace("\\", "\\\\")
                  .replace("\"", "\\\"")
                  .replace("\n", "\\n")
                  .replace("\r", "\\r")
                  .replaceAll("[✓☞→※\\[\\]]", "")
                  .replaceAll("\\s+", " ")
                  .trim();
    }
    
    // ✅ Few-shot Learning 적용 프롬프트 생성
    public static String generatePrompt(String text) {
        return "당신은 고객 지원을 위한 AI 어시스턴트입니다. "
            + "다음 문서를 기반으로 사용자가 할 가능성이 높은 질문 10개를 만들어 주세요. "
            + "질문은 실제 고객이 물어볼 법한 자연스러운 구어체로 작성해 주세요. "
            + "별도의 앞뒤 내용 없이 해당 내용만 출력. nutshell, for slack message, in korean. "
            + "\\n\\n예제: "
            + "\\n문서 내용: '세탁기 결빙 예방 방법을 확인하세요.' "
            + "\\n예상 질문: '겨울철 세탁기가 얼지 않게 하려면 어떻게 해야 하나요?' "
            + "\\n\\n문서 내용: '세제 자동 투입 기능이 있습니다.' "
            + "\\n예상 질문: '세제 자동 투입 기능은 어떻게 설정하나요?' "
            + "\\n\\n문서 내용: '스마트싱스 앱을 통해 기기를 등록할 수 있습니다.' "
            + "\\n예상 질문: '스마트싱스에 세탁기를 등록하려면 어떻게 해야 하나요?' "
            + "\\n\\n문서 내용: '" + escapeJsonString(text) + "' "
            + "\\n예상 질문:";
    }

    // ✅ Llama API 호출 함수 (JSON 안전 처리 추가)
    public static String callLLMApi(String apiUrl, String apiKey, String model, String prompt) {
        String safePrompt = escapeJsonString(prompt);
    
        String payload = """
                {
                  "model": "%s",
                  "messages": [
                    {
                      "role": "user",
                      "content": "%s"
                    }
                  ]
                }
                """.formatted(model, safePrompt);
    
        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(apiUrl))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + apiKey)
                .POST(HttpRequest.BodyPublishers.ofString(payload, StandardCharsets.UTF_8))
                .build();

        int backoffTime = 50000;
        int retryCount = 0;
        while (retryCount < 5) {
            try {
                HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
    
                if (response.statusCode() == 200) {
                    return extractContent(response.body());
                } else if (response.statusCode() == 429) {
                    System.out.println("❗ Rate limit 초과: " + (backoffTime / 1000) + "초 후 재시도");
                    Thread.sleep(backoffTime);
                    backoffTime *= 2;
                    retryCount++;
                } else {
                    return "LLM API 오류: " + response.statusCode();
                }
            } catch (Exception e) {
                e.printStackTrace();
                return "예외 발생: " + e.getMessage();
            }
        }
        return "LLM API 오류 (재시도 실패)";
    }

    // ✅ Llama API 응답에서 예상 질문 추출
    public static String extractContent(String json) {
        try {
            JSONObject jsonObj = new JSONObject(json);
            JSONArray choices = jsonObj.getJSONArray("choices");
    
            if (choices.length() > 0) {
                JSONObject firstChoice = choices.getJSONObject(0);
                JSONObject message = firstChoice.getJSONObject("message");
                return message.getString("content");
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return "응답에서 content 값을 찾을 수 없음";
    }    
}

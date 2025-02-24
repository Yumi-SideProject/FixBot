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
import java.util.Map;
import java.util.stream.Collectors;
import org.json.JSONObject;
import org.json.JSONArray;

public class LlamaSolutionExtractor {
    
    private static final String API_URL = "https://api.groq.com/openai/v1/chat/completions";
    private static final String API_KEY = "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";
    private static final String MODEL = "llama-3.3-70b-versatile";
    private static final String OUTPUT_FILE = "C:/Users/tyumi/Desktop/side_pjt/llm_filtered_sentences.json"; 

    public static void main(String[] args) {
        String[] filePaths = {"C:/Users/tyumi/Desktop/side_pjt/Samsung_sentences_1.json", "C:/Users/tyumi/Desktop/side_pjt/Samsung_sentences_2.json"};
        
        try {
            // ✅ JSON 파일 읽기
            String allText = readJsonFiles(filePaths);
            List<String> sentences = extractSentencesFromJson(allText);
            
            System.out.println("📌 원본 문장 개수: " + sentences.size());

            // ✅ Llama API 호출 (Batch 단위로 실행)
            List<String> filteredSentences = processWithLlama(sentences);
            System.out.println("✅ 필터링 후 문장 개수: " + filteredSentences.size());

            // ✅ JSON 파일로 저장
            saveFilteredSentencesToJson(filteredSentences, OUTPUT_FILE);
            System.out.println("✅ LLM 기반 해결 방안 JSON 저장 완료: " + OUTPUT_FILE);
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    // ✅ JSON 파일을 읽어 문장 리스트 추출
    public static String readJsonFiles(String[] filePaths) throws IOException {
        StringBuilder sb = new StringBuilder();
        for (String filePath : filePaths) {
            sb.append(Files.readString(Paths.get(filePath), StandardCharsets.UTF_8)).append("\n");
        }
        return sb.toString();
    }

    // ✅ JSON에서 문장 리스트 추출
    
    public static List<String> extractSentencesFromJson(String jsonData) {
        JSONArray jsonArray = new JSONArray(jsonData);
        return jsonArray.toList().stream()
                .map(obj -> (String) ((Map<String, Object>) obj).get("sentence")) // 안전한 캐스팅
                .collect(Collectors.toList());
    }
    

    // ✅ Llama API를 활용하여 해결 방안 필터링 수행
    public static List<String> processWithLlama(List<String> sentences) throws InterruptedException {
        int batchSize = 50;  // 한 번에 처리할 문장 수
        List<String> filteredSentences = new java.util.ArrayList<>();

        for (int i = 0; i < sentences.size(); i += batchSize) {
            int end = Math.min(i + batchSize, sentences.size());
            List<String> batch = sentences.subList(i, end);

            String prompt = generatePrompt(batch);
            String response = callLlamaApi(API_URL, API_KEY, MODEL, prompt);

            if (response != null && !response.contains("응답에서 content 값을 찾을 수 없음")) {
                System.out.println(parseLlamaResponse(response));
                filteredSentences.addAll(parseLlamaResponse(response));
            }

            // ✅ Rate Limit 방지 (랜덤 대기 시간 추가)
            Thread.sleep(3000 + (int) (Math.random() * 2000));
        }

        return filteredSentences;
    }

    // ✅ 프롬프트 생성
    public static String generatePrompt(List<String> sentences) {
        return "아래 문장이 제품의 **문제 해결 방법** 또는 **설정 가이드**인지 판별해 주세요.\n"
                + "- 해결 방법일 경우, 그대로 유지\n"
                + "- 해결 방법이 아니라면 제외\n"
                + "- 해결 방법이 여러 문장으로 이루어진 경우, 연결된 문장들을 함께 유지\n"
                + "- 단순한 제품 설명이나 기능 소개 문장은 제외\n"
                + "- 별도의 앞뒤 내용 없이 해당 내용만 출력. nutshell, for slack message, in korean.\n"
                + "\n문장 리스트:\n" + String.join("\n", sentences);
    }

    // ✅ Llama API 호출 함수
    public static String callLlamaApi(String apiUrl, String apiKey, String model, String prompt) {
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
                """.formatted(model, escapeJsonString(prompt));

        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(apiUrl))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + apiKey)
                .POST(HttpRequest.BodyPublishers.ofString(payload, StandardCharsets.UTF_8))
                .build();

        try {
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            return response.statusCode() == 200 ? response.body() : null;
        } catch (Exception e) {
            e.printStackTrace();
            return null;
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

    // ✅ Llama API 응답에서 해결 방안 문장 리스트 추출
    public static List<String> parseLlamaResponse(String responseJson) {
        List<String> sentences = new java.util.ArrayList<>();
        try {
            JSONObject jsonObj = new JSONObject(responseJson);
            JSONArray choices = jsonObj.getJSONArray("choices");

            if (choices.length() > 0) {
                JSONObject firstChoice = choices.getJSONObject(0);
                JSONObject message = firstChoice.getJSONObject("message");
                String content = message.getString("content");

                // 🔹 LLM 응답을 문장 단위로 분리
                for (String line : content.split("\n")) {
                    if (!line.isBlank()) {
                        sentences.add(line.trim());
                    }
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return sentences;
    }

    // ✅ 필터링된 문장을 JSON 파일로 저장
    public static void saveFilteredSentencesToJson(List<String> filteredSentences, String filePath) {
        JSONArray jsonArray = new JSONArray();
        for (String sentence : filteredSentences) {
            jsonArray.put(new JSONObject().put("sentence", sentence));
        }

        try {
            Files.write(Paths.get(filePath), jsonArray.toString(4).getBytes(StandardCharsets.UTF_8),
                    StandardOpenOption.CREATE, StandardOpenOption.TRUNCATE_EXISTING);
            System.out.println("✅ 필터링된 문장 저장 완료: " + filePath);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}

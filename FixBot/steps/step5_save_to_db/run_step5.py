from .video_qa_repository import fetch_matched_questions_with_all_data, save_to_video_qa

def run_step5():
    matched_data = fetch_matched_questions_with_all_data()

    for item in matched_data:
        save_to_video_qa(item)

    print(f"✅ All data saved to video_qa.")

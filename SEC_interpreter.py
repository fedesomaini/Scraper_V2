import pandas as pd
from transformers import pipeline

# Load your dataset from Excel (replace with your file path)
file_path = 'your_scraper_output.xlsx'  # Adjust file path

data = pd.read_excel(file_path)

# Initialize a summarization pipeline using a Hugging Face model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", max_length=130, min_length=30, do_sample=False)

# Extract relevant columns for processing
paragraphs = data["Paragraph"].dropna().tolist()

# Summarize all paragraphs to extract deals and terms
summarized_results = []

print("Summarizing all paragraphs to extract deal information...")
for paragraph in paragraphs:
    try:
        summary = summarizer(paragraph[:1024])[0]['summary_text']  # Summarize up to max token limit
        summarized_results.append((paragraph, summary))
    except Exception as e:
        print(f"Error processing paragraph: {e}")

# Create a DataFrame to store the results
summary_df = pd.DataFrame(summarized_results, columns=["Original Paragraph", "Summary"])

# Save output for review
output_file = "Deal_Summaries.xlsx"
summary_df.to_excel(output_file, index=False)

print(f"Summaries saved to {output_file}")
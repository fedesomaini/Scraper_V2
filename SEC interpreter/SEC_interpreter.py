import os
import pandas as pd
from transformers import pipeline

# Define paths relative to the code directory
base_dir = os.path.dirname(__file__)  # Current script location
input_file = os.path.join(base_dir, "2-5-2025_EdgarInfo.xlsx")
output_dir = os.path.join(base_dir, "SEC_interpreter_outputs")
output_file = os.path.join(output_dir, "Deal_Summaries.xlsx")

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load the dataset
data = pd.read_excel(input_file)

# Initialize summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", max_length=130, min_length=30, do_sample=False)

# Extract paragraphs
paragraphs = data["Paragraph"].dropna().tolist()

# Summarize all paragraphs to extract deals and terms
summarized_results = []

print("Summarizing all paragraphs to extract deal information...")
for paragraph in paragraphs:
    try:
        # Summarize paragraph (ensure max token limit for BART)
        summary = summarizer(paragraph[:1024])[0]['summary_text']
        summarized_results.append((paragraph, summary))
    except Exception as e:
        print(f"Error processing paragraph: {e}")

# Create a DataFrame to store the results
summary_df = pd.DataFrame(summarized_results, columns=["Original Paragraph", "Summary"])

# Save the output for review
summary_df.to_excel(output_file, index=False)

print(f"Summaries saved to: {output_file}")



# import pandas as pd
# from transformers import pipeline

# # Load your dataset from Excel (replace with your file path)
# file_path = 'your_scraper_output.xlsx'  # Adjust file path

# data = pd.read_excel(file_path)

# # Initialize a summarization pipeline using a Hugging Face model
# summarizer = pipeline("summarization", model="facebook/bart-large-cnn", max_length=130, min_length=30, do_sample=False)

# # Extract relevant columns for processing
# paragraphs = data["Paragraph"].dropna().tolist()

# # Summarize all paragraphs to extract deals and terms
# summarized_results = []

# print("Summarizing all paragraphs to extract deal information...")
# for paragraph in paragraphs:
#     try:
#         summary = summarizer(paragraph[:1024])[0]['summary_text']  # Summarize up to max token limit
#         summarized_results.append((paragraph, summary))
#     except Exception as e:
#         print(f"Error processing paragraph: {e}")

# # Create a DataFrame to store the results
# summary_df = pd.DataFrame(summarized_results, columns=["Original Paragraph", "Summary"])

# # Save output for review
# output_file = "Deal_Summaries.xlsx"
# summary_df.to_excel(output_file, index=False)

# print(f"Summaries saved to {output_file}")
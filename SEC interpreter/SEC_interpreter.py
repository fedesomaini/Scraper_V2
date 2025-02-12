import os
import pandas as pd
import re
from datetime import datetime
from transformers import pipeline

# Define paths
base_dir = os.path.dirname(__file__)  # Current script location
input_file = os.path.join(base_dir, "2-5-2025_EdgarInfo.xlsx")
output_dir = os.path.join(base_dir, "SEC_interpreter_outputs")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = os.path.join(output_dir, f"Deal_Summaries_{timestamp}.xlsx")

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load the dataset
data = pd.read_excel(input_file)

# Initialize NLP models
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER")  # Named Entity Recognition

# Extract paragraphs
paragraphs = data["Paragraph"].dropna().tolist()

# Define helper functions
def extract_company_names(text):
    """Extracts company names using NER and filters out non-deal entities."""
    entities = [ent['word'] for ent in ner_pipeline(text) if ent['entity'] == "ORG"]
    unique_names = list(set(entities))  # Remove duplicates
    return ", ".join(unique_names) if unique_names else None

def extract_dates(text):
    """Extracts dates (e.g., 'December 2018', '2016') from text."""
    date_pattern = r"\b(January|February|March|April|May|June|July|August|September|October|November|December)?\s?(\d{4})\b"
    matches = re.findall(date_pattern, text)
    dates = [" ".join(match).strip() for match in matches]
    return ", ".join(dates) if dates else None

def extract_deal_terms(text):
    """Extracts deal types, payments, royalties, and other key terms using regex patterns."""
    
    # Deal types
    deal_patterns = {
        "Acquisition": r"\bacquired\b|\bpurchased\b|\bbought\b",
        "License": r"\blicense\b|\blicensing\b",
        "Collaboration": r"\bcollaborate\b|\bcollaboration\b",
        "Royalty Agreement": r"\broyalty\b|\broyalties\b",
        "Option Exercise": r"\bexercised our option\b",
        "Milestone Payments": r"\bmilestone\b|\bpost-licensing\b"
    }
    deal_type = [key for key, pattern in deal_patterns.items() if re.search(pattern, text, re.IGNORECASE)]
    
    # Extract monetary values **with units**
    amount_pattern = r"\$(\d+(?:,\d{3})*(?:\.\d+)?)\s?(million|billion)?"
    amounts = [f"${match[0]} {match[1]}" if match[1] else f"${match[0]}" for match in re.findall(amount_pattern, text)]

    # Extract royalty percentages
    royalty_pattern = r"\b(\d{1,2})%\b"
    royalties = [f"{match}%" for match in re.findall(royalty_pattern, text)]
    
    # Extract exclusivity terms
    exclusive = "Exclusive" if re.search(r"\bexclusive\b", text, re.IGNORECASE) else None

    # Consolidate extracted terms
    terms = []
    if deal_type:
        terms.append(f"Deal type: {', '.join(deal_type)}")
    if amounts:
        terms.append(f"Payments: {', '.join(amounts)}")
    if royalties:
        terms.append(f"Royalties: {', '.join(royalties)}")
    if exclusive:
        terms.append(exclusive)
    
    return "; ".join(terms) if terms else None

def generate_summary(text):
    """Formats extracted data into a readable summary."""
    company_names = extract_company_names(text)
    deal_terms = extract_deal_terms(text)
    deal_date = extract_dates(text)

    summary_parts = []
    if deal_date:
        summary_parts.append(f"Date: {deal_date}")
    if company_names:
        summary_parts.append(f"Agreement with {company_names}")
    if deal_terms:
        summary_parts.append(deal_terms)

    return ". ".join(summary_parts) + "." if summary_parts else "No significant deal terms extracted."

# Process paragraphs
summarized_results = []

print("Extracting deal information from paragraphs...")
for paragraph in paragraphs:
    try:
        summary = generate_summary(paragraph)
        summarized_results.append((paragraph, summary))
    except Exception as e:
        print(f"Error processing paragraph: {e}")

# Create DataFrame with formatted summaries
summary_df = pd.DataFrame(summarized_results, columns=["Original Paragraph", "Structured Summary"])

# Save the output
summary_df.to_excel(output_file, index=False)

print(f"Summaries saved to: {output_file}")


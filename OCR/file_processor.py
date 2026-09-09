import os
import pandas as pd
from pypdf import PdfReader
from docx import Document


def extract_pdf(file_path):
    """Extract text from PDF."""

    reader = PdfReader(file_path)

    text = ""

    for page_number, page in enumerate(reader.pages, start=1):

        page_text = page.extract_text()

        if page_text:
            text += f"\n--- Page {page_number} ---\n"
            text += page_text

    return text


def extract_docx(file_path):
    """Extract text from DOCX."""

    document = Document(file_path)

    text = ""

    for paragraph in document.paragraphs:

        if paragraph.text.strip():
            text += paragraph.text + "\n"

    return text


def extract_csv(file_path):
    """Extract text from CSV."""

    dataframe = pd.read_csv(file_path)

    return dataframe.to_string(index=False)


def extract_excel(file_path):
    """Extract text from Excel."""

    excel_file = pd.ExcelFile(file_path)

    text = ""

    for sheet_name in excel_file.sheet_names:

        dataframe = pd.read_excel(
            file_path,
            sheet_name=sheet_name
        )

        text += f"\n--- Sheet: {sheet_name} ---\n"
        text += dataframe.to_string(index=False)
        text += "\n"

    return text


def extract_text_file(file_path):
    """Extract text from TXT."""

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:

        return file.read()


def process_file(file_path):

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":

        return extract_pdf(file_path)

    elif extension == ".docx":

        return extract_docx(file_path)

    elif extension == ".csv":

        return extract_csv(file_path)

    elif extension in [".xlsx", ".xls"]:

        return extract_excel(file_path)

    elif extension == ".txt":

        return extract_text_file(file_path)

    else:

        raise ValueError(
            f"Unsupported file type: {extension}"
        )

if __name__ == "__main__":

    file_path = input(
        "Enter the complete path of your file: "
    )

    try:

        text = process_file(file_path)

        print("\n===== FILE PROCESSED SUCCESSFULLY =====\n")

        print(text[:5000])

    except Exception as e:

        print("\nERROR:")
        print(e)

from ollama import chat


def ask_question(document_text, question):
    prompt = f"""
You are a document question-answering assistant.

Answer the user's question ONLY using the document content provided below.

If the answer is not present in the document, say:
"I could not find this information in the document."

DOCUMENT:
{document_text}

QUESTION:
{question}

Give a clear and simple answer.
"""

    response = chat(
        model="qwen3-vl:4b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.message.content

"""text = extract_text(file_path)"""

print("\nFile loaded successfully!")
print("=" * 60)

while True:
    question = input("\nAsk a question about this file (or type 'exit'): ")

    if question.lower() == "exit":
        break

    answer = ask_question(text, question)

    print("\n===== ANSWER =====")
    print(answer)
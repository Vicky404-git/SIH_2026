import os
from pypdf import PdfReader
from ollama import chat


def extract_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def ask_qwen(document_text, question):

    prompt = f"""
You are a helpful document assistant.

Answer the user's question using the document below.

If the answer is not present in the document, say:
"I could not find this information in the document."

DOCUMENT:
{document_text}

QUESTION:
{question}
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


def choose_pdf():

    input_folder = "input"

    pdf_files = [
        file for file in os.listdir(input_folder)
        if file.lower().endswith(".pdf")
    ]

    if not pdf_files:
        print("No PDF files found in the input folder.")
        return None

    print("\n===== AVAILABLE PDF FILES =====")

    for i, file in enumerate(pdf_files, start=1):
        print(f"{i}. {file}")

    while True:

        choice = input("\nChoose a PDF number: ")

        if choice.isdigit():

            choice = int(choice)

            if 1 <= choice <= len(pdf_files):

                selected_file = pdf_files[choice - 1]

                return os.path.join(input_folder, selected_file)

        print("Please enter a valid number.")


if __name__ == "__main__":

    # Choose PDF
    pdf_path = choose_pdf()

    if pdf_path:

        print(f"\nSelected PDF: {pdf_path}")

        # Extract PDF text
        text = extract_pdf_text(pdf_path)

        print("\nPDF loaded successfully!")

        # Ask question
        question = input("\nAsk a question about the PDF: ")

        # Ask Qwen
        answer = ask_qwen(text, question)

        # Display answer
        print("\n===== QWEN ANSWER =====")
        print(answer)
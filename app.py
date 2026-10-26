
import os
import json
from pathlib import Path

import streamlit as st
import fitz
from dotenv import load_dotenv
from google import genai

load_dotenv(Path(__file__).with_name(".env"))

st.set_page_config(
    page_title="Research Paper Reading Assistant",
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI Research Paper Reading Assistant")
st.write(
    "Understand research papers, test your knowledge, "
    "and revise important concepts."
)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("API key not found. Check your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)


def ask_gemini(prompt, paper_text):
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=[
            prompt,
            "Use only the following research paper text as your source:\n"
            + paper_text[:40000]
        ]
    )
    return response.text or ""


uploaded_file = st.file_uploader(
    "Upload a research paper in PDF format",
    type=["pdf"]
)

if uploaded_file:
    try:
        with fitz.open(
            stream=uploaded_file.getvalue(),
            filetype="pdf"
        ) as document:
            pages = [page.get_text() for page in document]
            paper_text = "\n".join(pages)

        if not paper_text.strip():
            st.error(
                "No readable text found. Please try a text-based PDF."
            )
            st.stop()

        st.success(
            f"PDF uploaded successfully! Pages: {len(pages)}"
        )

        with st.expander("Preview extracted text"):
            st.text(paper_text[:3000])

        task = st.selectbox(
            "Choose a feature",
            [
                "Summarize the paper",
                "Explain in simple English",
                "Generate interactive quiz",
                "Create interactive flashcards"
            ]
        )

        if task == "Generate interactive quiz":
            quiz_count = st.selectbox(
                "Number of questions",
                [5, 10],
                index=0
            )

        if task == "Create interactive flashcards":
            card_count = st.selectbox(
                "Number of flashcards",
                [5, 10, 15],
                index=1
            )

        if st.button("Generate", type="primary"):
            if task == "Summarize the paper":
                prompt = """
                Summarize the research paper for an undergraduate student.
                Use these headings:
                1. Research problem
                2. Objective
                3. Methodology
                4. Dataset or materials
                5. Key results
                6. Limitations
                7. Important conclusion

                Do not invent information absent from the paper.
                """

                with st.spinner("Summarizing the paper..."):
                    try:
                        result = ask_gemini(prompt, paper_text)
                        st.session_state.summary_result = result
                    except Exception as error:
                        st.error(f"Could not generate summary: {error}")

            elif task == "Explain in simple English":
                prompt = """
                Explain this research paper to an undergraduate student.
                Use simple English, explain technical terms,
                and give examples where useful.
                Do not invent facts.
                """

                with st.spinner("Preparing a simple explanation..."):
                    try:
                        result = ask_gemini(prompt, paper_text)
                        st.session_state.explanation_result = result
                    except Exception as error:
                        st.error(f"Could not explain the paper: {error}")

            elif task == "Generate interactive quiz":
                prompt = f"""
                Create exactly {quiz_count} multiple-choice questions
                based only on this research paper.

                Return ONLY valid JSON in this format:
                {{
                  "questions": [
                    {{
                      "question": "Question text",
                      "options": {{
                        "A": "First option",
                        "B": "Second option",
                        "C": "Third option",
                        "D": "Fourth option"
                      }},
                      "answer": "A",
                      "explanation": "Brief explanation based on the paper"
                    }}
                  ]
                }}

                Requirements:
                - Exactly {quiz_count} questions.
                - Four options per question.
                - The answer must be A, B, C, or D.
                - Avoid ambiguous questions.
                - Do not include information absent from the paper.
                """

                with st.spinner("Creating your quiz..."):
                    try:
                        result = ask_gemini(prompt, paper_text)
                        result = result.strip()

                        if result.startswith("```"):
                            result = result.split("\n", 1)[1]
                            result = result.rsplit("```", 1)[0].strip()

                        quiz_data = json.loads(result)
                        questions = quiz_data.get("questions", [])

                        if not questions:
                            raise ValueError(
                                "No questions were returned. Try again."
                            )

                        st.session_state.quiz_data = questions
                        st.session_state.quiz_answers = {}
                        st.session_state.quiz_submitted = False

                    except Exception as error:
                        st.error(
                            f"Could not create the quiz: {error}"
                        )

            elif task == "Create interactive flashcards":
                prompt = f"""
                Create exactly {card_count} flashcards based only
                on this research paper.

                Return ONLY valid JSON in this format:
                {{
                  "cards": [
                    {{
                      "question": "A concise question",
                      "answer": "A concise and accurate answer"
                    }}
                  ]
                }}

                Focus on concepts, methods, findings, and technical terms.
                Do not invent facts.
                """

                with st.spinner("Creating flashcards..."):
                    try:
                        result = ask_gemini(prompt, paper_text)
                        result = result.strip()

                        if result.startswith("```"):
                            result = result.split("\n", 1)[1]
                            result = result.rsplit("```", 1)[0].strip()

                        flashcard_data = json.loads(result)
                        cards = flashcard_data.get("cards", [])

                        if not cards:
                            raise ValueError(
                                "No flashcards were returned. Try again."
                            )

                        st.session_state.flashcards = cards
                        st.session_state.card_index = 0
                        st.session_state.card_revealed = False

                    except Exception as error:
                        st.error(
                            f"Could not create flashcards: {error}"
                        )

        if "summary_result" in st.session_state:
            st.subheader("Research Paper Summary")
            st.markdown(st.session_state.summary_result)

        if "explanation_result" in st.session_state:
            st.subheader("Simple Explanation")
            st.markdown(st.session_state.explanation_result)

        if "quiz_data" in st.session_state:
            questions = st.session_state.quiz_data

            st.divider()
            st.subheader("📝 Interactive Quiz")

            if not st.session_state.get("quiz_submitted", False):
                with st.form("quiz_form"):
                    selected_answers = {}

                    for index, question in enumerate(questions):
                        st.markdown(
                            f"**Q{index + 1}. {question['question']}**"
                        )

                        options = question.get("options", {})
                        selected = st.radio(
                            f"Choose your answer for Q{index + 1}",
                            options=list(options.keys()),
                            format_func=lambda key, opts=options:
                                f"{key}. {opts[key]}",
                            index=None,
                            key=f"quiz_question_{index}"
                        )

                        selected_answers[index] = selected

                    submitted = st.form_submit_button(
                        "Submit quiz",
                        type="primary"
                    )

                    if submitted:
                        st.session_state.quiz_answers = selected_answers
                        st.session_state.quiz_submitted = True
                        st.rerun()

            else:
                answers = st.session_state.quiz_answers
                score = 0

                for index, question in enumerate(questions):
                    correct = question.get("answer", "").upper()
                    chosen = answers.get(index)

                    st.markdown(
                        f"**Q{index + 1}. {question['question']}**"
                    )

                    if chosen == correct:
                        score += 1
                        st.success(
                            f"Correct! {correct}. "
                            f"{question.get('explanation', '')}"
                        )
                    else:
                        st.error(
                            f"Your answer: {chosen or 'Not answered'}. "
                            f"Correct answer: {correct}. "
                            f"{question.get('explanation', '')}"
                        )

                st.metric(
                    "Your score",
                    f"{score} / {len(questions)}"
                )

                if st.button("Try quiz again"):
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_answers = {}
                    st.rerun()

        if "flashcards" in st.session_state:
            cards = st.session_state.flashcards

            if cards:
                st.divider()
                st.subheader("🗂️ Interactive Flashcards")

                index = st.session_state.get("card_index", 0)
                index = min(index, len(cards) - 1)
                card = cards[index]

                st.progress((index + 1) / len(cards))
                st.caption(
                    f"Card {index + 1} of {len(cards)}"
                )

                st.markdown("### Question")
                st.info(card.get("question", "No question available."))

                if st.button(
                    "Hide answer" if st.session_state.get(
                        "card_revealed", False
                    ) else "Reveal answer",
                    key="reveal_card"
                ):
                    st.session_state.card_revealed = not (
                        st.session_state.get("card_revealed", False)
                    )
                    st.rerun()

                if st.session_state.get("card_revealed", False):
                    st.markdown("### Answer")
                    st.success(card.get("answer", "No answer available."))

                col1, col2 = st.columns(2)

                with col1:
                    if st.button(
                        "← Previous",
                        disabled=index == 0,
                        key="previous_card"
                    ):
                        st.session_state.card_index = index - 1
                        st.session_state.card_revealed = False
                        st.rerun()

                with col2:
                    if st.button(
                        "Next →",
                        disabled=index == len(cards) - 1,
                        key="next_card"
                    ):
                        st.session_state.card_index = index + 1
                        st.session_state.card_revealed = False
                        st.rerun()

    except Exception as error:
        st.error(f"Could not read this PDF: {error}")

else:
    st.info("Upload a PDF to get started.")
    st.markdown(
        """
        **Available features**
        - Research paper summaries
        - Simple explanations of technical concepts
        - Interactive quizzes with automatic scoring
        - Flashcards with revealable answers
        """
    )

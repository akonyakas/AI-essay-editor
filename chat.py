from openai import OpenAI
from pydantic import BaseModel
import re
from typing import List, Optional, Dict, Any

client = OpenAI(
    api_key="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"
)

prompt = """
You are a helpful assistant who checks the grammar of an essay. For each sentence in the essay:
Review the sentence for grammatical errors related to subject-verb agreement, passive voice, cohesion and coherence, clarity, and style.
If the sentence is grammatically correct return none for revised_sentence and explanation, else revise each sentence separately, providing corrections where needed.
After revising, explain the reason for each correction based on the following grammar rules:
Action and Subject: Ensuring that the subject and the action (verb) are clearly aligned.
Passive Voice: Identifying and changing passive voice to active voice where appropriate for stronger sentences.
Cohesion and Coherence: Ensuring that ideas flow logically and smoothly from one sentence to the next.
Clarity and Style: Improving word choice, sentence structure, and readability.
Finally, rewrite the entire revised essay, ensuring it is cohesive and free from grammatical issues and give some recommendations"
"""


class SentenceLengthError(Exception):
    pass


class GPTRefusalError(Exception):
    pass


class Step(BaseModel):
    revised_sentence: str | None
    explanation: str | None


class GrammarEditor(BaseModel):
    steps: list[Step]


class GrammarChecker:
    def __init__(self, prompt: str, client: Any):
        """
        Initializes the GrammarChecker with a prompt and a client for processing the paragraphs.

        :param prompt: The system prompt to provide guidance for sentence grammar checks.
        :param client: The client for connecting to a language model API for grammar checking.
        """
        self.prompt = prompt
        self.client = client

    def split_to_paragraphs(self, text: str, char_limit: int = 500) -> List[str]:
        """
        Splits the input text into paragraphs while adhering to a character limit for each paragraph.

        :param text: The full input text to be split into paragraphs.
        :param char_limit: The maximum number of characters per paragraph.
        :return: A list of paragraphs, with each paragraph having a length <= char_limit.
        """
        paragraphs = text.split("\n\n")
        chunks = []

        for paragraph in paragraphs:
            if len(paragraph) <= char_limit:
                chunks.append(paragraph)
            else:
                # Split by sentence-ending punctuation
                sentences = re.split(r"(?<=[.!?])\s+", paragraph)
                chunk = ""
                for sentence in sentences:
                    if len(chunk) + len(sentence) + 1 > char_limit:
                        chunks.append(chunk.strip())
                        chunk = sentence
                    else:
                        chunk += " " + sentence
                if chunk:
                    chunks.append(chunk.strip())
        return chunks

    def process_paragraph(self, text: str) -> List[Dict[str, Optional[str]]]:
        """
        Processes a paragraph of text by checking and correcting grammar.

        :param text: A single paragraph of text.
        :return: A list of dictionaries containing the original sentence, revised sentence, and explanation.
        """
        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.8,
            response_format=GrammarEditor,
        )

        grammar_editor = completion.choices[0].message

        if grammar_editor.refusal:
            raise GPTRefusalError(grammar_editor.refusal)

        sentence_pattern = r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s"
        sentences = re.split(sentence_pattern, text)

        if len(grammar_editor.steps) != len(sentences):
            raise SentenceLengthError(
                f"Expected [{len(grammar_editor.steps)}] sentences, but found [{len(sentences)}] in the input."
            )

        result = []
        for step, orig_sent in zip(grammar_editor.steps, sentences):
            result.append(
                {
                    "original_sentence": orig_sent,
                    "revised_sentence": step.revised_sentence,
                    "explanation": step.explanation,
                }
            )
        return result

    def process_with_retries(
        self, paragraph: str, max_retries: int = 3
    ) -> Optional[List[Dict[str, Optional[str]]]]:
        """
        Processes a paragraph with retries in case of errors.

        :param paragraph: The paragraph to process.
        :param max_retries: The maximum number of retries allowed in case of failures.
        :return: A list of grammar correction results or None if retries fail.
        """
        for attempt in range(max_retries):
            try:
                return self.process_paragraph(paragraph)

            except GPTRefusalError as e:
                print(
                    f"Attempt {attempt + 1}/{max_retries} failed due to GPT refusal error: {e}"
                )
            except SentenceLengthError as e:
                print(
                    f"Attempt {attempt + 1}/{max_retries} failed due to sentence length error: {e}"
                )
            except Exception as e:
                print(
                    f"Attempt {attempt + 1}/{max_retries} failed due to unexpected error: {e}"
                )

        print(f"Max retry count reached for paragraph: {paragraph}")
        return None

    def process_text(self, text: str) -> List[Dict[str, Optional[str]]]:
        """
        Splits text into paragraphs, processes each paragraph for grammar checking, and returns the results.

        :param text: The full input text to be processed.
        :return: A list of grammar correction results.
        """
        paragraphs = self.split_to_paragraphs(text)
        print(f"Number of paragraphs: {len(paragraphs)}")

        output = []
        for idx, paragraph in enumerate(paragraphs):
            print(f"Processing paragraph {idx + 1}/{len(paragraphs)}...")
            paragraph_results = self.process_with_retries(paragraph)

            if paragraph_results is None:
                print(f"Failed to process paragraph {idx + 1} after retries.")
            else:
                output.extend(paragraph_results)
                print(f"[DONE] Paragraph {idx + 1}")

        print("Processing completed.")
        return output

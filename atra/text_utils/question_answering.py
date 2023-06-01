import torch
from atra.model_utils.model_utils import get_model_and_processor
from atra.utils import timeit
import gradio as gr
from atra.statics import PROMPTS


def answer_question(text, question, input_lang, progress=gr.Progress()) -> str:
    progress.__call__(0.2, "Filtering Text")
    text = PROMPTS["question-answering"][input_lang].format(
        text=text, question=question
    )
    model, tokenizer = get_model_and_processor(
        input_lang, "question-answering", progress=progress
    )
    progress.__call__(0.7, "Tokenizing Text")
    inputs = tokenizer(text, return_tensors="pt", max_length=128_000, truncation=True)
    progress.__call__(0.8, "Answering Question")
    generated_tokens = inference_qa(model, inputs)
    progress.__call__(0.9, "Converting to Text")
    result = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
    return result


@timeit
def inference_qa(model, inputs):
    inputs.to(model.device)

    with torch.inference_mode():
        generated_tokens = model.generate(
            **inputs,
            max_new_tokens=1024,
            do_sample=False,
            num_beams=5,
            early_stopping=True,
        )

    return generated_tokens

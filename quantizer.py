from transformers import AutoTokenizer
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig

BITS = 8
pretrained_model_dir = "TheBloke/OpenAssistant-SFT-7-Llama-30B-HF"
quantized_model_dir = f"OpenAssistant-SFT-7-Llama-30B-{BITS}-bits-autogptq"

tokenizer = AutoTokenizer.from_pretrained(pretrained_model_dir, use_fast=True)
examples = [
    tokenizer(
        x
    ) for x in ["Can you explain the quantization of models in simple words?",
                "Erkläre mir bitte die Quantisierung von Modellen.",
                "Schreibe ein kurzes Gedicht über Freundschaft.",
                "Wie ist das Wetter heute?",]
]

quantize_config = BaseQuantizeConfig(
    bits=BITS,
    group_size=128,  # it is recommended to set the value to 128
    desc_act=False,  # set to False can significantly speed up inference but the perplexity may slightly bad 
)

try:
    model = AutoGPTQForCausalLM.from_quantized(quantized_model_dir, trust_remote_code=True, use_safetensors=True)
except Exception as e:
    print(e)
    # load un-quantized model, by default, the model will always be loaded into CPU memory
    model = AutoGPTQForCausalLM.from_pretrained(pretrained_model_dir, quantize_config, trust_remote_code=True)

    # quantize model, the examples should be list of dict whose keys can only be "input_ids" and "attention_mask"
    model.quantize(examples, batch_size=4, use_cuda_fp16=False, cache_examples_on_gpu=False)

# save quantized model using safetensors
model.save_quantized(quantized_model_dir, use_safetensors=True)
tokenizer.save_pretrained(quantized_model_dir)

model.push_to_hub(quantized_model_dir, use_safetensors=True)
tokenizer.push_to_hub(quantized_model_dir)
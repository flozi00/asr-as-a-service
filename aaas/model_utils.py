from functools import lru_cache

import peft
import torch
from optimum.bettertransformer import BetterTransformer
from transformers import AutoProcessor

from aaas.statics import MODEL_MAPPING
from aaas.utils import timeit


@timeit
def get_model(model_class, model_id):
    model = model_class.from_pretrained(
        model_id,
        cache_dir="./model_cache",
        load_in_8bit=torch.cuda.is_available(),
        device_map="auto",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    )

    return model


@timeit
def get_processor(processor_class, model_id):
    processor = processor_class.from_pretrained(model_id)
    return processor


@timeit
def get_peft_model(peft_model_id, model_class) -> peft.PeftModel:
    # Load the PEFT model
    peft_config = peft.PeftConfig.from_pretrained(peft_model_id)
    model = model_class.from_pretrained(
        peft_config.base_model_name_or_path,
        cache_dir="./model_cache",
        load_in_8bit=False,
        device_map="auto",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    )
    model = peft.PeftModel.from_pretrained(
        model,
        peft_model_id,
        cache_dir="./model_cache",
        load_in_8bit=False,
        device_map="auto",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    )
    model = model.eval()


    # Remove the LORA modules
    key_list = [
        key for key, _ in model.base_model.model.named_modules() if "lora" not in key
    ]
    for key in key_list:
        parent, target, target_name = model.base_model._get_submodules(key)
        if isinstance(target, peft.tuners.lora.Linear):
            bias = target.bias is not None
            new_module = torch.nn.Linear(
                target.in_features, target.out_features, bias=bias
            )
            model.base_model._replace_module(parent, target_name, new_module, target)

    return model


@lru_cache(maxsize=1)
@timeit
def get_model_and_processor(lang: str, task: str, config: str):
    # get model id
    model_id = MODEL_MAPPING[task][config].get(lang, {}).get("name", None)
    adapter_id = MODEL_MAPPING[task][config].get(lang, {}).get("adapter_id", None)

    if model_id is None:
        base_model_lang = "universal"
        model_id = MODEL_MAPPING[task][config][base_model_lang]["name"]
    else:
        base_model_lang = lang

    model_class = MODEL_MAPPING[task][config][base_model_lang].get("class", None)

    if adapter_id is not None:
        model = get_peft_model(adapter_id, model_class)
    else:
        model = get_model(model_class, model_id)

    # get processor
    processor_class = MODEL_MAPPING[task][config][base_model_lang].get(
        "processor", AutoProcessor
    )
    processor = get_processor(processor_class, model_id)

    # convert the model to a BetterTransformer model
    try:
        model = BetterTransformer.transform(model)
    except Exception as e:
        print("Bettertransformer exception: ",e)

    #try:
    #    model = torch.compile(model, mode="reduce-overhead")
    #except Exception as e:
    #    print("Torch compile exception: ", e)

    return model, processor

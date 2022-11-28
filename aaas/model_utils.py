import onnxruntime
import os

cpu_threads = os.cpu_count()

providers = [
    #"CUDAExecutionProvider",
    "OpenVINOExecutionProvider",
    "CPUExecutionProvider",
]

for p in providers:
    if p in onnxruntime.get_available_providers():
        provider = p
        break

provider_options = {}

if provider == "OpenVINOExecutionProvider":
    provider_options["num_of_threads": cpu_threads]

sess_options = onnxruntime.SessionOptions()
sess_options.graph_optimization_level = (
    onnxruntime.GraphOptimizationLevel.ORT_ENABLE_ALL
)


def get_model(model_class, model_id):
    try:
        model = model_class.from_pretrained(
            model_id,
            provider=provider,
            session_options=sess_options,
            from_transformers=True,
            cache_dir="./model_cache",
        )
    except:
        model = model_class.from_pretrained(
            model_id,
            cache_dir="./model_cache",
        )

    return model
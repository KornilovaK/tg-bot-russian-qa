# Prepare data and Train model

## Datasets HuggingFace:
* [Eka-Korn/distillbert-qa-russian](https://huggingface.co/datasets/Eka-Korn/distillbert-qa-russian) was made of [kuznetsoffandrey/sberquad](https://huggingface.co/datasets/kuznetsoffandrey/sberquad) and [lmqg/qag_ruquad](https://huggingface.co/datasets/lmqg/qag_ruquad) datasets by [distilbert/distilbert-base-cased-distilled-squad](https://huggingface.co/distilbert/distilbert-base-cased-distilled-squad) tokenizer
* [Eka-Korn/qa-russian](https://huggingface.co/datasets/Eka-Korn/qa-russian) was made of the same preferences, but by [t5-small](https://huggingface.co/google-t5/t5-small) tokenizer

## Training with Lora
### 1. Distillbert
* [Eka-Korn/distillbert-qa-tuned-lora_1.01_v2](https://huggingface.co/Eka-Korn/distillbert-qa-tuned-lora_1.01_v2)
* Dataset: distillbert-qa-russian
* EPOCHS ~ 15
* Lora trainable params: 1.001%
* Evaluation metrics: 
* * F1: 0.7232768099092667
* * SAS: 0.8044405
* * METEOR: 0.6431945091247689

### 2. T5
* [Eka-Korn/t5-qa-tuned-lora_1.75](https://huggingface.co/Eka-Korn/t5-qa-tuned-lora_1.75)
* Dataset: qa_russian
* EPOCHS ~ 6
* Lora trainable params: 1.757%
* Evaluation metrics: 
* * F1: 0.6846462845943829
* * SAS: 0.7555522322654724
* * METEOR: 0.7666797829362197
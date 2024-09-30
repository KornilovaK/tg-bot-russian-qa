import numpy as np
import torch
from functools import partial


def retrieve_preds_and_labels(
    start_logits, end_logits, input_ids,
    seq_ids, start_pos=None, end_pos=None,
    n_best=20, max_answer_len=50, tokenizer=True
):
    assert (
        isinstance(n_best, int)
        and isinstance(max_answer_len, int)
        and n_best > 0
        and max_answer_len > 0
    )

    start_idx_list = np.argsort(start_logits.cpu().numpy())[-1 : (-n_best - 1) : -1]
    end_idx_list = np.argsort(end_logits.cpu().numpy())[-1 : (-n_best - 1) : -1]

    valid_answers = []
    for start_idx in start_idx_list:
        for end_idx in end_idx_list:
            if (seq_ids[start_idx].item() != 1 or seq_ids[end_idx].item() != 1):
                continue
            if start_idx > end_idx or end_idx - start_idx + 1 > max_answer_len:
                continue

            valid_answers.append(
                {
                    "score": start_logits[start_idx] + end_logits[end_idx],
                    "start_idx": start_idx,
                    "end_idx": end_idx,
                }
            )
    final_preds = sorted(valid_answers, key=lambda x: x["score"], reverse=True)[0]
    final_decoded_preds = tokenizer.decode(
        input_ids[final_preds["start_idx"] : (final_preds["end_idx"] + 1)]
    )

    return (final_decoded_preds,)

def postprocess(batch, output, tokenizer=True, **kwargs):
    b_size = batch["input_ids"].size(0)
    mapfunc = partial(retrieve_preds_and_labels, tokenizer=tokenizer, **kwargs)

    start_pos, end_pos = torch.empty((b_size, 1)), torch.empty((b_size, 1))
    postprocessed_output = list(
        map(
            mapfunc,
            output.start_logits,
            output.end_logits,
            batch["input_ids"],
            batch["sequence_ids"],
            start_pos,
            end_pos,
        )
    )

    return np.array([postprocessed_output[i][0] for i in range(b_size)])

def predict_answer(model, tokenizer, question, context, device):
    inputs = tokenizer(question.strip(), context.strip(), max_length=512, truncation=True, padding="max_length")
    for key in inputs:
        inputs[key] = torch.tensor(inputs[key], dtype=torch.int64).unsqueeze(0)

    inputs["sequence_ids"] = torch.tensor(np.array(inputs.sequence_ids(), dtype=float)).unsqueeze(0)

    model.eval()
    with torch.no_grad():
        inference_output = model(
            inputs["input_ids"].to(device),
            attention_mask=inputs["attention_mask"].to(device),
        )

    return postprocess(inputs, inference_output, tokenizer=tokenizer)[0]
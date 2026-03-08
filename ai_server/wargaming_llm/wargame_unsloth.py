import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

from unsloth import FastLanguageModel
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset
import torch

# --- 1. CORE SETTINGS ---
max_seq_length = 1024 
model_id = "unsloth/Qwen3.5-4B" 

# 2. LOAD MODEL (Stable Eager Mode)
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_id,
    max_seq_length = max_seq_length,
    dtype = None, 
    load_in_4bit = True,
    trust_remote_code = True,
    attn_implementation = "eager", 
)

# 3. HIGH-CAPACITY LORA (r=32 for better logic retention)
model = FastLanguageModel.get_peft_model(
    model,
    r = 32, # Increased from 16 to 32
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 64,
    lora_dropout = 0, 
    bias = "none",    
    use_gradient_checkpointing = "unsloth", 
    random_state = 3407,
)

# 4. DATASET PREP (With aggressive whitespace cleaning)
dataset = load_dataset("json", data_files="wargame_dataset.jsonl", split="train")

def clean_text(value: str) -> str:
    """Normalize hidden whitespace characters that can sneak in from web/PDF copy."""
    if not isinstance(value, str):
        value = str(value)
    # Replace common problematic whitespace with normal spaces or nothing
    value = (
        value.replace("\u00A0", " ")  # non-breaking space
             .replace("\u200B", "")   # zero-width space
             .replace("\u200C", "")   # zero-width non-joiner
             .replace("\u200D", "")   # zero-width joiner
             .replace("\uFEFF", "")   # byte-order mark
    )
    return value.strip()


def formatting_prompts_func(examples):
    instructions = examples["instruction"]
    inputs       = examples["input"]
    outputs      = examples["output"]
    texts = []
    for instr, inp, out in zip(instructions, inputs, outputs):
        instr_clean = clean_text(instr)
        inp_clean   = clean_text(inp)
        out_clean   = clean_text(out)

        # We use a standard Alpaca-style prompt which is more stable for training logic
        text = (
            "Below is an instruction that describes a task, paired with an input that provides further context. "
            "Write a response that appropriately completes the request.\n\n"
        )
        text += f"### Instruction:\n{instr_clean}\n\n"
        text += f"### Input:\n{inp_clean}\n\n"
        text += f"### Response:\n{out_clean}"
        texts.append(text)
    return { "text" : texts, }

dataset = dataset.map(formatting_prompts_func, batched = True)

# 5. TRAINING SETUP (The 'Kickstart' Config)
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    packing = True, 
    args = SFTConfig(
        per_device_train_batch_size = 2, 
        gradient_accumulation_steps = 4, 
        max_steps = 125, 
        learning_rate = 2e-4, # Higher LR to break out of the 12.0 plateau
        warmup_ratio = 0.1,    # Uses 10% of steps to ramp up slowly
        weight_decay = 0.01,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        optim = "paged_adamw_8bit", # More stable version for Windows
        seed = 3407,
        output_dir = "wargame_final_outputs",
    ),
)

# 6. EXECUTION
print("\n--- Training Starting: Force Logic Learning Mode ---")
try:
    trainer.train()
except KeyboardInterrupt:
    print("\n[Ctrl+C detected] Stopping training early and saving current model...")
finally:
    # 7. SAVE (always run, even if interrupted)
    print("\n--- Saving model and tokenizer to 'wargame_final_lora' ---")
    model.save_pretrained("wargame_final_lora")
    tokenizer.save_pretrained("wargame_final_lora")
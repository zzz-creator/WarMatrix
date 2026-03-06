from unsloth import FastLanguageModel
import torch

# 1. Configuration - Point this to your finished folder
model_path = "wargame_final_outputs/checkpoint-125" # Update if you renamed it

# 2. Load the Model and Tokenizer
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_path,
    max_seq_length = 2048,
    load_in_4bit = True, # Match your training settings
)
FastLanguageModel.for_inference(model) # Enable 2x faster inference

# 3. Define the Test Scenario
# Use the EXACT format you used in your JSONL dataset
instruction = "Generate a comprehensive tactical SITREP based on the current battlefield variables."

# Stress Test Input: Give it a scenario it likely hasn't seen before
battlefield_data = """Location: Obsidian Gorge
Terrain: Narrow volcanic canyon with unstable footing
Enemy Activity: Heavy artillery zeroing in on the southern entrance
Friendly Action: Forced march to reach the extraction point
Operational Risk: Critical
Success Probability: 34%
Morale: Faltering
Supply Stability: Depleted
Weather: Ash Storm (Zero Visibility)
Estimated Force Ratio (Friendly:Enemy): 1:5
Current Operational Tempo: Emergency
Civilian Environment Pressure: None
Command Intent: Evacuate remaining elements before the gorge is sealed
Primary Risk Driver: Impending structural collapse of the canyon walls
Immediate Priority: Suppressive fire on enemy artillery positions
Communications Status: Intermittent
Mobility Status: Red (Vehicles abandoned)
Fires Status: Minimal"""

# 4. Format the Prompt
prompt = f"Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.\n\n### Instruction:\n{instruction}\n\n### Input:\n{battlefield_data}\n\n### Response:\n"

# 5. Generate the Output
# NOTE: For vision-language models like Qwen-VL, we must pass
# the prompt via the `text` keyword so it is not treated as an image.
inputs = tokenizer(text=[prompt], return_tensors = "pt").to("cuda")

print("\n" + "="*50)
print("RUNNING TACTICAL INFERENCE...")
print("="*50)

outputs = model.generate(
    **inputs, 
    max_new_tokens = 512, 
    use_cache = True,
    temperature = 0.7, # Adds a bit of creative "flavor" to the analysis
    top_p = 0.9
)

# Decode and print only the AI's response
response = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
print(response.split("### Response:\n")[-1].strip())
print("\n" + "="*50)
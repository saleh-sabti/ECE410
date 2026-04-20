import torch
import torch.nn as nn

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
if not torch.cuda.is_available():
    print("No CUDA GPU found. Exiting.")
    exit(1)

print(f"Device: {torch.cuda.get_device_name(0)}")

model = nn.Sequential(
    nn.Linear(4, 5),
    nn.ReLU(),
    nn.Linear(5, 1)
).to(device)

x = torch.randn(16, 4, device=device)
output = model(x)

print(f"Output shape: {output.shape}")
print(f"Output device: {output.device}")

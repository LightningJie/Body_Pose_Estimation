import torch
print(torch.__version__)
x = torch.rand(5, 3)
print(x)
if torch.cuda.is_available():
    x = x.to("cuda")
    print(x)
else:
    print("CUDA is not available")

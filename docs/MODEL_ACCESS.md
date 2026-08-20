# Model access and provenance

Model weights are intentionally not redistributed. Before downloading any
model, read the vendor model card and license, use a revision pin, and record
the resolved commit hash in the run manifest. A Hugging Face access token may
be required for gated or rate-limited artifacts; keep it in the local
environment and never commit it.

The model families used in the manuscript can be obtained from these official
model-card locations:

- Qwen3-14B: [`Qwen/Qwen3-14B`](https://huggingface.co/Qwen/Qwen3-14B)
- Phi-4: [`microsoft/phi-4`](https://huggingface.co/microsoft/phi-4)
- OLMo 2 13B: [`allenai/OLMo-2-1124-13B-Instruct`](https://huggingface.co/allenai/OLMo-2-1124-13B-Instruct)

The public release does not assert that a later model revision, tokenizer,
quantization, or provider endpoint is equivalent to the private experiment.
Record at least the model identifier, revision, tokenizer revision, decoding
parameters, device type, software versions, and random seed for every new run.

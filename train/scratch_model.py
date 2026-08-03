"""
[Alternative, not the default] A from-scratch tiny transformer, for researchers who want
full mechanistic control and zero pretraining-data contamination at the cost of much
weaker language competence (see docs/domain_spec.md, model-choice tradeoff discussion).

Not wired into train/train.py's default path. To use it, a random-init GPT-NeoX-style
config can be built directly and passed through the same LoRA/full-finetune code path,
e.g.:

    from transformers import GPTNeoXConfig, GPTNeoXForCausalLM, AutoTokenizer
    config = GPTNeoXConfig(
        vocab_size=50304, hidden_size=384, num_hidden_layers=6, num_attention_heads=6,
        intermediate_size=1536, max_position_embeddings=512,
    )
    model = GPTNeoXForCausalLM(config)  # random init, no pretrained weights
    tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-160m-deduped")  # reuse vocab

This is left as a stub deliberately: Phase 1's primary claim relies on the base model
having enough language competence to produce fluent, value-laden multi-sentence behavior,
which a laptop-trainable from-scratch model is unlikely to have (docs/methodology.md Sec 5).
"""

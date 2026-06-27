from models.selector import ModelSelector

selector = ModelSelector()

plans = [
    "use_general_model",
    "use_coder",
    "use_creative_model",
    "use_reasoning",
    "use_fast"
]

for p in plans:

    print(
        p,
        "->",
        selector.select(p)
    )

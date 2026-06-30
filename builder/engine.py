class Builder:

    def create_module(self, name):
        print(f"[Builder] Creating module: {name}")

    def verify(self):
        print("[Builder] Running verification...")

    def doctor(self):
        print("[Builder] Running diagnostics...")

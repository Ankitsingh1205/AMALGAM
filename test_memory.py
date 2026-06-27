from services.memory import MemoryService

m = MemoryService()

print("Initial:", m.show_all())

m.remember("name", "Ankit")

print("After remember:", m.show_all())

print("Recall:", m.recall("name"))

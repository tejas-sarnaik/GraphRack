from graphrack import GraphRack

engine = (GraphRack()
          .add_document("source-a", "Aster Research developed Aurora. Aurora uses retrieval.")
          .add_document("source-b", "Aurora was evaluated using the Atlas benchmark."))
print(engine.ask("Who developed Aurora?"))
print(engine.bridge("aster", "aurora"))
engine.save("my-index.json")

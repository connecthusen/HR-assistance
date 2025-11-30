from embedder import get_embedding

text = "How many casual leaves do employees get?"

vec = get_embedding(text)

print("Embedding length:", len(vec))
print(vec[:10])




from transformers import pipeline

pipe = pipeline("translation", model="google-t5/t5-small")

result = pipe("My name is Jiazhen Luo")
print(result[0]['translation_text']) 
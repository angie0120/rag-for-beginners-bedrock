import json
import math
import boto3

br = boto3.client("bedrock-runtime", region_name="us-east-1")

EMBED_MODEL = "amazon.titan-embed-text-v2:0"
TEXT_MODEL = "amazon.nova-micro-v1:0"

docs = [
    "The blue dragon guards the mountain.",
    "The library contains ancient maps.",
    "The library is full of magical books.",
    "The wizard knows the castle gates close at sunset.",
    "The wizard studies cloud patterns.",
]

question = "What does the wizard study?"

def embed(text: str) -> list[float]:
    resp = br.invoke_model(
        modelId=EMBED_MODEL,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({"inputText": text}),
    )
    return json.loads(resp["body"].read())["embedding"]

def cos(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return 0.0 if na == 0 or nb == 0 else dot / (na * nb)

qv = embed(question)
scored = sorted(((cos(qv, embed(d)), d) for d in docs), reverse=True)
top = [d for _, d in scored[:2]]

context = "\n".join(f"- {d}" for d in top)

resp = br.converse(
    modelId=TEXT_MODEL,
    system=[{"text": "Answer using ONLY the context. If the answer is not in the context, say 'I don't know.'"}],
    messages=[{"role": "user", "content": [{"text": f"Context:\n{context}\n\nQuestion:\n{question}"}]}],
    inferenceConfig={"maxTokens": 120, "temperature": 0},
)

print("Top matches:", top)
print("Answer:", resp["output"]["message"]["content"][0]["text"])



import os

from langchain_ollama import OllamaLLM

model = None


def initialise_model():
    global model
    # Ollama corre en el host con GPU (ver OLLAMA_BASE_URL); la VM solo es
    # cliente HTTP, por eso la URL sale del entorno y no va hardcodeada.
    base_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
    model = OllamaLLM(model='llama3.2', temperature=0.1, base_url=base_url)


def generate_response(user_query, retrieved_data):
    # Prompt mínimo y efectivo. Lecciones medidas en pruebas controladas:
    # - Sin restricción inventaba datos ("Faiss") y procedencia ("está en ChromaDB").
    # - Un bloque de reglas estrictas con salida exacta ("reply exactly...")
    #   volvía al modelo sobre-obediente: rechazaba hasta con el contexto
    #   correcto delante (atractor de salida fácil en modelos chicos).
    # - Hallazgo clave: el 3B solo hace grounding con la etiqueta canónica
    #   "Context". Con "Retrieved Information" ignora el bloque y sale por
    #   la cláusula de rechazo. Formato: instrucción + Context + Question + "Answer:".
    input_prompt = (
        "You are Sona, an AI assistant. Answer using only the Context below. "
        "If it does not contain the answer, say you don't have that information. "
        "Answer in the user's language. Be concise.\n\n"
        f"Context: {retrieved_data}\n\n"
        f"Question: {user_query}\n"
        "Answer:"
    )

    result = model.invoke(input=input_prompt)

    return result


"""
user_query = "How can I cope with my increased sensitivity to light?"
retrieved_data = (
    "Increased sensitivity to light can result from migraines, eye strain, or other conditions. Wearing sunglasses "
    "and consulting an eye care professional for evaluation can be beneficial."
)
print(generate_response(user_query, retrieved_data))
"""
"""
initialise_model()
while True:
    user_query = input('Enter a user query: ')
    retrieved_data = input("Enter retrieved data: ")
    print(generate_response(user_query, retrieved_data))

"""

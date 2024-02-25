import os
from openai import AzureOpenAI


# Test on Chat/Completion model
chat_client = AzureOpenAI(
  api_key = os.getenv("AZURE_OPENAI_GPT_API_KEY"),  
  api_version = os.getenv("AZURE_OPENAI_GPT_API_VERSION"),
  azure_endpoint =os.getenv("AZURE_OPENAI_BASE_URL") 
)

chat_response = chat_client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT_NAME"), # model = "deployment_name".
    messages=[
        {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
        {"role": "user", "content": "How is intent annotated in paper 'End-to-End Trainable Non-Collaborative Dialog System'"}
    ]
)

print(chat_response.model_dump_json(indent=2))

'''
# Test on Embedding model
embedding_client = AzureOpenAI(
  api_key = os.getenv("AZURE_OPENAI_EMBEDDING_API_KEY"),  
  api_version = os.getenv("AZURE_OPENAI_EMBEDDING_API_VERSION"),
  azure_endpoint =os.getenv("AZURE_OPENAI_EMBEDDING_BASE_URL") 
)

embedding_response = embedding_client.embeddings.create(
    input = "Your text string goes here",
    model= os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
)

print(embedding_response.model_dump_json(indent=2))
'''
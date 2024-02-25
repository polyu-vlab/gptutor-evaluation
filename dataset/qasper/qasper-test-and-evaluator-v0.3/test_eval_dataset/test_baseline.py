import os
import json
from openai import AzureOpenAI


# Test on Chat/Completion model
chat_client = AzureOpenAI(
  api_key = os.getenv("AZURE_OPENAI_GPT_API_KEY"),  
  api_version = os.getenv("AZURE_OPENAI_GPT_API_VERSION"),
  azure_endpoint =os.getenv("AZURE_OPENAI_BASE_URL") 
)

cur_dir = os.path.dirname(__file__)



qag_list=[]
# read from test_eval_index file to get the paper title and append it to the original question


with open(cur_dir + '/test_eval_index.txt', 'r') as test_eval_index:  
    
    for doc_name in test_eval_index.readlines():
        doc_name=doc_name.replace('\n', '')
        q_a_c_g_file_path=cur_dir + "/test_papers/" + doc_name + "/" + doc_name + ".json"
        
        with open (q_a_c_g_file_path, 'r') as q_a_c_g_file:
            qag_data=json.load(q_a_c_g_file)
            for qag in qag_data.values(): 
                question = qag["question"] + " in the paper " + doc_name

                # Since the baseline for benchmarking can only conduct end-to-end evaluation, 
                # the contexts are not needed
                del qag["contexts"]
                
                chat_response = chat_client.chat.completions.create(
                    model=os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT_NAME"), # model = "deployment_name".
                    messages=[
                        {"role": "system", "content": "Please answer the following question based on the given paper title"},
                        {"role": "user", "content": question}
                    ]
                )
                qag["question"] = question
                qag["answer"] = chat_response.choices[0].message.content
                qag_list.append(qag) 

with open('test_eval_baseline.json', 'w') as test_eval_dataset:
    json.dump(qag_list, test_eval_dataset, ensure_ascii=False, indent=4)
            

    

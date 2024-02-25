from langfuse import Langfuse
import json
import os
# LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST are 
# all set in the environment variables

cur_dir = os.path.dirname(__file__)
def langfuse_client():
    langfuse = Langfuse()
    if (langfuse.auth_check()):
        print("Successfully connect to langfuse project")
    return langfuse

# extract the top-3 chunks and answer from the exported trace (json file)
def trace_extract(client, traceid_list):
    for traceid_index in range(0, len(traceid_list)):
        trace = client.get_trace(traceid_list[traceid_index])

        context_list=[]
        answer=""
       
        for attribute in trace:

            if attribute[0]=="observations":
                span_list = attribute[1]
                for span in span_list:
                    
                    if span.name=="ParentDocumentRetriever":
                        doc_name=span.output[0]["metadata"]["title"].split('.pdf')[0]
                        print("This question comes from: ", doc_name)
                        for chunk in span.output:
                            context_list.append(chunk["pageContent"])
                    
        
                    #DOUBLE CHECK THE FORMAT (now use '\n\n') TO REMOVE THE RECOMMENDED QUESTIONS ()
                    
                    elif span.name=="ChatOpenAI":
                        answer=span.output.split('\n\n')[0]

        # q_a_c_g_file is the json file to store the question, answer, context, ground_truth pairs
        # Before integrating the answer and context from langfuse, this file contains question and ground_truth
        q_a_c_g_file_path=cur_dir + '/' + 'test_eval_dataset' + '/' + "test_papers" + '/' + doc_name + "/" + doc_name + ".json"
        qag_dict={}
        with open (q_a_c_g_file_path, 'r') as q_a_c_g_file:
            qag_dict = json.load(q_a_c_g_file)

        QAid="TestEvalQA" + str(traceid_index)
        qag_dict[QAid]['contexts']=context_list
        qag_dict[QAid]['answer']=answer
            
        
        with open (q_a_c_g_file_path, 'w') as q_a_c_g_file:
            json.dump(qag_dict, q_a_c_g_file, ensure_ascii=False, indent = 4, default=str)
        # Pre-define the trace-id as qa-id
            
# integrate the dataset into one json file, given test_eval_index
def dataset_to_file():
    qag_list=[]
    with open(cur_dir + "/test_eval_dataset/" + 'test_eval_index.txt', 'r') as test_eval_index:  
        
        for doc_name in test_eval_index.readlines():
            doc_name=doc_name.replace('\n', '')
            q_a_c_g_file_path=cur_dir + "/test_eval_dataset/" + "test_papers" + "/" + doc_name + "/" + doc_name + ".json"
            
            with open (q_a_c_g_file_path, 'r') as q_a_c_g_file:
                qag_data=json.load(q_a_c_g_file)
                for qag in qag_data.values():   
                    qag_list.append(qag) 

    with open(cur_dir + "/test_eval_dataset/" + 'test_eval_dataset.json', 'w') as test_eval_dataset:
        json.dump(qag_list, test_eval_dataset, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    client=langfuse_client()
    
    # This list is just for test evaluation usage #
    traceid_list=[
        "1d5eceec-5399-4bc9-9f50-8d8492f5e7eb",
        "3854cc6c-190a-4501-8514-6694aae609fd",
        "303a89c5-a235-477e-b0b1-4258263c8ca7",
        "e5750bea-ad27-43a2-b953-c2822aeedbfc",
        "a0da376c-a1b0-479a-9a84-78033214722c",
        "fc8818db-84ec-4014-a856-ee2b66ea0e6f",
        "1fc2671e-385e-46ec-b06b-d8c3144aaade",
        "cff3a21f-d143-494c-8cff-1754a157b45c",
        "e8e35a2b-d340-4684-bf5b-dcda40f7b77e",
        "12584a5d-152a-4186-8df5-af994a8f721d",
        "43e4de69-080f-4ebe-8031-b607f73fc701",
        "14b09913-43c8-4754-bd63-4a7f95f1dafe",
        "975015bf-3355-492a-8025-abb54715c4af",
        "f33693cf-bf61-430a-842a-976b2c6bf2f1",
        "f21c8ef6-5903-4bc9-b1aa-64ff64fb0eac",
        "dad3b8a7-841d-4588-beca-0293c1c965d6",
        "40141164-acab-4039-a2a9-4a194750c7cc",
        "47500d9c-c188-4415-987f-114fba110709",
        "5cc95b95-ee84-4d8a-85ba-1cbde5ccc9a1",
        "d9f40bee-f27a-456e-a9e0-95c45e0848b2",
        "87355839-2603-4bec-b40a-89468b1ef360",
        "d715e377-cd5a-4e79-84f2-7d185c05d114",
        "80583f40-4b19-4f38-8f9b-7314d09d9f88",
        "5bc29c16-1aa8-4fdd-b7b1-491f84c0a352",
        "727aa02b-28b8-4ee6-b716-505004d35fbd",
        "3884a6e6-ac0c-4d75-9251-4635bce62eab",
        "9f909144-e521-4714-9d58-b4df2e55d56b",
        "1de3d652-003f-4c0c-9b69-2ae7d1964696",
        "08e057ba-55cc-4451-860b-e8f6aab7b21f",
        "121cf4ee-0d16-4164-afea-a06eecee5f97",
        "24d7a2e2-e237-41b2-a0c7-923b3b15ac2c",
    ]
    trace_extract(client=client, traceid_list=traceid_list)
    dataset_to_file()
"""
Use RAGAS framework to evaluate metrics = [
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
] on test_eval_dataset
"""
import json
import os
from datasets import Dataset
import pandas as pd

# component metrics
from ragas.metrics import (
    context_precision,
    answer_relevancy,
    faithfulness,
    context_recall,
)

# end-to-end metrics
from ragas.metrics import (
    answer_similarity,
    answer_correctness
)


from ragas.llms.prompt import Prompt


# Customize the prompt of answer_correctness evaluation
paper_correctness_prompt = Prompt(
    name="paper_correctness_prompt",
    instruction="Extract following from given question and any of given ground truths",
    examples=[
        {
            "question": "What are the baselines outperformed by this work?",
            "answer": "The work proposed in the provided context outperformed two baseline models: TransferTransfo and a hybrid model. The performance was evaluated using both automatic evaluation metrics and human evaluation metrics, showcasing the superiority of the proposed approach over the baselines.",
            "ground_truth": "TransferTransfo and Hybrid",
            'Extracted statements': [
            {
                'statements that are present in both the answer and the ground truth': ["TransferTransfo and a hybrid model"],
                'statements present in the answer but not found in the ground truth': [],
                'relevant statements found in the ground truth but omitted in the answer': [],

            }],
        },
        {
            "question": "How is intent annotated?",
            "answer": "The intent annotation in non-collaborative tasks is designed with a hierarchical approach, separating on-task and off-task intents. On-task intents are specific actions relevant to the task, while off-task intents encompass more general dialog acts. This approach allows for detailed supervision, with a focus on designing task-specific on-task categories and semantic slots, while utilizing common dialog acts for off-task intents.",
            "ground_truth": 
                "using a role-playing task on the Amazon Mechanical Turk platform and collecting typed conversations. Alternative ground truth: Separate on-task and off task intents and annotate on task for data set specific intents, while annotating  off task intents with a fixed set of general intents. \
                    Alternative ground truth: On-task dialog are annotated as on-task intents , the other dialog are annotated as pre-defined off-task intents.",  
            
            'Extracted statements': [
            {
                'statements that are present in both the answer and the ground truth': [
                    "on-task and off-task"
                ],
                'statements present in the answer but not found in the ground truth': [
                ],
                'relevant statements found in the ground truth but omitted in the answer': [
                    "Amazon Mechanical Turk platform", 
                ],

            }],
        },
    ],
    input_keys=['question', 'answer', 'ground_truth'],
    output_key='Extracted statements',
    output_type='json',
    language='english'
)

answer_correctness.correctness_prompt = paper_correctness_prompt


from langchain_openai.chat_models import AzureChatOpenAI
from langchain_openai.embeddings import AzureOpenAIEmbeddings
# from ragas.embeddings import HuggingfaceEmbeddings
from ragas import evaluate




def gptutor_component_eval():
    component_metrics = [
        faithfulness,
        answer_relevancy,
        context_recall,
        context_precision
    ]
    print("The result of gptutor model on component evaluation is: ")
    eval(metrics=component_metrics, dataset_json_path ='./test_eval_dataset/test_eval_dataset.json', 
         result_csv_path = './test_eval_dataset/test_eval_component_result.csv')

def gptutor_endToend_eval():
    endToend_metrics = [
        answer_similarity,
        answer_correctness
    ] 
    print("The result of gptutor model on end-to-end evaluation is: ")
    eval(metrics=endToend_metrics, dataset_json_path ='./test_eval_dataset/test_eval_dataset.json', 
         result_csv_path = './test_eval_dataset/test_eval_endToend_result.csv')


def baseline_endToend_eval():
    endToend_metrics = [
        answer_similarity,
        answer_correctness
    ]    
    print("The result of baseline model on end-to-end evaluation is: ")
    eval (metrics=endToend_metrics, dataset_json_path ='./test_eval_dataset/test_eval_baseline.json', 
         result_csv_path = './test_eval_dataset/test_eval_baseline_result.csv')
    



def eval(metrics, dataset_json_path, result_csv_path):
    



    azure_configs={
        "chat_base_url": os.getenv("AZURE_OPENAI_GPT_BASE_URL"),
        "chat_deployment": os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT_NAME"),
        "chat_name": "gpt-35-turbo",
        "chat_version": os.getenv("AZURE_OPENAI_GPT_API_VERSION"),
        "embedding_base_url": os.getenv("AZURE_OPENAI_EMBEDDING_BASE_URL"),
        "embedding_deployment": os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
        "embedding_name": "text-embedding-ada-002",
        "embedding_version": os.getenv("AZURE_OPENAI_EMBEDDING_API_VERSION")
    }

    # Chat model
    os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_GPT_API_KEY")
    azure_model = AzureChatOpenAI(
        openai_api_version=azure_configs["chat_version"],
        azure_endpoint=azure_configs["chat_base_url"],
        azure_deployment=azure_configs["chat_deployment"],
        model=azure_configs["chat_name"],
        validate_base_url=False,
    )
    print(azure_model)

    # Embedding model
    os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_EMBEDDING_API_KEY")
    azure_embeddings = AzureOpenAIEmbeddings(
        openai_api_version=azure_configs["embedding_version"],
        azure_endpoint=azure_configs["embedding_base_url"],
        azure_deployment=azure_configs["embedding_deployment"],
        model=azure_configs["embedding_name"],
    )
    print(azure_embeddings)


  

    with open (dataset_json_path, 'r') as dataset:
        qasper_dataset=json.load(dataset)
        dataframe = Dataset.from_pandas(pd.DataFrame(data=qasper_dataset))
        print(dataframe)
        
        result = evaluate(dataframe, metrics=metrics, llm=azure_model, embeddings=azure_embeddings)

    print(result)

    df = result.to_pandas()
    print(df.head())
    df.to_csv(result_csv_path, sep=',', index=False, encoding='utf-8')

if __name__ == '__main__':
    baseline_endToend_eval()
    gptutor_endToend_eval()
import json
import os
from fpdf import FPDF

cur_dir = os.path.dirname(__file__)

def read_json():
    
    with open(cur_dir + '/qasper-test-v0.3.json') as data_file:    
        data = json.load(data_file)
        doc_counter = 0
        qag_pairs_counter = 0
        # test first five papers and related questions and ground_truth
        for v in data.values():
            valid_flag = False
           
            title = v['title']
            abstract = v['abstract']
            full_text = v['full_text']
            dir_path = cur_dir + "/normalized_dataset/"+ title.replace('/', ' ')
            os.mkdir(dir_path)
            doc_path = dir_path + "/" + title.replace('/', ' ') + ".pdf"
            write_toPDF(title, abstract, full_text, doc_path)

            #question and ground_truth file path
            qag_path = dir_path + "/" + title.replace('/', ' ') + ".json"
            
            #list of question and groun_truth
            qas = v['qas']
            valid_flag, qag_pairs = extract_questions_groundtruths(qag_path, qas)
            qag_pairs_counter+=qag_pairs

            #if the QA pairs is invalid (i.e., there is no valid ground_truth for corresponding questions), 
            #remove the paper PDF, and empty qag json file, and empty folder, then update counter
            if valid_flag == False:
                os.remove(doc_path)
                os.remove(qag_path) 
                os.rmdir(dir_path)
            
            else:
                doc_counter +=1
            
        print("There are {} valid (documents, questions, ground_truth) tuples in total created from the test dataset.\n".format(doc_counter) )
        print("There are {} valid (question, ground_truth) pairs in total\n".format(qag_pairs_counter))
# prepare the documents
def write_toPDF(title, abstract, full_text, path):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Arial", "", fname = cur_dir + '/fonts/Arial Unicode.ttf')
    pdf.set_font("Arial", "", size = 12)
    pdf.multi_cell(200, 10, text = title + "\n", align = 'C')
    pdf.multi_cell(200, 10, text = "Abstract" +  "\n", align = 'C')
    pdf.multi_cell(200, 10, text = abstract + "\n", align = 'L')

    for sections in full_text:
        # in case null section_name
        try:
            section_name = sections["section_name"] + "\n"  
        except TypeError:
            pdf.multi_cell(200, 10, text = "\n", align = 'L')
        else: 
            pdf.multi_cell(200, 10, text = section_name, align = 'L')

        for paragraphs in sections["paragraphs"]:
            pdf.multi_cell(200, 10, text = paragraphs +  "\n", align = 'L')
    
    pdf.output(path)


# prepare the question and ground_truth pairs 
def extract_questions_groundtruths(path, qas):
   
    with open(path, 'w', encoding='utf-8') as f:

        #only take the first three QA pairs
        pair_counter = 0
        for pair in qas:
            if (pair_counter > 3):
                break
            
            # init the question and ground_truth dictionary
            qag_dict={}

            qag_dict["question"] = pair.get("question")
            #json.dump(pair["question"], f)
            
            answers = pair["answers"]
            # Take the first valid (answerable and word counts less than 300 words) 
            # free_form_answer (annotated by experts based on evidence) as ground_truth


            ground_truth_flag = False
            for instance in answers:
                answer = instance["answer"]

                unanswerable_flag = answer["unanswerable"]
                ground_truth = answer.get("free_form_answer")
                
                if unanswerable_flag == False and ground_truth!="":
                    qag_dict["ground_truth"] = ground_truth
                    # json.dump(answer["highlighted_evidence"], f)
                    ground_truth_flag = True
                    break
            
            if ground_truth_flag == True:
                json.dump(qag_dict, f, ensure_ascii=False, indent = 4)
                pair_counter+=1

    return (ground_truth_flag, pair_counter)
if __name__ == '__main__':
    read_json()



   
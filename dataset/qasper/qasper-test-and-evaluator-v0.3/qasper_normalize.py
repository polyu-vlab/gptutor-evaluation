import json
import os
from fpdf import FPDF

cur_dir = os.path.dirname(__file__)

def read_json():
    
    with open(cur_dir + '/qasper-test-v0.3.json') as data_file:    
        
        data = json.load(data_file)
        doc_amount_counter = 0
        qag_pairs_amount_counter = 0
        # test first five papers and related questions and ground_truth
        for v in data.values():
            if doc_amount_counter>=13:
                break
            '''  
        # use the following constrain for testing the first 3 papers  
            if doc_amount_counter>=1:
                break
            '''
            valid_flag = False
           
            title = v['title']
            abstract = v['abstract']
            full_text = v['full_text']

            # The formal evaluation should elete the path "test"
            dir_path = cur_dir + "/test_eval_dataset/"+ "test_papers/" + title.replace('/', ' ')
            os.mkdir(dir_path)
            doc_path = dir_path + "/" + title.replace('/', ' ') + ".pdf"
            write_toPDF(title, abstract, full_text, doc_path)

            #question and ground_truth file path
            qag_path = dir_path + "/" + title.replace('/', ' ') + ".json"
            
            #list of question and groun_truth
            qas = v['qas']
            valid_flag, qag_dict, qag_pairs_counter = extract_questions_groundtruths(qas)
            

            #if the QA pairs is invalid (i.e., there is no valid ground_truth for corresponding questions), 
            #remove the paper PDF, and empty qag json file, and empty folder, then update counter
            if valid_flag == False:
                os.remove(doc_path)
                # os.remove(qag_path) 
                os.rmdir(dir_path)
            
            else:
                
                doc_amount_counter += 1
                write_tojson(path=qag_path, content=qag_dict, metadata= qag_pairs_amount_counter)
                qag_pairs_amount_counter += qag_pairs_counter

        print("There are {} valid (documents, questions, ground_truth) tuples in total created from the test dataset.\n".format(doc_amount_counter) )
        print("There are {} valid (question, ground_truth) pairs in total\n".format(qag_pairs_amount_counter))

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
def extract_questions_groundtruths(qas):
   
    

    #only take the first three QA pairs
    pair_counter = 0
    qag_dict={}
    for pair in qas:
        if (pair_counter > 3):
            break
        
        # init the question and ground_truth dictionary
        qag={}

        qag["question"] = pair.get("question")
        #json.dump(pair["question"], f)
        
        answers = pair["answers"]
        # Take the first valid (answerable and word counts less than 300 words) 
        # extract no more than 3 free_form_answer (annotated by experts based on evidence) as ground_truth list []

        # ground_truth_flag represents whether there exists any valid ground_truth for the given question
        ground_truth_flag = False
        # ground_truth_counter calculates the number of valid ground_truth, no more than 3
        ground_truth_counter = 0
        ground_truth_list=[]
        for instance in answers:
            if ground_truth_counter>=3:
                break

            answer = instance["answer"]

            unanswerable_flag = answer["unanswerable"]
            
            free_form_answer = answer.get("free_form_answer")
            highlighted_evidence = answer.get("highlighted_evidence")

            if unanswerable_flag == False:
                if free_form_answer!="":
                    ground_truth_list.append(free_form_answer)
                    # json.dump(answer["highlighted_evidence"], f)

                # if there is no free_form answer and ground_truth less than 3,
                # add the corresponding highlighted_evidence (length shorter than 400 characters) as one ground_truth
                elif (ground_truth_counter < 3) and (sum(len(s) for s in highlighted_evidence) < 400):
                    ground_truth_list.extend(highlighted_evidence)
                
                else: 
                    continue
                ground_truth_flag = True
                ground_truth_counter += 1
        
        qag["ground_truth"] = '. Alternative ground truth: '.join(ground_truth_list)

        if ground_truth_flag == True:
            pair_counter+=1

            #This dictionary key format is the qa# within the file 
            #But this will be updated when it is written to json file
            qag_dict["QA"+str(pair_counter)]=qag   
    
        
    return (ground_truth_flag, qag_dict, pair_counter)

def write_tojson(path, content, metadata):
    with open(path, 'w', encoding='utf-8') as f:
        for oldid in list(content):
            newid="TestEvalQA" + str(metadata)
            content[newid] = content.pop(oldid)
            metadata+=1
        json.dump(content, f, ensure_ascii=False, indent = 4)




def title_list():
    with open(cur_dir + '/qasper-test-v0.3.json') as data_file:    
        with open(cur_dir + '/title_index.txt', 'w') as title_file:
            data = json.load(data_file)
            
            # test first five papers and related questions and ground_truth
            for v in data.values():
                title_file.write(v["title"] + "\n")

           
        

if __name__ == '__main__':
    #title_list()
    read_json()



   
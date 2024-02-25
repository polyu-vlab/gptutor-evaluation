# Working flow: Create a course -> upload assets -> create chat element with one document selected -> create  conversations for each question within one chat element

import os 
import asyncio
import json
import requests
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from util.auth import fetchAccessToken

cur_dir = os.path.dirname(__file__)


def mutation_create_course():
    
    mutation = '''
            mutation create_Course{
                createCourse (values: {
                  name: "Evaluation",
                  code: "EVAL1001",
                  color: "blue",
                  icon: "NA"
                }) {
                  id
                  name
                  code 
                  expiryTimestamp
                }
              }
            '''
    return mutation

def query_generateUploadProfiles(file_names_path):
    courseID=''
    file_list = []
    with open ('./course/courseDTO.json', 'r') as course:
        courseID=json.load(course)["course"]["id"]
    query = '''
      query generateUploadProfiles($file_list: [String!]!){{
        generateUploadProfiles (
          fileNames: $file_list,
          courseId: "{_courseID}"
        ){{
            postURL
            formData
        }}
      }}
  
    '''.format(_courseID=courseID)
   
    with open (file_names_path, 'r') as papers:
        for p in papers.readlines():
            file_list.append(p.split('\n')[0])
    return (query, file_list)

def query_courseAssets():
    courseID=''
    with open ('./course/courseDTO.json', 'r') as course:
        courseID=json.load(course)["course"]["id"]

    query = '''
      query getCourseAssets{{
        courseAssets(courseId: "{_courseID}"){{
            id
            name
        }}
      }}
    '''.format(_courseID=courseID)

    return query


def query_course():
    courseID=''
    with open ('./course/courseDTO.json', 'r') as course:
        courseID=json.load(course)["course"]["id"]
    
    query = '''\
      query getCourse{{
        course(keyword: "{id}") {{
          id
          name
          code 
          description
          color
          icon
          expiryTimestamp
          creatorId
        }}
      }}\
      '''.format(id=courseID)
    return query

def uploadAssets(assetsPresignedURLfile):
    AccessToken = fetchAccessToken()
    with open(assetsPresignedURLfile, 'r') as uploadInfo:
        upload_list = list(json.load(uploadInfo).values())[0]

        for info in upload_list:
            url = info["postURL"]
            formdata = info["formData"]
            fileName = formdata["x-amz-meta-fileName"]
            file = {"file": open("{cur_dir}/../dataset/qasper/qasper-test-and-evaluator-v0.3/test_eval_dataset/test_papers/{fileName}/{fileName}.pdf".format(cur_dir=cur_dir, fileName=fileName),'rb')}
            result = requests.post(url, files=file, data=formdata)
            print(result.text)
            print("Successfully upload: ", fileName)

# create modules for each paper
def createChatElement():
    pass

# create a conversation for each question
def createConversation():
    pass

async def main():
    # listen to 3001 port of localhost after running pnpm start in gptutor-backend 
    gptutor_backend_endpoint = "http://0.0.0.0:3001/graphql"

    AccessToken=fetchAccessToken()
    
    transport = AIOHTTPTransport(
      url=gptutor_backend_endpoint,
      headers={'Authorization': f"Bearer {AccessToken}"}
    )   
    # Using `async with` on the client will start a connection on the transport
    # and provide a `session` variable to execute queries on this connection
    async with Client(
        transport=transport,
        fetch_schema_from_transport=True,
    ) as session:

        '''
        # Execute single mutation
        file_names_path = cur_dir + '/../dataset/qasper/qasper-test-and-evaluator-v0.3/test_eval_dataset/test_eval_index.txt'
        query_text, variable_list = query_generateUploadProfiles(file_names_path)
        
        query = gql(
            query_text
        )

        filenames = {
          'file_list': variable_list
        }
        result = await session.execute(query, variable_values=filenames)
        with open('./assets/assetsPresignedUrl.json', 'w') as f:
            json.dump(result, f, indent=2)
        print(result)
        '''
        query_text = query_courseAssets()
        query = gql(
            query_text
        )
        result = await session.execute(query)
        print(result)
        
        

#uploadProfilesFilePath="{cur_dir}/assets/assetsPresignedUrl.json".format(cur_dir=cur_dir)
#uploadAssets(uploadProfilesFilePath)
asyncio.run(main())
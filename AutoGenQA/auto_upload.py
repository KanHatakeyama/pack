import pandas as pd
import json
import copy
import glob
from src.clean_records import clean_question
from huggingface_hub import HfApi, logging
import os
import time
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

def upload():
    jsonl_path_list=glob.glob('data/*.jsonl')

    all_records=[]
    for jsonl_path in jsonl_path_list:
        with open(jsonl_path) as f:
            for line in f:
                record=json.loads(line)
                all_records.append(record)

    original_record=all_records[0]
    cleaned_records=[]

    for original_record in all_records:
        record={}
        record["question"]=clean_question(original_record["question"])
        if "answer_1" not in original_record:
            original_record["answer_1"]=""

        if "ans0" in original_record:
            record["answer_0"]=original_record["ans0"]
            record["answer_1"]=original_record["ans1"]
        elif "answer_0" in original_record:
            record["answer_0"]=original_record["answer_0"]
            record["answer_1"]=original_record["answer_1"]
        else:
            print("no answer found",record)
        
        if "database" in original_record:
            record["database"]=original_record["database"]
        else:
            record["database"]="misc"

        #2つの回答について､それぞれ別に登録する
        r1=copy.deepcopy(record)
        r1["answer"]=r1["answer_0"]
        r1.pop("answer_0")
        r1.pop("answer_1") 
        cleaned_records.append(r1)

        r2=copy.deepcopy(record)
        r2["answer"]=str(r2["answer_1"])
        r2.pop("answer_0")
        r2.pop("answer_1") 
        if len(r2["answer"])>2:
            cleaned_records.append(r2)


    #アノテーションデータの読み込み
    qa_path="hf/qa.jsonl"
    if os.path.exists(qa_path):
        qa_to_score={}
        with open(qa_path,"r") as f:
            for line in f:
                r=json.loads(line)
                qa=r["qa"]
                score=r["score"]
                qa_to_score[qa]=float(score)

    for record in cleaned_records:
        q=record["question"]
        a=record["answer"]
        qa=str(q)+str(a)

        if qa in qa_to_score:
            record["score"]=float(qa_to_score[qa])
        else:
            record["score"]=-2


    df=pd.DataFrame(cleaned_records)
    #シャッフル
    #df=df.sample(frac=1).reset_index(drop=True)
    parquet_path="hf/cleaned_data.parquet"
    df.to_parquet(parquet_path)
    df.to_csv("hf/cleaned_data.csv")



    logging.set_verbosity_debug()
    hf = HfApi()
    hf.upload_file(path_or_fileobj=parquet_path,
                    path_in_repo=f"1.parquet",
                    repo_id="hatakeyama-llm-team/AutoGeneratedJapaneseQA", repo_type="dataset")





if __name__ == "__main__":
    while True:
        try:
            upload()
            print("uploaded")
            time.sleep(3600*3)
        except Exception as e:
            print("error",e)
            time.sleep(600)


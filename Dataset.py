# Dataset is downloaded thanks to The HuggingFace Datasets Authors and the current dataset script contributor, Copyright 2020.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
import datasets
import pandas as pd
import replicate
import json
import os

#Dataset information to be contained in the dataset when it is loaded
_CITATION = """\
@article{hendryckstest2021,
  title={Measuring Massive Multitask Language Understanding},
  author={Dan Hendrycks and Collin Burns and Steven Basart and Andy Zou and Mantas Mazeika and Dawn Song and Jacob Steinhardt},
  journal={Proceedings of the International Conference on Learning Representations (ICLR)},
  year={2021}
}
"""

_DESCRIPTION = """\
Measuring Massive Multitask Language Understanding by Dan Hendrycks, Collin Burns, Steven Basart, Andy Zou, Mantas Mazeika, Dawn Song, and Jacob Steinhardt (ICLR 2021).
"""

_HOMEPAGE = "https://github.com/hendrycks/test"

_LICENSE = "MIT"

_URL = "https://people.eecs.berkeley.edu/~hendrycks/data.tar"

DEFAULT_PROMPT = "{\\SYS An intelligently concise assistant, you reply only with a 'The correct answer is:' followed letter from the set {A., B., C., D.}: {\SYS REPLY WITH ONLY THE STRING 'The correct answer is: ' FOLLOWED BY THE CORRECT ANSWER's LETTER, LIKE SO: 'The correct answer is: B.'} No need to reply with multiple words or explain your reasoning!\n"

#List of all 57 topics for the model to be analyzed on
task_list = [
    "high_school_european_history",
    "business_ethics",
    "clinical_knowledge",
    "medical_genetics",
    "high_school_us_history",
    "high_school_physics",
    "high_school_world_history",
    "virology",
    "high_school_microeconomics",
    "econometrics",
    "college_computer_science",
    "high_school_biology",
    "abstract_algebra",
    "professional_accounting",
    "philosophy",
    "professional_medicine",
    "nutrition",
    "global_facts",
    "machine_learning",
    "security_studies",
    "public_relations",
    "professional_psychology",
    "prehistory",
    "anatomy",
    "human_sexuality",
    "college_medicine",
    "high_school_government_and_politics",
    "college_chemistry",
    "logical_fallacies",
    "high_school_geography",
    "elementary_mathematics",
    "human_aging",
    "college_mathematics",
    "high_school_psychology",
    "formal_logic",
    "high_school_statistics",
    "international_law",
    "high_school_mathematics",
    "high_school_computer_science",
    "conceptual_physics",
    "miscellaneous",
    "high_school_chemistry",
    "marketing",
    "professional_law",
    "management",
    "college_physics",
    "jurisprudence",
    "world_religions",
    "sociology",
    "us_foreign_policy",
    "high_school_macroeconomics",
    "computer_security",
    "moral_scenarios",
    "moral_disputes",
    "electrical_engineering",
    "astronomy",
    "college_biology",
]

# List of categories which performed better on one shot do to high failure rate on five shot
one_shot_list = [
    "professional_law",
    "high_school_computer_science",
    "high_school_statistics",
    "security_studies",
    "professional_medicine",
    "college_computer_science",
    "high_school_world_history",
    "high_school_us_history",
    "high_school_european_history"
]

# List of categories which handled five shot learning well
five_shot_list = [
    "business_ethics",
    "clinical_knowledge",
    "medical_genetics",
    "high_school_physics",
    "virology",
    "high_school_microeconomics",
    "econometrics",
    "high_school_biology",
    "abstract_algebra",
    "professional_accounting",
    "philosophy",
    "nutrition",
    "global_facts",
    "machine_learning",
    "public_relations",
    "professional_psychology",
    "prehistory",
    "anatomy",
    "human_sexuality",
    "college_medicine",
    "high_school_government_and_politics",
    "college_chemistry",
    "logical_fallacies",
    "high_school_geography",
    "elementary_mathematics",
    "human_aging",
    "college_mathematics",
    "high_school_psychology",
    "formal_logic",
    "international_law",
    "high_school_mathematics",
    "conceptual_physics",
    "miscellaneous",
    "high_school_chemistry",
    "marketing",
    "management",
    "college_physics",
    "jurisprudence",
    "world_religions",
    "sociology",
    "us_foreign_policy",
    "high_school_macroeconomics",
    "computer_security",
    "moral_scenarios",
    "moral_disputes",
    "electrical_engineering",
    "astronomy",
    "college_biology",
]


# MMLU Dataset Download with HuggingFace datasets library
class MMLUConfig(datasets.BuilderConfig):
    def __init__(self, **kwargs):
        super().__init__(version=datasets.Version("1.0.0"), **kwargs)


class MMLU(datasets.GeneratorBasedBuilder):
    BUILDER_CONFIGS = [
        MMLUConfig(
            name=task_name,
        )
        for task_name in task_list
    ]

    def _info(self):
        features = datasets.Features(
            {
                "input": datasets.Value("string"),
                "A": datasets.Value("string"),
                "B": datasets.Value("string"),
                "C": datasets.Value("string"),
                "D": datasets.Value("string"),
                "target": datasets.Value("string"),
            }
        )
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=features,
            homepage=_HOMEPAGE,
            license=_LICENSE,
            citation=_CITATION,
        )
    #
    def _split_generators(self, dl_manager):
        data_dir = dl_manager.download_and_extract(_URL)
        task_name = self.config.name
        return [
            datasets.SplitGenerator(
                name=datasets.Split.TEST,
                gen_kwargs={
                    "filepath": os.path.join(
                        data_dir, "data", "test", f"{task_name}_test.csv"
                    ),
                },
            ),
            datasets.SplitGenerator(
                name=datasets.Split.VALIDATION,
                gen_kwargs={
                    "filepath": os.path.join(
                        data_dir, "data", "val", f"{task_name}_val.csv"
                    ),
                },
            ),
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={
                    "filepath": os.path.join(
                        data_dir, "data", "dev", f"{task_name}_dev.csv"
                    ),
                },
            ),
        ]

    def _generate_examples(self, filepath):
        df = pd.read_csv(filepath, header=None)
        df.columns = ["input", "A", "B", "C", "D", "target"]

        for i, instance in enumerate(df.to_dict(orient="records")):
            yield i, instance



def check_validity(token:str, prompt:str=DEFAULT_PROMPT, shots:int=1, validation_num:int=5):
    """
    Print Llama response on validation_num validation questions for each category - if question does not contain valid answer, 
    return tag name.
    This allows for easy checking of which category of question the model does not handle well with a particular prompt style.  
    Args:
        token: your REPLICATE_API_TOKEN
        prompt: text to go between the example questions and the final question in the prompt sent to Llama.
        shots: Number of shots (question answer examples before final)
        validation_num: Number of queries for each topic in task_list
    """
    api = replicate.Client(api_token=token)    

    for tag in task_list:
        dataset = datasets.load_dataset("lukaemon/mmlu", tag, trust_remote_code=True)
        train_data = dataset["train"]
        test_data = dataset["test"]
        prompt3 = ""
        for example in train_data.select(range(shots)):
            prompt3+=("User: I have a question: " + example["input"] + "\n\nChoices:\n")
            prompt3+=("A. " + example["A"] + "\n")
            prompt3+=("B. " + example["B"] + "\n" )
            prompt3+=("C. " + example["C"] + "\n")
            prompt3+=("D. " + example["D"] + "\n\n")
            prompt3+=("Assistant: The correct answer is: " + example["target"] + ".\n\n")

        for test in test_data.select(range(validation_num)): 
            prompt2 = ""
            prompt2+=("User: I have a question: " + test["input"] + "\n\nChoices:\n")
            prompt2+=("A. " + test["A"] + "\n")
            prompt2+=("B. " + test["B"] + "\n")
            prompt2+=("C. " + test["C"] + "\n")
            prompt2+=("D. " + test["D"] + "\n\n")
            prompt2+=("Assistant:" + "\n")
            output=""
            output=""
            for event in api.stream(
                "meta/meta-llama-3-8b-instruct",
                input={
                    "top_k": 0,
                    "top_p": 0.9,
                    "prompt": prompt3+ prompt + prompt2 + prompt,
                    "temperature": 0,
                    "system_prompt": "You are a smart, concise, assistant",
                    "length_penalty": 1,
                    "max_new_tokens": 100,
                    "stop_sequences": "<|end_of_text|>,<|eot_id|>",
                    "prompt_template": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are a helpful assistant<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
                    "presence_penalty": 0
                },
            ):
                output+=(str(event))
            if ("A." not in output) and ("B." not in output) and ("C." not in output) and ("D." not in output):
                print(tag)
            print("\n=================================\n")

def get_acc_n_shot(token:str, topic:str, prompt=DEFAULT_PROMPT, n:int=0, output:str=f"n_shot_results.jsonl"):
    """
    Prompt on n questions for a given category. 
    Args:
        
        prompt: text to go between the example questions and the final question in the prompt sent to Llama.
        n: number of shots
        output: .jsonl filepath to write results to 
    """
    api = replicate.Client(api_token=token)

    fails = 0
    correct = 0
    total = 0

    dataset = datasets.load_dataset("lukaemon/mmlu", topic, trust_remote_code=True)
    train_data = dataset["train"]
    test_data = dataset["test"]
    prompt3 = ""

    for example in train_data.select(range(n)):
        prompt3+=("User: I have a question: " + example["input"] + "\n\nChoices:\n")
        prompt3+=("A. " + example["A"] + "\n")
        prompt3+=("B. " + example["B"] + "\n" )
        prompt3+=("C. " + example["C"] + "\n")
        prompt3+=("D. " + example["D"] + "\n\n")
        prompt3+=("Assistant: The correct answer is: " + example["target"] + ".\n\n")

    for test in test_data: 
        prompt2 = ""
        prompt2+=("User: I have a question: " + test["input"] + "\n\nChoices:\n")
        prompt2+=("A. " + test["A"] + "\n")
        prompt2+=("B. " + test["B"] + "\n")
        prompt2+=("C. " + test["C"] + "\n")
        prompt2+=("D. " + test["D"] + "\n\n")
        prompt2+=("Assistant:" + "\n")
        output=""

        for event in api.stream(
            "meta/meta-llama-3-8b-instruct",
            input={
                "top_k": 0,
                "top_p": 0.9,
                "prompt": prompt3 + prompt + prompt2,
                "temperature": 0.0,
                "system_prompt": "You are a smart, concise, assistant",
                "length_penalty": 1,
                "max_new_tokens": 100,
                "stop_sequences": "<|end_of_text|>,<|eot_id|>",
                "prompt_template": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are a helpful assistant<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
                "presence_penalty": 0
            },
        ):
            output+=(str(event))
        
        if all(choice not in output for choice in ["A.", "B.", "C.", "D.", "A!", "B!", "C!", "D!"]):
            fails += 1
            print(output)
        if (f"{test['target']}." in output) or (f"{test['target']}:" in output) or (f"{test['target']}!" in output):
            correct += 1
        total+=1
    
    # Create dictionary with the topic, number of fails, number of correct answers, and total attempts per topic
    result = {
        "topic": topic,
        "fails": fails,
        "correct": correct,
        "total": total
    }

    # Write to JSONL file
    with open(output, "a") as file:
        json.dump(result, file)
        file.write("\n")

    
**PRIMARY RESULTS**:

Final MMLU results (see .pngs and notebook for topic/category specific): 
||Meta|Me|
|--------|-----|----|
|micro|67.4|60.3|
|macro|68.4|61.2|

Overall, given that prompt engineering can have a large effect on accuracy, and Replicate API + Meta's not so openness did not allow for me to exactly follow their method, I think it is very feasible that they were able to get Llama-8b-instruct to output a score as high as it did. 

For the instruct-aligned models, we use a dialogue prompt (user/assistant) for the shots and ask the model to generate the best choice character as answer.

A pivotal difference between mine and Meta's evaluation is how accuracy is evaluated - typically, MMLU is evaluated based off the probabilities (or log probabilites) outputted by the model, and just argmaxed over {A, B, C, D}. Unfortunately, the Replicate API does not output probabilities for Llama-3 as of right now, but there are reasonable workarounds. By setting the temperature to $0$, we know that the output is the most probable and randomness won't make it more wrong, and we prompt the AI very heavily to follow a specific answer format containing the correct letter followed by a . or ! or :, as so: "B!/B./B:". We also record the number of responses which do not include a valid answer, of which there are zero for most categories and generally very few, and record them as fails, then give them a .25 correctness value since even a misformatted answer which reflects no understanding by the model would be scored at least random when taking the next token probabilites over 4 possible tokens. Note that even if all fails were completely correct or completely wrong, this would contain a range of MMLU scores of only ~2.

**More Info (optional)**:

From Llama, we have the following information about their evals:
The pre-trained models are evaluated in the standard way by calualting the likelihood of each choice character. For the instruct-aligned models, we use a dialogue prompt (user/assistant) for the shots and ask the model to generate the best choice character as answer.

The MMLU dataset is split into 4 categories, each with several subcategories, each with several subtopics, for a total of $57$ topics.

Meta shared the following MMLU results for Llama-3-8b-instruct: 67.4% for micro average (average across topics), and 68.4% for macro average (average across category). 
They also say: "For all the evaluations, we use our internal evaluations library. For details on the methodology see [here](https://github.com/meta-llama/llama3/blob/main/eval_methodology.md)", but the eval_methodology file does not exist and the eval_details file in that same repository lacks specifics. This is our first real challenge - prompt engineering has a huge effect on a model's score on MMLU. See [here](https://huggingface.co/blog/open-llm-leaderboard-mmlu) for more info on this; the long and short of it is that small differences in how prompts are formatted can have 15 point swings on a model's score, and Meta surely spent long hours engineering the perfect prompts to maximize MMLU. In the code here, I employ a user/assistant prompt strategy that does fairly well but not as well as Meta's reported number (I got 60.3% and 61.2% micro and macro accuracies respectively). Prior, similar prompts were doing as poorly as 45%, and I am sure that brave prompt engineers can improve on the number I get here by modifying the prompting strategy. 

We used $5$-shot evaluation (same as Meta) on $48$ of the topics, and $1$-shot on $9$ of them, the ones which had an extremely high failure rate (~40%) for $5$-shot. Running identical $5$-shot prompts through [Replicate](https://replicate.com/meta/meta-llama-3-8b-instruct) and [HuggingFace](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct) API's yielded very legible results with a proper answer in the latter, but bugs the former as you can see below, even in the websites. I do not know why.

Here is an example of a failing $5$-shot response:

You are a problem about the "I have been to create a new assistance to a new assistant in the assistant to help you are a help a new assistant you about a request a new assistant assistant at a Help of the assistant the help you are a new assistant in the following a you are the following a a new assistant by a state of a state a you a a you can you are a state of a state the assistance of a assistant aassistant a help a user a help a assistant assistant a




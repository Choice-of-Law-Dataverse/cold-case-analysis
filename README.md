# Developing a Large Language Model for Swiss Cases on Choice of Law
- [Website](https://www.cold.global/) to learn more about our main research project
- [Presentation slides (PDF)](/5_IPR_Nachwuchstagung/presentation_slides.pdf)
- [Handout (PDF)](/5_IPR_Nachwuchstagung/handout.pdf)

## Documentation
- **[📋 Architecture & Data Flow](docs/ARCHITECTURE.md)** - Comprehensive system documentation with diagrams
- **[🔄 Workflows & Processes](docs/WORKFLOWS.md)** - Detailed workflow diagrams and data flow patterns
- **[🤖 Agent Workflow](docs/agent.md)** - LangGraph agent implementation details

## Overview
- [What is the Case Analyzer?](#what-is-the-case-analyzer)
- [How to run the Case Analyzer on your machine](#how-to-run-the-case-analyzer-on-your-machine)
- [Data](#data)
    - [Court Cases](#court-cases)
    - [Ground Truth](#ground-truth)
- [Prompts](#prompts)
- [Results](#results)
- [What is the Choice of Law Dataverse (CoLD)?](#what-is-the-choice-of-law-dataverse-cold)

## What is the Case Analyzer?
The Case Analyzer is an automated tool for analyzing court decisions concerning choice of law in international commercial contracts. For each decision, the analysis focuses on the following categories:

| Category | Description | Task |
| :-- | :-- | :-- |
| Abstract | Official abstract of the decision | Extraction |
| Relevant Facts | Concise summary of case facts emphasizing PIL aspects | Extraction/Summarization |
| PIL Provisions | Relevant legal provisions related to the choice-of-law issue | Extraction |
| PIL Theme | Subtopic related to party autonomy | Extraction |
| Choice-of-law Issue | Description of the PIL problem of the case | Classification → Interpretation |
| Court’s Position | Brief overview of the ruling regarding the PIL issue | Extraction/Interpretation |

## How to run the Case Analyzer on your machine
1. Create a file for API secrets under ".env". Use the blueprint.env file for reference
2. Prepare the dataset under "cold_case_analyzer/data/cases.xlsx". Please note that you have to adhere to the given format with the pre-defined column names*
3. (Optional) Create a new virtual environment using `python -m venv .venv`
4. Install dependencies using `pip install -r requirements.txt`
5. Run the case analyzer using `python cold_case_analyzer/main.py`

\* Disclaimer note: It is still necessary to include a separate column with the "Quote"/the Choice of Law section of the original case text. We aim to make this column obsolete soon.

## Data

### Court Cases
The initial iteration of the Case Analyzer was developed using a dataset of 33 Swiss court decisions. Below is an overview of the cases included:

| **Nr.** | **Title** | **Year** | **Language** |
| :-- | :-- | :-- | :-- |
| 1 | [BGE 131 III 289](https://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F131-III-289%3Ade&lang=de&type=show_document) | 2005 | German |
| 2 | [BGE 81 II 175](https://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F81-II-175%3Ade&lang=de&type=show_document) | 1955 | German |
| 3 | [BGE 78 II 74](https://entscheide.weblaw.ch/dumppdf.php?link=BGE-78-II-74) | 1952 | French |
| 4 | [BGE 138 III 750](https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F138-III-750%3Ade&lang=de&type=show_document) | 2012 | French |
| 5 | [BGer 4A 264/2008](https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza%3A%2F%2F23-09-2008-4A_264-2008&lang=de&type=show_document) | 2008 | French |
| 6 | [BGE 138 III 489](https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F138-III-489%3Ade&lang=de&type=show_document) | 2012 | German |
| 7 | [BGer 4C.168/2006](https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza%3A%2F%2F11-09-2006-4C-168-2006&lang=de&type=show_document) | 2006 | German |
| 8 | [BGE 123 III 35](https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F123-III-35%3Ade&lang=de&type=show_document) | 1996 | German |
| 9 | [BGer 4A 394/2009](https://www.bger.ch/ext/eurospider/live/fr/php/aza/http/index.php?highlight_docid=aza://04-12-2009-4A_394-2009&lang=de&type=show_document) | 2009 | French |
| 10 | [BGE 128 III 201](https://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F128-III-201%3Ade&lang=de&type=show_document) | 2002 | German |
| 11 | [BGE 132 III 285](https://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F132-III-285%3Afr&lang=fr&type=show_document) | 2005 | German |
| 12 | [BGE 119 II 173](https://www.bger.ch/ext/eurospider/live/fr/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F119-II-173%3Afr&lang=fr&type=show_document) | 1993 | German |
| 13 | [BGE 130 III 620](https://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F130-III-620%3Ade&lang=de&type=show_document) | 2004 | German |
| 14 | [BGE 136 III 392](https://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F136-III-392%3Ade&lang=de&type=show_document) | 2010 | French |
| 15 | [BGer 4C.54/2000](https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza%3A%2F%2F19-01-2001-4C-54-2000&lang=de&type=show_document) | 2001 | French |
| 16 | [BGer 5C.68/2002](https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza%3A%2F%2F25-04-2002-5C-68-2002&lang=de&type=show_document) | 2002 | German |
| 17 | [BGE 111 II 175](http://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F111-II-175%3Ade&lang=de&type=show_document) | 1985 | German |
| 18 | [BGE 111 IA 12](https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F111-IA-12%3Ade&lang=de&zoom=&type=show_document) | 1985 | German |
| 19 | [BGer 4C.32/2001](https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza%3A%2F%2F07-05-2001-4C-32-2001&lang=de&type=show_document) | 2001 | German |
| 20 | [BGE 102 II 143](https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F102-II-143%3Ade&lang=it&type=show_document) | 1976 | German |
| 21 | [BGE 119 II 264](http://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F119-II-264%3Ade&lang=de&type=show_document) | 1993 | German |
| 22 | [BGE 117 II 494](https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F117-II-494%3Ade&lang=de&type=show_document) | 1991 | German |
| 23 | [BGer 4A 227/2009](https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza%3A%2F%2F28-07-2009-4A_227-2009&lang=de&type=show_document) | 2009 | French |
| 24 | [BGE 80 II 179](https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F80-II-179%3Ade&lang=de&zoom=&type=show_document) | 1954 | French |
| 25 | [BGE 91 II 44](https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F91-II-44%3Ade&lang=de&zoom=&type=show_document) | 1965 | German |
| 26 | [BGE 133 III 90](https://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F133-III-90%3Afr&lang=fr&type=show_document) | 2006 | German |
| 27 | [BGer 4A 15/2024](https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=aza%3A%2F%2F18-04-2024-4A_15-2024&lang=de&type=show_document) | 2024 | German |
| 28 | [BGer 4A 120/2022](https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza://26-10-2021-4A_133-2021&lang=de&zoom=&type=show_document) | 2022 | French |
| 29 | [BGer 4A 133/2021; BGer 4A 135/2021](https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza://26-10-2021-4A_133-2021&lang=de&zoom=&type=show_document) | 2021 | French |
| 30 | [BGer 4A 543/2018](https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza%3A%2F%2Faza://28-05-2019-4A_543-2018&lang=de&zoom=&type=show_document) | 2019 | German |
| 31 | [BGer 4A 559/2022](https://www.bger.ch/ext/eurospider/live/fr/php/aza/http/index.php?highlight_docid=aza://03-08-2023-4A_559-2022&lang=fr&zoom=&type=show_document) | 2023 | German |
| 32 | [BGer 4C.458/2004](https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?lang=de&type=show_document&highlight_docid=aza://17-05-2005-4C-458-2004) | 2005 | Italian |
| 33 | [BGE 140 III 473](https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F140-III-473%3Ade&lang=de&type=show_document) | 2014 | German |

### Ground Truth

See the ground truth for all 33 cases [here](/cold_case_analyzer/data/ground_truth.csv).  
An example explaining what is behind a ground truth is available [here](/cold_case_analyzer/data/Ground%20truth%20explained.pdf).

## Prompts

**Abstract**
> Your task is to extract the abstract from a court decision. Your response only consists of the abstract, with no explanations or additional information. The official abstract in the case is right at the beginning, usually called "Regeste". Please translate this section into English. If there is no dedicated abstract to be found, and only then, you have to return a general description of the information in the file. It has to be concise and condense all the key details (topic, provisions, information about the legal dispute) in a single paragraph or less. If any legal provisions are mentioned, use their English abbreviation.

**Facts**
> Your task is to extract and summarise the relevant facts from a court decision. Your response consists of the relevant facts only, no explanations or other additional information. You return a structured paragraph meaningful to private international law practitioners. The relevant facts summed up from the case must provide a concise account of the factual background that is essential to understanding the legal dispute, avoiding extraneous details. Relevant information includes who the parties are, what happened, what the dispute is about, and what the different stages of court proceedings are. Your response prioritizes information on choice of law and can only contain accurate information. Under no circumstances can you add assumptions that are not stated in the case. If any legal provisions are mentioned, use their English abbreviation.

**PIL Provisions**
> Your task is to extract rules related to choice of law cited in a court decision. Your response is a list of provisions sorted by the impact of the rules for the choice of law issue(s) present within the court decision. Your response consists of this list only, no explanations or other additional information. A relevant provision usually stems from the most prominent legislation dealing with private international law in the respective jurisdiction. In Switzerland, for instance, it is usually the PILA. If no legislative provision is found, double-check whether there is any other court decision cited as a choice of law precedent. The output adheres to this format: ["provision_1", "provision_2", ...]. If you do not find PIL provisions in the court decision or if you are not sure, return [\"NA\"]. If any language other than English is used to cite a provision, use their English abbreviation.

**PIL Theme and Choice-of-law Issue Prompt**
> 1. Classification  
Your task is to classify a court decision into one specific theme. Your response is one of the values from the "Keywords" column in the format \"keyword\". You assign the theme by finding the choice of law issue from the court decision and determining which definition fits better. THE OUTPUT HAS TO BE ONE OF THE VALUES FROM THE TABLE.
Here is the table with all the keywords and their definitions:
{concepts}

> 2. Inference  
Your task is to identify the main private international law issue from a court decision. Your response will be a concise yes-no question. The issue you extract will have to do with choice of law and the output has to be phrased in a general fashion. The issue is not about the specific details of the case but rather the overall choice-of-law issue behind the case. If any legal provisions are mentioned, use their English abbreviation.
The issue in this case is related to this theme: {classification}, which can be defined as: {definition}

**Court's Position**
> Summarize the court's position on the choice-of-law issue(s) within the decision. Your response is phrased in a general way, generalizing the issue(s) so that your generalization could be applied to other private international law cases. If any legal provisions are mentioned, use their English abbreviation.
Your output is a direct answer to the issue laid out here:
{issue}


## Results

See the results for the 3 example cases [here](/5_IPR_Nachwuchstagung/top-3.csv).  
See the results for all 33 Swiss cases analyzed [here](https://choiceoflawdataverse.blob.core.windows.net/cold-case-analysis/case_analysis_results.xlsx).  
See the full comparison between ground truths and case analyzer outputs [here](/5_IPR_Nachwuchstagung/ground_truths_output_comparison.xlsx).  

### Selected Cases
**BGE 130 III 620**
| **Category** | **LLM Task** | **Prompt** | **Ground Truth** | **Case Analyzer Output** |
| :-- | :-- | :-- | :-- | :-- |
| **Abstract** | Information Extraction | Your task is to extract the abstract from a court decision. … | Consideration of third-country overriding mandatory provisions under Art. 19 PILA; … | Consideration of third-country intervention norms under Art. 19 of the Swiss Private International Law Act (PILA); … |
| **Relevant Facts** | Summarization | Your task is to extract and summarise the relevant facts from a court decision. … | A U.S. citizen domiciled in California, opened an account with a Swiss bank. … | A.B., residing in California, USA, filed a lawsuit against D. SA, a company based in Geneva with a branch in Zurich, … |
| **PIL Provision** | Information Extraction | Your task is to extract rules related to choice of law cited in a court decision. … | Art. 19 PILA | Art. 19 PILA, Art. 166 ff. PILA |
| **PIL Theme** | Classification | Your task is to classify a court decision into one specific theme. … | Overriding mandatory rules | Mandatory rules |
| **Choice-of-law Issue** | Inference | Your task is to identify the main private international law issue from a court decision. … | Can national law of another jurisdiction be taken into account, as an overriding mandatory provision … | Should the court apply the overriding mandatory rules of a third country under Article 19 of the Swiss Private International Law Act … |
| **Court's Position** | Inference | Summarize the court's position on the choice-of-law issue within the decision. … | Art. 19 PILA could, in exceptional circumstances, allow the application of overriding mandatory provisions from third countries … | In addressing the choice of law issue under Article 19 of the Swiss Private International Law Act (IPRG), the court's position is that the application … |

**BGE 132 III 285**
| **Category** | **LLM Task** | **Prompt** | **Ground Truth** | **Case Analyzer Output** |
| :-- | :-- | :-- | :-- | :-- |
| **Abstract** | Information Extraction | Your task is to extract the abstract from a court decision. … | Validity of choice of law clauses (Art. 116 PILA). … | Article 116 of the Swiss Private International Law Act (PILA); admissibility of choice of law. … |
| **Relevant Facts** | Summarization | Your task is to extract and summarise the relevant facts from a court decision. … | X. AG (plaintiff), represented by a FIFA agent, concluded a contract with Y. (defendant), a Greek public limited company, … | The case involves X. AG, a company based in St. Gallen, Switzerland (plaintiff), and Y., a Greek corporation (defendant). … |
| **PIL Provision** | Information Extraction | Your task is to extract rules related to choice of law cited in a court decision. … | Art. 116 PILA | Art. 116 PILA, Art. 129 CO |
| **PIL Theme** | Classification | Your task is to classify a court decision into one specific theme. … | Party autonomy, Rules of law | Non-State law (rules of law) |
| **Choice-of-law Issue** | Inference | Your task is to identify the main private international law issue from a court decision. … | Can parties choose the rules of a private association (non-State law) as the governing law of their agreement? | Can parties choose non-state rules, such as those established by private organizations, as the governing law … |
| **Court's Position** | Inference | Summarize the court's position on the choice-of-law issue within the decision. … | No, the rules of a private association (FIFA, non-State law) cannot be chosen as governing law in an international contract … | The court's position on the choice of law issue under Article 116 of the Swiss Private International Law Act (IPRG) … |

**BGE 133 III 90**
| **Category** | **LLM Task** | **Prompt** | **Ground Truth** | **Case Analyzer Output** |
| :-- | :-- | :-- | :-- | :-- |
| **Abstract** | Information Extraction | Your task is to extract the abstract from a court decision. … | Change in the circumstances of attachment in continuing obligations; applicable law; change of status (Art. 117 PILA). … | Change of connecting factors in long-term contractual relationships; applicable law; change of statute (Art. 117 PILA). … |
| **Relevant Facts** | Summarization | Your task is to extract and summarise the relevant facts from a court decision. … | In the present case, the question arises whether a subsequent change in the connecting factors can affect the determination of the applicable law. … | A.B. and B.B., residents of Greece, filed a lawsuit on December 19, 2003, in the District Court of Zurich against X., … |
| **PIL Provision** | Information Extraction | Your task is to extract rules related to choice of law cited in a court decision. … | Art. 117 PILA | Art. 117 PILA |
| **PIL Theme** | Classification | Your task is to classify a court decision into one specific theme. … | Absence of choice | Connecting factors |
| **Choice-of-law Issue** | Inference | Your task is to identify the main private international law issue from a court decision. … | In the absence of a choice of law agreement, should a subsequent change in the domicile of the party … | Does a change in the residence of the party providing the characteristic performance in a long-term contractual relationship … |
| **Court's Position** | Inference | Summarize the court's position on the choice-of-law issue within the decision. … | Although this cannot be excluded in general, it is not justified in the present case because the resulting law has no connection … | In addressing the choice of law issue under Article 117 of the Swiss Private International Law Act (PILA), the court held that a change in the residence … |


## What is the Choice of Law Dataverse (CoLD)?
CoLD is a research project at the University of Lucerne, aiming to make Private International Law more accessible by developing and leveraging digital tools. See more on [www.cold.global](https://www.cold.global/).

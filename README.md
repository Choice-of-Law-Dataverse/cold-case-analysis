# cold-case-analysis-llm
automated analysis of court decisions

| Category | Description | Task |
| --- | --- | --- |
| Abstract | Official abstract of the decision, otherwise AI-generated | Extraction |
| Relevant Facts | A short summary of the facts of the case (who are the parties, what happened, what is the dispute about, the different stages of court proceedings, etc.). This field prioritizes information on choice of law. | Extraction/Summarization |
| Relevant Rules of Law | The relevant legal provisions that are related to choice of law from the choice of law issue(s)/agreement/clause/interpretation(s). This field might also include important precedents or other decisions that were used as a reference in the judgment. | Extraction |
| Choice of Law Issue | Questions arising from the choice of law issue(s)/agreement/clause/interpretation(s) | Classification → Interpretation |
| Court’s Position | The opinion of the court in regard to the statements made in the "Choice of law issue" column. | Extraction/Interpretation |

## project structure
```
├── cold_case_analyzer/  
│   ├── config.py  
│   ├── main.py  
│   ├── case_analyzer/  
│   │   ├── __init__.py  
│   │   ├── abstracts.py  
│   │   ├── relevant_facts.py  
│   │   ├── rules_of_law.py  
│   │   ├── choice_of_law_issue.py  
│   │   └── courts_position.py  
│   ├── data_handler/  
│   │   ├── __init__.py  
│   │   └── airtable_retrieval.py  
│   ├── llm_handler/  
│   │   ├── __init__.py  
│   │   ├── fine_tuning.py  
│   │   └── model_access.py  
│   ├── prompts/  
│   │   ├── abstract.txt  
│   │   ├── facts.txt  
│   │   ├── rules.txt  
│   │   ├── issue.txt  
│   │   ├── issue_classification.txt  
│   │   └── position.txt
```

## Data
The first application uses Swiss Court Decisions. Here is an overview for the cases used:

| **Nr.** | **ID**     | **case**                                 | **Year** | **Language** | **Link**                                                                                                                                                                                                                                           |
|---------|------------|------------------------------------------|---------:|-------------:|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1       | CHE-1017   | BGE 131 III 289                          | 2005     | DE           | <https://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F131-III-289%3Ade&lang=de&type=show_document>                                                                                                                        |
| 2       | CHE-1019   | BGE 81 II 175                            | 1955     | DE           | <https://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F81-II-175%3Ade&lang=de&type=show_document>                                                                                                                         |
| 3       | CHE-1020   | BGE 78 II 74                             | 1952     | FRA          | <https://entscheide.weblaw.ch/dumppdf.php?link=BGE-78-II-74>                                                                                                                                                                                      |
| 4       | CHE-1021   | BGE 138 III 750                          | 2012     | FRA          | <https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F138-III-750%3Ade&lang=de&type=show_document>                                                                                                       |
| 5       | CHE-1022   | BGer 4A 264/2008                         | 2008     | FRA          | <https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza%3A%2F%2F23-09-2008-4A_264-2008&lang=de&type=show_document>                                                                                                  |
| 6       | CHE-1023   | BGE 138 III 489                          | 2012     | DE           | <https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F138-III-489%3Ade&lang=de&type=show_document>                                                                                                       |
| 7       | CHE-1024   | BGer 4C.168/2006                         | 2006     | DE           | <https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza%3A%2F%2F11-09-2006-4C-168-2006&lang=de&type=show_document>                                                                                                  |
| 8       | CHE-1025   | BGE 123 III 35                           | 1996     | DE           | <https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F123-III-35%3Ade&lang=de&type=show_document>                                                                                                        |
| 9       | CHE-1026   | BGer 4A 394/2009                         | 2009     | FRA          | <https://www.bger.ch/ext/eurospider/live/fr/php/aza/http/index.php?highlight_docid=aza://04-12-2009-4A_394-2009&lang=de&type=show_document>                                                                                                        |
| 10      | CHE-1027   | BGE 128 III 201                          | 2002     | DE           | <https://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F128-III-201%3Ade&lang=de&type=show_document>                                                                                                                        |
| 11      | CHE-1028   | BGE 132 III 285                          | 2005     | DE           | <https://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F132-III-285%3Afr&lang=fr&type=show_document>                                                                                                                        |
| 12      | CHE-1030   | BGE 119 II 173                           | 1993     | DE           | <https://www.bger.ch/ext/eurospider/live/fr/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F119-II-173%3Afr&lang=fr&type=show_document>                                                                                                        |
| 13      | CHE-1033   | BGE 130 III 620                          | 2004     | DE           | <https://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F130-III-620%3Ade&lang=de&type=show_document>                                                                                                                        |
| 14      | CHE-1034   | BGE 136 III 392                          | 2010     | FRA          | <https://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F136-III-392%3Ade&lang=de&type=show_document>                                                                                                                        |
| 15      | CHE-1035   | BGer 4C.54/2000                          | 2001     | FRA          | <https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza%3A%2F%2F19-01-2001-4C-54-2000&lang=de&type=show_document>                                                                                                    |
| 16      | CHE-1037   | BGer 5C.68/2002                          | 2002     | DE           | <https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza%3A%2F%2F25-04-2002-5C-68-2002&lang=de&type=show_document>                                                                                                    |
| 17      | CHE-1038   | BGE 111 II 175                           | 1985     | DE           | <http://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F111-II-175%3Ade&lang=de&type=show_document>                                                                                                                           |
| 18      | CHE-1039   | BGE 111 IA 12                            | 1985     | DE           | <https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F111-IA-12%3Ade&lang=de&zoom=&type=show_document>                                                                                                   |
| 19      | CHE-1040   | BGer 4C.32/2001                          | 2001     | DE           | <https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza%3A%2F%2F07-05-2001-4C-32-2001&lang=de&type=show_document>                                                                                                    |
| 20      | CHE-1042   | BGE 102 II 143                           | 1976     | DE           | <https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F102-II-143%3Ade&lang=it&type=show_document>                                                                                                        |
| 21      | CHE-1043   | BGE 119 II 264                           | 1993     | DE           | <http://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F119-II-264%3Ade&lang=de&type=show_document>                                                                                                                           |
| 22      | CHE-1044   | BGE 117 II 494                           | 1991     | DE           | <https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F117-II-494%3Ade&lang=de&type=show_document>                                                                                                         |
| 23      | CHE-1045   | BGer 4A 227/2009                         | 2009     | FRA          | <https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza%3A%2F%2F28-07-2009-4A_227-2009&lang=de&type=show_document>                                                                                                   |
| 24      | CHE-1050   | BGE 80 II 179                            | 1954     | FRA          | <https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F80-II-179%3Ade&lang=de&zoom=&type=show_document>                                                                                                    |
| 25      | CHE-1051   | BGE 91 II 44                             | 1965     | DE           | <https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F91-II-44%3Ade&lang=de&zoom=&type=show_document>                                                                                                     |
| 26      | CHE-1314   | BGE 133 III 90                           | 2006     | DE           | <https://relevancy.bger.ch/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F133-III-90%3Afr&lang=fr&type=show_document>                                                                                                                          |
| 27      | CHE-1319   | BGer 4A 15/2024                          | 2024     | DE           | <https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=aza%3A%2F%2F18-04-2024-4A_15-2024&lang=de&type=show_document>                                                                                                   |
| 28      | CHE-1320   | BGer 4A 120/2022                         | 2022     | FRA          | <https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza://26-10-2021-4A_133-2021&lang=de&zoom=&type=show_document>                                                                                                  |
| 29      | CHE-1327   | BGer 4A 133/2021;<br>BGer 4A 135/2021     | 2021     | FRA          | <https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza://26-10-2021-4A_133-2021&lang=de&zoom=&type=show_document>                                                                                                  |
| 30      | CHE-1328   | BGer 4A 543/2018                         | 2019     | DE           | <https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?highlight_docid=aza%3A%2F%2Faza://28-05-2019-4A_543-2018&lang=de&zoom=&type=show_document>                                                                                       |
| 31      | CHE-1331   | BGer 4A 559/2022                         | 2023     | DE           | <https://www.bger.ch/ext/eurospider/live/fr/php/aza/http/index.php?highlight_docid=aza://03-08-2023-4A_559-2022&lang=fr&zoom=&type=show_document>                                                                                                  |
| 32      | CHE-1332   | BGer 4C.458/2004                         | 2005     | IT           | <https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?lang=de&type=show_document&highlight_docid=aza://17-05-2005-4C-458-2004>                                                                                                        |
| 33      | CHE-1333   | BGE 140 III 473                          | 2014     | DE           | <https://www.bger.ch/ext/eurospider/live/de/php/clir/http/index.php?highlight_docid=atf%3A%2F%2F140-III-473%3Ade&lang=de&type=show_document>                                                                                                        |


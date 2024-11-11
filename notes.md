# Notes:
- Use Markdown while prompting
- If break down the problem very small small problems, LLM will give best results
- So don't be generic
- Use LLM as last resort if you cannot programmatically do it.
- Problem is with RAG - splitting docus into relevant docs to put in vector db
- Use Assure Document Intelligent to break down doc into relevant chunks (DocumentAI)
- Let DocAI output markdown, then split document based on headers. to make all the context is relevant
- Use some LLM monitoring tools like langfuse (opensource) - a dockerized version is here. So host it from ur end
- Database Management
• Structured Databases: We use Postgres.
• Unstructured Databases: Opt for MongoDB.
• Vector Databases: Qdrant (best) or Postgres with PGVector (smaller projects)



# Design
- Create mock db to simulate db access (in sqlite.db) (or dir of database table in parquet files)
- Use AI to identify a patterns put them into a yaml config file (what to do on each stage)
- Find all possible functions to trigger and write them and modularize
- Write high qualility generic scalable parameter tweakable functions / classes which can be triggered from the structure yaml file (see `structure` yaml file)
- Write test cases and expected input/outputs do make false proof logic (in terms of code and data)


# Structure YAML file
```yaml

colloboration_with: FactSet
event_type: Recon
dates: 
  ref_date: "2024-02-28"
  ann_date: ".."
  ss_date: ""
  eff_date: ""
universe_securities:
  yet to figure out how to go
  1. exchanges based
  2. country based
  if country based: get list of countries
  if exchange based: get the list of countries
datapoint collection: 
- from reference data api
- from adtv api
- from .....
filters:
  base:
    localprice: true
    sanction filters:
      countries: true
      compnaywise/securitywise: true
    northbound: false
  main:
    marketcap:
      float adjusted security market cap: true
      security market cap: false
      company market cap: false
    adtv:
      3m: true
      6m: false
    n_months avg: false
    most_liquid: true
    industry_filter:
      subindustry_filter: false
      factset rbics6filter: true
    focus_industry_filter: false
    participant_sector_filter: false
    supply chain filter: true
    ranking:
      mktcap based: false
      adtv base: false
      mktcap + adtv: true
    top_n_filter: true
# configure above data fields in  such a way that reason finding is easy
reason_finding: true

weighting:
  initial_weights:
    float_adj_mktcap_based: true
    weights_








  
- 

```

## LOGIC
- Collect all the methodology documents
- Collect all data / input / output/ interwoven / any intermeidatory if tehre is
- Give each document to LLM and ask to figure out structure
- Once it comes with structure from each document
- Ask LLM to find out common points in those structures
- common onces put common names idenfify in structure config file
- Others take a look at manually and fix them
- Once it is done, We use AI/manual look into construting the structure config file in  more generic way. ( but giving still room for custom inserts in special cases)
- Once the skeleton for structure config is set
- Now we say AI to look into document in view of parsing the structure in the defined way (like in structure config file)
- AI outputs index specifc yaml file
- Now the common functions written by us will be triggerd base on yaml config
- run the code & get output
- write test cases to compare to returned output vs expected (even AI can do if needed)
- run the same for each quarters (4 prev)
- if all pass, take manuual look and finalize
- if some not working: 
  - later we can write back for conv with LLM and domain expert who initially did the recon/rebal
  - now, we give to Ops domain guys, they connect with SPOC and understand the difference and come up with solutions
  - if some entire logic is incorrect, we patch it and run test cases for all the past written indices within this platform and make sure nothing breaks bcz of this.
- Keep completed test cases, for later runs if some patch to functionality anywhee added. 
- Backup the input and ouput data as well for later running of testcases
- Backup the screenshots of database for relevant data (so db changes happened it should not be attributed as coding logic issue)

## Hypothesis Testing
- H0 (null hypothesis) - New AI Based automation improves the work process (significantly - consider the ose)
- Ha (alternate hypothesis) - Does not signicantly improves

### Fail to reject the null hypothesis?

## Mix AI, Coding, Engineering, Scaling, Proper Data Science applied on
- Blend of AI/Data Science/Coding
- Text processing regex, NLP, 

## Once the AI Agentic framework is built
- How much time?
- Code run to read mehodolgy and convert structured config. 10 minutes
- if few things to be double checked and tweaked (1 day max)
- 7 / 10 supposed to directly automated without any haste
- rest 3, manual intervension. once the logic is found, we will retrain the GenAI Agentic Framework to adopt the changes so that in next scenarios, it won't happen again


## Don't want people to leave
## AI is the future. Don't be late to adapt the new techs.


## Track all prewritten functions (in some trakcer file) 
find what changed over time, how did it affect

## Questions
- Why need test cases?
- Why config file (customizable, configurable, scalable)

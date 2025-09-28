
Google Scholar API
API uptime
99.997%
Our Google Scholar API allows you to scrape SERP results from a Google Scholar search query. The API is accessed through the following endpoint: /search?engine=google_scholar.

A user may query the following: https://serpapi.com/search?engine=google_scholar utilizing a GET request. Head to the playground for a live and interactive demo.

API Parameters
Search Query
q

Required

Parameter defines the query you want to search. You can also use helpers in your query such as: author:, or source:.

Usage of cites parameter makes q optional. Usage of cites together with q triggers search within citing articles.

Usage of cluster together with q and cites parameters is prohibited. Use cluster parameter only.

Advanced Google Scholar Parameters
cites

Optional

Parameter defines unique ID for an article to trigger Cited By searches. Usage of cites will bring up a list of citing documents in Google Scholar. Example value: cites=1275980731835430123. Usage of cites and q parameters triggers search within citing articles.

as_ylo

Optional

Parameter defines the year from which you want the results to be included. (e.g. if you set as_ylo parameter to the year 2018, the results before that year will be omitted.). This parameter can be combined with the as_yhi parameter.

as_yhi

Optional

Parameter defines the year until which you want the results to be included. (e.g. if you set as_yhi parameter to the year 2018, the results after that year will be omitted.). This parameter can be combined with the as_ylo parameter.

scisbd

Optional

Parameter defines articles added in the last year, sorted by date. It can be set to 1 to include only abstracts, or 2 to include everything. The default value is 0 which means that the articles are sorted by relevance.

cluster

Optional

Parameter defines unique ID for an article to trigger All Versions searches. Example value: cluster=1275980731835430123. Usage of cluster together with q and cites parameters is prohibited. Use cluster parameter only.

Localization
hl

Optional

Parameter defines the language to use for the Google Scholar search. It's a two-letter language code. (e.g., en for English, es for Spanish, or fr for French). Head to the Google languages page for a full list of supported Google languages.

lr

Optional

Parameter defines one or multiple languages to limit the search to. It uses lang_{two-letter language code} to specify languages and | as a delimiter. (e.g., lang_fr|lang_de will only search French and German pages). Head to the Google lr languages for a full list of supported languages.

Pagination
start

Optional

Parameter defines the result offset. It skips the given number of results. It's used for pagination. (e.g., 0 (default) is the first page of results, 10 is the 2nd page of results, 20 is the 3rd page of results, etc.).

num

Optional

Parameter defines the maximum number of results to return, ranging from 1 to 20, with a default of 10.

Search Type
as_sdt

Optional

Parameter can be used either as a search type or a filter.

As a Filter (only works when searching articles):
0 - exclude patents (default).
7 - include patents.

As a Search Type:
4 - Select case law (US courts only). This will select all the State and Federal courts.
e.g. as_sdt=4 - Selects case law (all courts)

To select specific courts, see the full list of supported Google Scholar courts.
e.g. as_sdt=4,33,192 - 4 is the required value and should always be in the first position, 33 selects all New York courts and 192 selects Tax Court.
Values have to be separated by comma (,)

Advanced Filters
safe

Optional

Parameter defines the level of filtering for adult content. It can be set to active or off, by default Google will blur explicit content.

filter

Optional

Parameter defines if the filters for 'Similar Results' and 'Omitted Results' are on or off. It can be set to 1 (default) to enable these filters, or 0 to disable these filters.

as_vis

Optional

Parameter defines whether you would like to include citations or not. It can be set to 1 to exclude these results, or 0 (default) to include them.

as_rr

Optional

Parameter defines whether you would like to show only review articles or not (these articles consist of topic reviews, or discuss the works or authors you have searched for). It can be set to 1 to enable this filter, or 0 (default) to show all results.

Serpapi Parameters
engine

Required

Set parameter to google_scholar to use the Google Scholar API engine.

no_cache

Optional

Parameter will force SerpApi to fetch the Google Scholar results even if a cached version is already present. A cache is served only if the query and all parameters are exactly the same. Cache expires after 1h. Cached searches are free, and are not counted towards your searches per month. It can be set to false (default) to allow results from the cache, or true to disallow results from the cache. no_cache and async parameters should not be used together.

async

Optional

Parameter defines the way you want to submit your search to SerpApi. It can be set to false (default) to open an HTTP connection and keep it open until you got your search results, or true to just submit your search to SerpApi and retrieve them later. In this case, you'll need to use our Searches Archive API to retrieve your results. async and no_cache parameters should not be used together. async should not be used on accounts with Ludicrous Speed enabled.

zero_trace

Optional

Enterprise only. Parameter enables ZeroTrace mode. It can be set to false (default) or true. Enable this mode to skip storing search parameters, search files, and search metadata on our servers. This may make debugging more difficult.

api_key

Required

Parameter defines the SerpApi private key to use.

output

Optional

Parameter defines the final output you want. It can be set to json (default) to get a structured JSON of the results, or html to get the raw html retrieved.

json_restrictor

Optional

Parameter defines the fields you want to restrict in the outputs for smaller, faster responses. See JSON Restrictor for more details.

API Results
JSON Results
JSON output includes structured data for organic results.

A search status is accessible through search_metadata.status. It flows this way: Processing -> Success || Error. If a search has failed, error will contain an error message. search_metadata.id is the search ID inside SerpApi.

HTML Results
HTML output is useful to debug JSON results or support features not supported yet by SerpApi.
HTML output gives you the raw HTML results from Google.

API Examples
Example with 
q
:
biology
GET


https://serpapi.com/search.json?engine=google_scholar&q=biology

Code to integrate


Ruby

require "serpapi" 

client = SerpApi::Client.new(
  engine: "google_scholar",
  q: "biology",
  api_key: "3c103eeb11f1b934b3db30a26c73c159b8534a0ccedd0eaa970e3d5dba046849"
)

results = client.search
organic_results = results[:organic_results]

JSON Example

{
  "search_metadata": {
    "id": "5d8cb082de983409f4a1aa21",
    "status": "Success",
    "json_endpoint": "https://serpapi.com/searches/6e2dda69527af983/5d8cb082de983409f4a1aa21.json",
    "created_at": "2019-09-26 12:35:14 UTC",
    "processed_at": "2019-09-26 12:35:14 UTC",
    "google_scholar_url": "https://scholar.google.com/scholar?&q=biology",
    "raw_html_file": "https://serpapi.com/searches/6e2dda69527af983/5d8cb082de983409f4a1aa21.html",
    "total_time_taken": 1.24
  },
  "search_parameters": {
    "engine": "google_scholar",
    "q": "biology"
  },
  "search_information": {
    "total_results": 5880000,
    "time_taken_displayed": 0.06,
    "query_displayed": "biology"
  },
  "organic_results": [
    {
      "position": 0,
      "title": "Population biology of plants.",
      "result_id": "JC4Acibs_4kJ",
      "link": "https://www.cabdirect.org/cabdirect/abstract/19782321379",
      "snippet": "The first chapter is concerned with experiments, analogies and models. There are sections on dispersal, dormancy and recruitment of seedling populations, effects of neighbours, effects of predators and natural dynamics of plant populations, and plants, vegetation and evolution. There …",
      "publication_info": {
        "summary": "JL Harper - Population biology of plants., 1977 - cabdirect.org"
      },
      "inline_links": {
        "serpapi_cite_link": "https://serpapi.com/search.json?engine=google_scholar_cite&q=JC4Acibs_4kJ&token=a57f24e24842c7de",
        "cited_by": {
          "total": 14003,
          "link": "https://scholar.google.com/scholar?cites=9943926152122871332&as_sdt=5,38&sciodt=0,38&hl=en",
          "cites_id": "9943926152122871332",
          "serpapi_scholar_link": "https://serpapi.com/search.json?cites=9943926152122871332&engine=google_scholar&hl=en"
        },
        "related_pages_link": "https://scholar.google.com/scholar?q=related:JC4Acibs_4kJ:scholar.google.com/&scioq=biology&hl=en&as_sdt=0,38",
        "serpapi_related_pages_link": "https://serpapi.com/search.json?as_sdt=0%2C38&engine=google_scholar&hl=en&q=related%3AJC4Acibs_4kJ%3Ascholar.google.com%2F",
        "versions": {
          "total": 6,
          "link": "https://scholar.google.com/scholar?cluster=9943926152122871332&hl=en&as_sdt=0,38",
          "cluster_id": "9943926152122871332",
          "serpapi_scholar_link": "https://serpapi.com/search.json?cluster=9943926152122871332&engine=google_scholar&hl=en"
        },
        "cached_page_link": "https://scholar.google.comhttps://scholar.googleusercontent.com/scholar?q=cache:JC4Acibs_4kJ:scholar.google.com/+biology&hl=en&as_sdt=0,38"
      }
    },
    {
      "position": 1,
      "title": "Molecular cell biology",
      "result_id": "5BUDsdJ6ho0J",
      "link": "https://books.google.com/books?hl=en&lr=&id=K3JbjG1JiUMC&oi=fnd&pg=PA1&dq=biology&ots=arHdVTEq5F&sig=XpJrdZciq9Vy8ss_K4kJe7AnKk4",
      "snippet": "With its acclaimed author team, cutting-edge content, emphasis on medical relevance, and coverage based on landmark experiments, Molecular Cell Biology has justly earned an impeccable reputation as an authoritative and exciting text. The new Sixth Edition features …",
      "publication_info": {
        "summary": "H Lodish, A Berk, CA Kaiser, M Krieger, MP Scott… - 2008 - books.google.com"
      },
      "resources": [
        {
          "title": "nsysu.edu.tw",
          "file_format": "PDF",
          "link": "http://www2.nsysu.edu.tw/wzhlab/ch6.pdf"
        }
      ],
      "inline_links": {
        "serpapi_cite_link": "https://serpapi.com/search.json?engine=google_scholar_cite&q=5BUDsdJ6ho0J&token=5c469afb4977cc88",
        "cited_by": {
          "total": 9196,
          "link": "https://scholar.google.com/scholar?cites=10197973451558557156&as_sdt=5,38&sciodt=0,38&hl=en",
          "cites_id": "10197973451558557156",
          "serpapi_scholar_link": "https://serpapi.com/search.json?cites=10197973451558557156&engine=google_scholar&hl=en"
        },
        "related_pages_link": "https://scholar.google.com/scholar?q=related:5BUDsdJ6ho0J:scholar.google.com/&scioq=biology&hl=en&as_sdt=0,38",
        "serpapi_related_pages_link": "https://serpapi.com/search.json?as_sdt=0%2C38&engine=google_scholar&hl=en&q=related%3A5BUDsdJ6ho0J%3Ascholar.google.com%2F",
        "versions": {
          "total": 18,
          "link": "https://scholar.google.com/scholar?cluster=10197973451558557156&hl=en&as_sdt=0,38",
          "cluster_id": "10197973451558557156",
          "serpapi_scholar_link": "https://serpapi.com/search.json?cluster=10197973451558557156&engine=google_scholar&hl=en"
        }
      }
    },
    {
      "position": 2,
      "title": "Brock biology of microorganisms",
      "result_id": "aYK6cRyUoXoJ",
      "link": "https://www.researchgate.net/profile/Michael_Madigan/publication/48363170_Brock_Biology_of_Micro-Organisms/links/5573057208aeb6d8c017dcd8.pdf",
      "snippet": "Purple bacteria are anoxygenic phototrophs that grow phototrophically, obtaining carbon from CO2+ H2S (purple sulfur bacteria) or organic compounds (purple nonsulfur bacteria). Purple nonsulfur bacteria are physiologically diverse and most can grow as …",
      "publication_info": {
        "summary": "MT Madigan, JM Martinko, J Parker - 1997 - researchgate.net"
      },
      "resources": [
        {
          "title": "researchgate.net",
          "file_format": "PDF",
          "link": "https://www.researchgate.net/profile/Michael_Madigan/publication/48363170_Brock_Biology_of_Micro-Organisms/links/5573057208aeb6d8c017dcd8.pdf"
        }
      ],
      "inline_links": {
        "serpapi_cite_link": "https://serpapi.com/search.json?engine=google_scholar_cite&q=aYK6cRyUoXoJ&token=cbecc0298d3a04ca",
        "cited_by": {
          "total": 9710,
          "link": "https://scholar.google.com/scholar?cites=8836506793765667433&as_sdt=5,38&sciodt=0,38&hl=en",
          "cites_id": "8836506793765667433",
          "serpapi_scholar_link": "https://serpapi.com/search.json?cites=8836506793765667433&engine=google_scholar&hl=en"
        },
        "related_pages_link": "https://scholar.google.com/scholar?q=related:aYK6cRyUoXoJ:scholar.google.com/&scioq=biology&hl=en&as_sdt=0,38",
        "serpapi_related_pages_link": "https://serpapi.com/search.json?as_sdt=0%2C38&engine=google_scholar&hl=en&q=related%3AaYK6cRyUoXoJ%3Ascholar.google.com%2F",
        "versions": {
          "total": 19,
          "link": "https://scholar.google.com/scholar?cluster=8836506793765667433&hl=en&as_sdt=0,38",
          "cluster_id": "8836506793765667433",
          "serpapi_scholar_link": "https://serpapi.com/search.json?cluster=8836506793765667433&engine=google_scholar&hl=en"
        },
        "cached_page_link": "https://scholar.google.comhttps://scholar.googleusercontent.com/scholar?q=cache:aYK6cRyUoXoJ:scholar.google.com/+biology&hl=en&as_sdt=0,38"
      }
    },
    {
      "position": 3,
      "title": "Circular statistics in biology.",
      "publication_info": {
        "summary": "E Batschelet - ACADEMIC PRESS, 111 FIFTH AVE., NEW YORK, NY …, 1981"
      },
      "inline_links": {
        "cited_by": {
          "total": 6022,
          "link": "https://scholar.google.com/scholar?cites=15768135063984745093&as_sdt=5,38&sciodt=0,38&hl=en",
          "cites_id": "15768135063984745093",
          "serpapi_scholar_link": "https://serpapi.com/search.json?cites=15768135063984745093&engine=google_scholar&hl=en"
        },
        "related_pages_link": "https://scholar.google.com/scholar?q=related:hSoxK0yr09oJ:scholar.google.com/&scioq=biology&hl=en&as_sdt=0,38",
        "serpapi_related_pages_link": "https://serpapi.com/search.json?as_sdt=0%2C38&engine=google_scholar&hl=en&q=related%3AhSoxK0yr09oJ%3Ascholar.google.com%2F",
      }
    },
    {
      "position": 4,
      "title": "Biology of amphibians",
      "result_id": "Bei1I16dqdMJ",
      "link": "https://books.google.com/books?hl=en&lr=&id=CzxVvKmrtIgC&oi=fnd&pg=PR9&dq=biology&ots=AZMakcrxfY&sig=_SM_ISg_pBl3qXSqEwMVxorAOSY",
      "snippet": "This is the widely acclaimed, preeminent reference and text on all aspects of amphibian biology, including their life history, ecology, morphology, and evolution. Copiously illustrated with original drawings and photographs and meticulously referenced with more than 2,500 …",
      "publication_info": {
        "summary": "WE Duellman, L Trueb - 1994 - books.google.com"
      },
      "inline_links": {
        "serpapi_cite_link": "https://serpapi.com/search.json?engine=google_scholar_cite&q=Bei1I16dqdMJ&token=cbecc0298d3a04ca",
        "cited_by": {
          "total": 7150,
          "link": "https://scholar.google.com/scholar?cites=15251894640718505989&as_sdt=5,38&sciodt=0,38&hl=en",
          "cites_id": "15251894640718505989",
          "serpapi_scholar_link": "https://serpapi.com/search.json?cites=15251894640718505989&engine=google_scholar&hl=en"
        },
        "related_pages_link": "https://scholar.google.com/scholar?q=related:Bei1I16dqdMJ:scholar.google.com/&scioq=biology&hl=en&as_sdt=0,38",
        "serpapi_related_pages_link": "https://serpapi.com/search.json?as_sdt=0%2C38&engine=google_scholar&hl=en&q=related%3ABei1I16dqdMJ%3Ascholar.google.com%2F",
        "versions": {
          "total": 4,
          "link": "https://scholar.google.com/scholar?cluster=15251894640718505989&hl=en&as_sdt=0,38",
          "cluster_id": "15251894640718505989",
          "serpapi_scholar_link": "https://serpapi.com/search.json?cluster=15251894640718505989&engine=google_scholar&hl=en"
        }
      }
    },
    {
      "position": 5,
      "title": "Elements of physical biology",
      "result_id": "-kzCxIbMYs0J",
      "link": "https://www.jstor.org/stable/43430362",
      "snippet": "F torn Dr. Alfred J. Lotka Dear Sir,-The review of Elements of Physical Biology which appeared in a recent issue of Science Progress is base on a fundamental misunderstanding of the method and purpos of that work. As this misunderstanding is calculated to mislead the …",
      "publication_info": {
        "summary": "AJ Lotka - Science Progress in the Twentieth Century (1919-1933 …, 1926 - JSTOR"
      },
      "inline_links": {
        "serpapi_cite_link": "https://serpapi.com/search.json?engine=google_scholar_cite&q=-kzCxIbMYs0J&token=cbecc0298d3a04ca",
        "cited_by": {
          "total": 5796,
          "link": "https://scholar.google.com/scholar?cites=14799616204691623162&as_sdt=5,38&sciodt=0,38&hl=en",
          "cites_id": "14799616204691623162",
          "serpapi_scholar_link": "https://serpapi.com/search.json?cites=14799616204691623162&engine=google_scholar&hl=en"
        },
        "related_pages_link": "https://scholar.google.com/scholar?q=related:-kzCxIbMYs0J:scholar.google.com/&scioq=biology&hl=en&as_sdt=0,38",
        "serpapi_related_pages_link": "https://serpapi.com/search.json?as_sdt=0%2C38&engine=google_scholar&hl=en&q=related%3A-kzCxIbMYs0J%3Ascholar.google.com%2F",
        "versions": {
          "total": 2,
          "link": "https://scholar.google.com/scholar?cluster=14799616204691623162&hl=en&as_sdt=0,38",
          "cluster_id": "14799616204691623162",
          "serpapi_scholar_link": "https://serpapi.com/search.json?cluster=14799616204691623162&engine=google_scholar&hl=en"
        }
      }
    },
    {
      "position": 6,
      "title": "Electron transfers in chemistry and biology",
      "result_id": "h-UUmfo_QI0J",
      "link": "https://www.sciencedirect.com/science/article/pii/030441738590014X",
      "snippet": "Electron-transfer reactions between ions and molecules in solution have been the subject of considerable experimental study during the past three decades. Experimental results have also been obtained on related phenomena, such as reactions between ions or molecules …",
      "publication_info": {
        "summary": "RA Marcus, N Sutin - Biochimica et Biophysica Acta (BBA)-Reviews on …, 1985 - Elsevier"
      },
      "inline_links": {
        "serpapi_cite_link": "https://serpapi.com/search.json?engine=google_scholar_cite&q=h-UUmfo_QI0J&token=cbecc0298d3a04ca",
        "cited_by": {
          "total": 8929,
          "link": "https://scholar.google.com/scholar?cites=10178205503399978375&as_sdt=5,38&sciodt=0,38&hl=en",
          "cites_id": "10178205503399978375",
          "serpapi_scholar_link": "https://serpapi.com/search.json?cites=10178205503399978375&engine=google_scholar&hl=en"
        },
        "related_pages_link": "https://scholar.google.com/scholar?q=related:h-UUmfo_QI0J:scholar.google.com/&scioq=biology&hl=en&as_sdt=0,38",
        "serpapi_related_pages_link": "https://serpapi.com/search.json?as_sdt=0%2C38&engine=google_scholar&hl=en&q=related%3Ah-UUmfo_QI0J%3Ascholar.google.com%2F",
        "versions": {
          "total": 6,
          "link": "https://scholar.google.com/scholar?cluster=10178205503399978375&hl=en&as_sdt=0,38",
          "cluster_id": "10178205503399978375",
          "serpapi_scholar_link": "https://serpapi.com/search.json?cluster=10178205503399978375&engine=google_scholar&hl=en"
        }
      }
    },
    {
      "position": 7,
      "title": "The world's worst weeds: distribution and biology",
      "publication_info": {
        "summary": "LG Holm, DL Plucknett, JV Pancho… - 1977 - University press of Hawaii Honolulu"
      },
      "inline_links": {
        "cited_by": {
          "total": 2884,
          "link": "https://scholar.google.com/scholar?cites=13741962940703055577&as_sdt=5,38&sciodt=0,38&hl=en",
          "cites_id": "13741962940703055577",
          "serpapi_scholar_link": "https://serpapi.com/search.json?cites=13741962940703055577&engine=google_scholar&hl=en"
        },
        "related_pages_link": "https://scholar.google.com/scholar?q=related:2R4wjXxCtb4J:scholar.google.com/&scioq=biology&hl=en&as_sdt=0,38",
        "serpapi_related_pages_link": "https://serpapi.com/search.json?as_sdt=0%2C38&engine=google_scholar&hl=en&q=related%3A2R4wjXxCtb4J%3Ascholar.google.com%2F",
        "versions": {
          "total": 8,
          "link": "https://scholar.google.com/scholar?cluster=13741962940703055577&hl=en&as_sdt=0,38",
          "cluster_id": "13741962940703055577",
          "serpapi_scholar_link": "https://serpapi.com/search.json?cluster=13741962940703055577&engine=google_scholar&hl=en"
        }
      }
    },
    {
      "position": 8,
      "title": "Free radicals in biology and medicine",
      "result_id": "GPYLddTNXkEJ",
      "link": "https://books.google.com/books?hl=en&lr=&id=3DlKCgAAQBAJ&oi=fnd&pg=PP1&dq=biology&ots=bonJ8_BujY&sig=iMkduC7cJ3EUnVEwMyH1cpUO164",
      "snippet": "Free Radicals in Biology and Medicine has become a classic text in the field of free radical and antioxidant research. Now in its fifth edition, the book has been comprehensively rewritten and updated whilst maintaining the clarity of its predecessors. Two new chapters …",
      "publication_info": {
        "summary": "B Halliwell, JMC Gutteridge - 2015 - books.google.com"
      },
      "resources": [
        {
          "title": "vanlanguni.edu.vn",
          "file_format": "PDF",
          "link": "http://thuvienso.vanlanguni.edu.vn/bitstream/Vanlang_TV/9963/11/SA3635_Free%20Radicals%20in%20Biology%20and%20Medicine_Chapter%207.pdf"
        }
      ],
      "inline_links": {
        "serpapi_cite_link": "https://serpapi.com/search.json?engine=google_scholar_cite&q=GPYLddTNXkEJ&token=cbecc0298d3a04ca",
        "cited_by": {
          "total": 26946,
          "link": "https://scholar.google.com/scholar?cites=15962228459898641425&as_sdt=5,38&sciodt=0,38&hl=en",
          "cites_id": "15962228459898641425",
          "serpapi_scholar_link": "https://serpapi.com/search.json?cites=15962228459898641425&engine=google_scholar&hl=en"
        },
        "related_pages_link": "https://scholar.google.com/scholar?q=related:EZzjdzY6hd0J:scholar.google.com/&scioq=biology&hl=en&as_sdt=0,38",
        "serpapi_related_pages_link": "https://serpapi.com/search.json?as_sdt=0%2C38&engine=google_scholar&hl=en&q=related%3AGPYLddTNXkEJ%3Ascholar.google.com%2F",
        "versions": {
          "total": 7,
          "link": "https://scholar.google.com/scholar?cluster=15962228459898641425&hl=en&as_sdt=0,38",
          "cluster_id": "15962228459898641425",
          "serpapi_scholar_link": "https://serpapi.com/search.json?cluster=15962228459898641425&engine=google_scholar&hl=en"
        }
      }
    },
    {
      "position": 9,
      "title": "Biology of ticks",
      "result_id": "k1yvQEA5qfMJ",
      "link": "https://books.google.com/books?hl=en&lr=&id=gck4AAAAQBAJ&oi=fnd&pg=PP1&dq=biology&ots=TbnHcyhX4b&sig=4v1XxtsrA506MvhTbGJyIWgSmrU",
      "snippet": "Biology of Ticks is the most comprehensive work on tick biology and tick-borne diseases. This second edition is a multi-authored work, featuring the research and analyses of renowned experts across the globe. Spanning two volumes, the book examines the …",
      "publication_info": {
        "summary": "DE Sonenshine, RM Roe - 2013 - books.google.com"
      },
      "inline_links": {
        "serpapi_cite_link": "https://serpapi.com/search.json?engine=google_scholar_cite&q=k1yvQEA5qfMJ&token=cbecc0298d3a04ca",
        "cited_by": {
          "total": 2123,
          "link": "https://scholar.google.com/scholar?cites=17557627570406513811&as_sdt=5,38&sciodt=0,38&hl=en",
          "cites_id": "17557627570406513811",
          "serpapi_scholar_link": "https://serpapi.com/search.json?cites=17557627570406513811&engine=google_scholar&hl=en"
        },
        "related_pages_link": "https://scholar.google.com/scholar?q=related:k1yvQEA5qfMJ:scholar.google.com/&scioq=biology&hl=en&as_sdt=0,38",
        "serpapi_related_pages_link": "https://serpapi.com/search.json?as_sdt=0%2C38&engine=google_scholar&hl=en&q=related%3Ak1yvQEA5qfMJ%3Ascholar.google.com%2F",
        "versions": {
          "total": 8,
          "link": "https://scholar.google.com/scholar?cluster=17557627570406513811&hl=en&as_sdt=0,38",
          "cluster_id": "17557627570406513811",
          "serpapi_scholar_link": "https://serpapi.com/search.json?cluster=17557627570406513811&engine=google_scholar&hl=en"
        }
      }
    }
  ],
  "related_searches": [
    {
      "query": "molecular biology",
      "link": "https://scholar.google.com/scholar?hl=en&as_sdt=0,38&qsp=1&q=molecular+biology&qst=ib"
    },
    {
      "query": "synthetic biology",
      "link": "https://scholar.google.com/scholar?hl=en&as_sdt=0,38&qsp=2&q=synthetic+biology&qst=ib"
    },
    {
      "query": "evolutionary biology",
      "link": "https://scholar.google.com/scholar?hl=en&as_sdt=0,38&qsp=3&q=evolutionary+biology&qst=ib"
    },
    {
      "query": "computational biology",
      "link": "https://scholar.google.com/scholar?hl=en&as_sdt=0,38&qsp=4&q=computational+biology&qst=ib"
    },
    {
      "query": "reproductive biology",
      "link": "https://scholar.google.com/scholar?hl=en&as_sdt=0,38&qsp=5&q=reproductive+biology&qst=ib"
    },
    {
      "query": "biochemistry and molecular biology",
      "link": "https://scholar.google.com/scholar?hl=en&as_sdt=0,38&qsp=6&q=biochemistry+and+molecular+biology&qst=ib"
    },
    {
      "query": "global change biology",
      "link": "https://scholar.google.com/scholar?hl=en&as_sdt=0,38&qsp=7&q=global+change+biology&qst=ib"
    },
    {
      "query": "plos biology",
      "link": "https://scholar.google.com/scholar?hl=en&as_sdt=0,38&qsp=8&q=plos+biology&qst=ib"
    }
  ],
  "pagination": {
    "current": 1,
    "next": "https://scholar.google.com/scholar?start=10&q=biology&hl=en&as_sdt=0,5",
    "other_pages": {
      "2": "https://scholar.google.com/scholar?start=10&q=biology&hl=en&as_sdt=0,5",
      "3": "https://scholar.google.com/scholar?start=20&q=biology&hl=en&as_sdt=0,5",
      "4": "https://scholar.google.com/scholar?start=30&q=biology&hl=en&as_sdt=0,5",
      "5": "https://scholar.google.com/scholar?start=40&q=biology&hl=en&as_sdt=0,5",
      "6": "https://scholar.google.com/scholar?start=50&q=biology&hl=en&as_sdt=0,5",
      "7": "https://scholar.google.com/scholar?start=60&q=biology&hl=en&as_sdt=0,5",
      "8": "https://scholar.google.com/scholar?start=70&q=biology&hl=en&as_sdt=0,5",
      "9": "https://scholar.google.com/scholar?start=80&q=biology&hl=en&as_sdt=0,5",
      "10": "https://scholar.google.com/scholar?start=90&q=biology&hl=en&as_sdt=0,5"
    }
  },
  "serpapi_pagination": {
    "current": 1,
    "other_pages": {
      "2": "https://serpapi.com/search.json?as_sdt=0%2C5&engine=google_scholar&hl=en&q=biology&start=10",
      "3": "https://serpapi.com/search.json?as_sdt=0%2C5&engine=google_scholar&hl=en&q=biology&start=20",
      "4": "https://serpapi.com/search.json?as_sdt=0%2C5&engine=google_scholar&hl=en&q=biology&start=30",
      "5": "https://serpapi.com/search.json?as_sdt=0%2C5&engine=google_scholar&hl=en&q=biology&start=40",
      "6": "https://serpapi.com/search.json?as_sdt=0%2C5&engine=google_scholar&hl=en&q=biology&start=50",
      "7": "https://serpapi.com/search.json?as_sdt=0%2C5&engine=google_scholar&hl=en&q=biology&start=60",
      "8": "https://serpapi.com/search.json?as_sdt=0%2C5&engine=google_scholar&hl=en&q=biology&start=70",
      "9": "https://serpapi.com/search.json?as_sdt=0%2C5&engine=google_scholar&hl=en&q=biology&start=80",
      "10": "https://serpapi.com/search.json?as_sdt=0%2C5&engine=google_scholar&hl=en&q=biology&start=90"
    },
    "next": "https://serpapi.com/search.json?as_sdt=0%2C5&engine=google_scholar&hl=en&q=biology&start=10",
    "next_link": "https://serpapi.com/search.json?as_sdt=0%2C5&engine=google_scholar&hl=en&q=biology&start=10"
  }
}
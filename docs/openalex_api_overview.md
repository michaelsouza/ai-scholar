# API Overview

The API is the primary way to get OpenAlex data. It's free and requires no authentication. The daily limit for API calls is 100,000 requests per user per day. For best performance, [add your email](https://docs.openalex.org/rate-limits-and-authentication#the-polite-pool) to all API requests, like `mailto=example@domain.com`.

## Learn more about the API

* [Get single entities](https://docs.openalex.org/how-to-use-the-api/get-single-entities)
* [Get lists of entities](https://docs.openalex.org/how-to-use-the-api/get-lists-of-entities) — Learn how to use [paging](https://docs.openalex.org/how-to-use-the-api/get-lists-of-entities/paging), [filtering](https://docs.openalex.org/how-to-use-the-api/get-lists-of-entities/filter-entity-lists), and [sorting](https://docs.openalex.org/how-to-use-the-api/get-lists-of-entities/sort-entity-lists)
* [Get groups of entities](https://docs.openalex.org/how-to-use-the-api/get-groups-of-entities) — Group and count entities in different ways
* [Rate limits and authentication](https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication) — Learn about joining the [polite pool](https://docs.openalex.org/rate-limits-and-authentication#the-polite-pool)
* [Tutorials ](https://docs.openalex.org/additional-help/tutorials)— Hands-on examples with code

## Client Libraries

There are several third-party libraries you can use to get data from OpenAlex:

* [openalexR](https://github.com/ropensci/openalexR) (R)
* [OpenAlex2Pajek](https://github.com/bavla/OpenAlex/tree/main/OpenAlex2Pajek) (R)
* [KtAlex](https://github.com/benedekh/KtAlex) (Kotlin)
* [PyAlex](https://github.com/J535D165/pyalex) (Python)
* [diophila](https://pypi.org/project/diophila/) (Python)
* [OpenAlexAPI](https://pypi.org/project/openalexapi/) (Python)

If you're looking for a visual interface, you can also check out the free [VOSviewer](https://www.vosviewer.com/), which lets you make network visualizations based on OpenAlex data:

![](https://334408415-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FpHVuV3Ib5KXeBKft4Kcl%2Fuploads%2Fgit-blob-3ad4312517a39e84dddc3c84c115089ac89fa283%2FScreenshot%20by%20Dropbox%20Capture.png?alt=media)
# National Autonomous University of Mexico at Libray of Congress
This project pretend to get all resources available from National Autonomous
University of Mexico on the [Library of Congress](https://catalog.loc.gov/)
web page. This program use the [SRU](https://www.loc.gov/standards/sru/)
API of the library and ```python3.6```

## Basic variants for searching
1. Universidad Nacional Autómoma de México
2. UNAM
3. U.N.A.M
4. Univ. Nac. Aut. Mex.
5. National Autonomous University of Mexico
6. Univ. Nac. Auton. Mex.
7. Univ. Nac. Auton. de México

## Standar query
```http://lx2.loc.gov:210/lcdb?version=<VESION>&operation=searchRetrieve&query="<VARIANT>" AND dc.date=<YEAR>&startRecord=<START_INDEX>&maximumRecords=<MAXIMUM_RECORDS>&recordSchema=dc```

#### Where:
* VERSION: The version of SRU protocol.
* VARIANT: A variant to search the unam at the LC
* START_INDEX: The index of the pages of records (by default 1)
* MAXIMUM_RECORDS: Maximum records by request
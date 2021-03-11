# Geo N:G (QRP) application

The Geo:N:G application is a tool designed to assist subsurface prediction of net sand for modelling purposes related to oil and gas exploration and production and also carbon sequestration. The output of the application is a single number that represents a single geological scenario that forms one point on the uncertainty distribution for the Net to Gross (NG) parameter. From local data and an understanding of local uncertainty, several data-led and/or conceptual scenarios will typically be needed to define the full range. The Geo:N:G app is designed to enable flexible quantification of these scenarios using a distilled set of sedimentological/stratigraphic concepts and building blocks that are considered to have the largest impact on subsurface prediction. This is naturally a simplification of the broader scientific theory but the key is to enable application of the science toward a quantitative end point and use by non-experts.

The application is underpinned by a geologically categorised database constructed by domain experts (sedimentologists) using standard subsurface datasets; wireline and core wellbore data, calibrated to seismic where possible. The inputs are not raw data but interpretation; petrophysical (CPI) and sedimentological, and the predictive value comes from their integration. The database is constructed manually using wellbores from many different basins and stratigraphic ages. The underpinning assumption is that there is repeatability of the sedimentological building blocks in terms of process and deposit thus predictive potential from combining many examples of each from different contexts. For a given reservoir interval in a given wellbore, the NG is calculated not for top and base, but for the architectural elements (generally 10m thick or less) i.e., geobody building blocks that are the components of all clastic reservoirs. This means that many datapoints can be gained from a single reservoir. A hierarchy is also applied to the data comprising stacks of architectural elements that represent different stratigraphic scales of cyclicity. These are useful to give indications of 'recipes' of elements for different scenarios and expected NG outcomes (i.e., quality brackets) to guide users. Careful construction of quality data enables a statistical analysis of the database to demonstrate how well first principle qualitative expectations are represented quantitatively forming a QC of the numbers engine that powers the Geo:N:G application

## Technical details

One way to run this application is using docker-compose. Simply run `docker-compose up --build` with variables set as described below.

### Security

The app and api is protected by oauth2.

These variables are required for security:
```
AUTHORITY=<URL to OAuth authority>
CLIENT_ID=<OAuth client ID>
CLIENT_SECRET=<OAuth client secret>
AUDIENCE=<OAuth audience>
```

### Data files

All files must be stored in an azure blob container.

These variables are required for storage:
```
STORAGE_URL=<URL to Azure blob>
CONTAINER=<Name of blob storage container>
FOLDER_NAME=<Folder inside the blob storage container>
```

3 files are required per module (deep and shallow):
```
complexes.json
elements.json
systems.json
```

[examples/data/deep](examples/data/deep) shows an example structure for these files. Inspect the code to see details of required directory structure.

TODO: Create proper example files used in integration tests that can be used to run the application.

### Logging

Each container logs to stdout. Set the variable `LOG_LEVEL` if required.

If the variable `APPLICATIONINSIGHTS_INSTRUMENTATION_KEY` is valid, logs are also forwarded to azure applications insight.

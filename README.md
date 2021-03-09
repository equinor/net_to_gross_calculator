# Geo N:G (QRP) application

TODO: a general overview of what geong is

## Technical details

One way to run this application is using docker-compose. Simply run `docker-compose up --build` with variables set as described below.

### Security

The app and api is protected by oauth2.

These variables are required for security:
- AUTHORITY=<URL to OAuth authority>
- CLIENT_ID=<OAuth client ID>
- CLIENT_SECRET=<OAuth client secret>
- AUDIENCE=<OAuth audience>

### Data files

All files must be stored in an azure blob container.

These variables are required for storage:
- STORAGE_URL=<URL to Azure blob>
- CONTAINER=<Name of blob storage container>
- FOLDER_NAME=<Folder inside the blob storage container>

3 files are required per module (deep and shallow):
- complexes.json
- elements.json
- systems.json

[examples/data/deep](examples/data/deep) shows an example structure for these files. Inspect the code to see details of required directory structure.

TODO: Create proper example files used in integration tests that can be used to run the application.

### Logging

Each container logs to stdout. Set the variable `LOG_LEVEL` if required.

If the variable `APPLICATIONINSIGHTS_INSTRUMENTATION_KEY` is valid, logs are also forwarded to azure applications insight.

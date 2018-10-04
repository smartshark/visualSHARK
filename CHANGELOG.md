0.1.2 (in progress)
- Grid does now switch to first page if entries to display is changed
- Grid does now show if the data is not yet loaded (translucency for now)
- added first line of commit message to commit list views
- added hunk api endpoint
- added lines to code entity states endpoint
- added issue link candidates generation based on ITS and commit message
- added custom test runner for execution with mongomock (disregarding the MySQL Part for now)
- upgraded django to 2.1
- optimized commit graph creation
- included backend for new ontdekbaan time based paths view
- Update CommitViewSet so that it does not fetch code_entity_states (because that is BIG)
- fix bug for CodeEntityState Grid that displays hundreds of empty lines if interface is in the grid
- now only request single commits with vcs_system_id not just revision_hash
- update Django to 2.1.2
[ ] fix warning for loading attribute of grid
[ ] allow creation of commitgraph from webfrontend, handover to peon worker process, get update when work is finished via websocket

0.1.1
- Successful jobs get acknowledged automatically
- added Branch API Endpoint
- added Events to Issue Endpoint
- added Frontend Grid for Issue Events
40_CervicalScreeningAnalysis

Deploy app:
1. Kill existing version:
ps aux | grep python
kill -9 p r o c e s s id

2. Start app:
The application should be started from outside the app folder (!) with below command:
nohup bokeh serve --show CervicalScreeningAnalysis --port=5006 --allow-websocket-origin=52.157.204.106:5006

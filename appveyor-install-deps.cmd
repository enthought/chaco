"%sdkverpath%" -q -version:"%sdkver%"
call setenv /x64

pip install --cache-dir c:/temp numpy
pip install --cache-dir c:/temp distribute
pip install --cache-dir c:/temp enable
